<?php
// Fix screenshot bucket permissions - make publicly readable
// Appwrite stores real ACLs in the _perms tables, not just the _permissions JSON column

$pdo = new PDO('mysql:host=appwrite-mariadb;dbname=appwrite', 'root', 'rootsecretpassword');

// 1. Update _console_bucket_2_perms: change team:xxx -> any for all read entries
$stmt = $pdo->prepare("UPDATE _console_bucket_2_perms SET _permission='any' WHERE _type='read'");
$stmt->execute();
echo "Screenshot file perms updated (read->any): " . $stmt->rowCount() . " rows\n";

// 2. Update _console_buckets_perms for the screenshots bucket row
$stmt2 = $pdo->prepare("UPDATE _console_buckets_perms SET _permission='any' WHERE _type='read' AND _document='screenshots'");
$stmt2->execute();
echo "Bucket perms updated: " . $stmt2->rowCount() . " rows\n";

// If no bucket perms row exists, insert one
if ($stmt2->rowCount() === 0) {
    $pdo->prepare("INSERT INTO _console_buckets_perms (_type, _permission, _document) VALUES ('read','any','screenshots')")->execute();
    echo "Bucket perm inserted\n";
}

// 3. Disable fileSecurity on bucket
$pdo->exec("UPDATE _console_buckets SET fileSecurity=0 WHERE _uid='screenshots'");
echo "fileSecurity disabled\n";

// 4. Verify
$rows = $pdo->query("SELECT _type, _permission FROM _console_bucket_2_perms LIMIT 6")->fetchAll(PDO::FETCH_ASSOC);
foreach ($rows as $r) echo "  file perm: " . $r['_type'] . " => " . $r['_permission'] . "\n";

echo "Done!\n";
