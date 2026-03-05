<?php
// Queue SSL cert for new deployment domain
$redis = new Redis();
$redis->connect('appwrite-redis', 6379);

$domains = [
    'simple-html-web.sites.forwarddb.ajstudioz.co.in',
    'branch-main-4dc2d0a.sites.forwarddb.ajstudioz.co.in',
    'commit-0f13ded78880d09d.sites.forwarddb.ajstudioz.co.in',
    '69a967a7994b57d722af.sites.forwarddb.ajstudioz.co.in',
];

foreach ($domains as $domain) {
    $job = json_encode([
        'pid' => uniqid(),
        'queue' => 'utopia-queue.queue.v1-certificates',
        'timestamp' => time(),
        'payload' => [
            'project' => ['$id' => 'console', '$internalId' => '1'],
            'domain' => [
                'domain' => $domain,
                'domainType' => 'deployment',
            ],
            'skipRenewCheck' => false,
            'validationDomain' => $domain,
        ]
    ]);
    $result = $redis->lPush('utopia-queue.queue.v1-certificates', $job);
    $domainStr = $domain;
    echo "Queued cert for {$domainStr}: " . ($result ? "OK" : "FAILED") . "\n";
}
