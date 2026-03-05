<?php
/**
 * Appwrite Auto-Cert Watcher
 * Watches for new site/deployment rules without SSL certs and queues them automatically.
 * Runs as a persistent background service — Vercel-like instant HTTPS.
 */

$dbHost = getenv('DB_HOST') ?: 'appwrite-mariadb';
$dbUser = getenv('DB_USER') ?: 'root';
$dbPass = getenv('DB_PASS') ?: 'rootsecretpassword';
$dbName = getenv('DB_NAME') ?: 'appwrite';
$redisHost = getenv('REDIS_HOST') ?: 'appwrite-redis';
$redisPort = (int)(getenv('REDIS_PORT') ?: 6379);
$pollInterval = (int)(getenv('POLL_INTERVAL') ?: 10); // seconds

$QUEUE = 'utopia-queue.queue.v1-certificates';
$queued = []; // track already-queued domains in this session
$cycleCount = 0;

function log_msg(string $msg): void {
    echo '[' . date('Y-m-d H:i:s') . '] ' . $msg . PHP_EOL;
}

function getDB(string $host, string $user, string $pass, string $db): PDO {
    $dsn = "mysql:host={$host};dbname={$db};charset=utf8mb4";
    $pdo = new PDO($dsn, $user, $pass, [
        PDO::ATTR_ERRMODE            => PDO::ERRMODE_EXCEPTION,
        PDO::ATTR_DEFAULT_FETCH_MODE => PDO::FETCH_ASSOC,
        PDO::ATTR_TIMEOUT            => 5,
    ]);
    return $pdo;
}

function getRedis(string $host, int $port): Redis {
    $redis = new Redis();
    $redis->connect($host, $port, 5);
    return $redis;
}

function queueCert(Redis $redis, string $queue, string $domain, string $domainType, array $project): bool {
    $job = json_encode([
        'pid'       => uniqid('autocert_', true),
        'queue'     => $queue,
        'timestamp' => time(),
        'payload'   => [
            'project'         => $project,
            'domain'          => [
                'domain'     => $domain,
                'domainType' => $domainType,
            ],
            'skipRenewCheck'    => false,
            'validationDomain'  => $domain,
        ],
    ]);
    return (bool)$redis->lPush($queue, $job);
}

log_msg('Auto-cert watcher started. Poll interval: ' . $pollInterval . 's');

$cycleCount = 0;
while (true) {
    $cycleCount++;
    try {
        $pdo   = getDB($dbHost, $dbUser, $dbPass, $dbName);
        $redis = getRedis($redisHost, $redisPort);

        // Find ALL tables that have rules (console + per-project)
        $tables = [];
        $stmt = $pdo->query("SHOW TABLES");
        foreach ($stmt->fetchAll(PDO::FETCH_COLUMN) as $t) {
            if (str_ends_with($t, '_rules') && !str_ends_with($t, '_rules_perms')) {
                $tables[] = $t;
            }
        }

        $found = 0;
        foreach ($tables as $table) {
            $rows = $pdo->query(
                "SELECT _uid, domain, type, projectInternalId, projectId
                 FROM `{$table}`
                 WHERE (certificateId IS NULL OR certificateId = '')
                   AND domain != ''
                 LIMIT 50"
            )->fetchAll();

            foreach ($rows as $row) {
                $domain = $row['domain'];

                // Skip main Appwrite internal domains
                if (str_ends_with($domain, '.appwrite.io') || $domain === 'localhost') {
                    continue;
                }

                // Build project reference
                $projectId         = $row['projectId'] ?? 'console';
                $projectInternalId = $row['projectInternalId'] ?? '1';

                // Skip if already queued this session
                if (isset($queued[$domain])) {
                    continue;
                }

                $domainType = $row['type'] ?? 'deployment';
                $project    = ['$id' => $projectId, '$internalId' => $projectInternalId];

                if (queueCert($redis, $QUEUE, $domain, $domainType, $project)) {
                    $queued[$domain] = time();
                    log_msg("✓ Queued cert for: {$domain} (type={$domainType}, project={$projectId})");
                    $found++;
                } else {
                    log_msg("✗ Failed to queue cert for: {$domain}");
                }
            }
        }

        // Heartbeat every 6 cycles (~60 seconds)
        if ($cycleCount % 6 === 1) {
            log_msg("♥ Watching " . count($tables) . " rule tables | " . count($queued) . " queued this session | All certs OK");
        }

        // Expire session cache after 10 minutes
        $now = time();
        foreach ($queued as $d => $ts) {
            if ($now - $ts > 600) {
                unset($queued[$d]);
            }
        }

        unset($pdo, $redis);
    } catch (Throwable $e) {
        log_msg('ERROR: ' . $e->getMessage());
    }

    sleep($pollInterval);
}
