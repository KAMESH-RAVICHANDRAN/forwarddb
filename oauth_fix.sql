<?php
// Queue SSL cert jobs for site domains
// Run: docker exec appwrite php /tmp/queue_certs.php

$redis = new Redis();
$redis->connect('appwrite-redis', 6379);

$namespace = 'utopia-queue';
$queue = 'v1-certificates';

$domains = [
    [
        '_uid' => '69a8d9c92e8dec5f508e',
        'domain' => 'magic-portfolio.sites.forwarddb.ajstudioz.co.in',
        'projectId' => '69a8d820002b9906bb9a',
        'projectInternalId' => '1',
        'type' => 'deployment',
        'status' => 'verified',
    ],
    [
        '_uid' => '69a8d9c98a5b456bad20',
        'domain' => '69a8d9c98a5af4b97a4b.sites.forwarddb.ajstudioz.co.in',
        'projectId' => '69a8d820002b9906bb9a',
        'projectInternalId' => '1',
        'type' => 'deployment',
        'status' => 'verified',
    ],
];

foreach ($domains as $domainData) {
    $pid = uniqid('', true);
    $payload = [
        'pid' => $pid,
        'queue' => $queue,
        'timestamp' => time(),
        'payload' => [
            'project' => ['$id' => '69a8d820002b9906bb9a', '$internalId' => '1'],
            'domain' => array_merge(['$id' => $domainData['_uid']], $domainData),
            'skipRenewCheck' => true,
            'validationDomain' => null,
        ],
    ];
    $result = $redis->lPush("{$namespace}.queue.{$queue}", json_encode($payload));
    echo "Queued cert for {$domainData['domain']}: " . ($result ? "OK" : "FAILED") . "\n";
}


