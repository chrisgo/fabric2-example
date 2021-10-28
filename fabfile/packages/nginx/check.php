<?php

/**
 * Check script to make sure system is functioning properly
 * Suitable to use for Amazon (or other) systems that do a string
 * check.  The check string that needs to be found is
 *
 * "healthy" : "all"
 *
 * 1/26/21 CG: Note: Remove space around colon when pasting into AWS string check
 * Can't make it exact because if this renders as a TEXT file, it will still PASS
 *
 * There is an entire JSON array for more sophisticated string
 * matches
 *
 * TODO: Self-healing code by trying to fix the broken pieces of the system
 *
 * (1) S3FS => done (needs sudo configuration to allow PHP to run mount/umount)
 * (2) Broken worker (not running mount point)
 * (3) Can't connect to resque server (queue)
 * (4) Can't connect to redis server (cache & sessions)
 *
 * This needs to be a very basic PHP script (no framework dependencies)
 * as this will just be called via a plan HTTP call
 *
 * For Amazon Healthcheck, needs to be on the IP address + port 80
 * Path is: check.php
 *
 */

$checks = [
    's3fs' => [
        '/mnt/s3fs' => false,
        //'/mnt/s3fs-docs' => false,
        //'/mnt/s3fs-archive' => false,
    ],
    'worker' => [
    ],
];

// Loop through mounts
// and try to fix any broken ones
if (!empty($checks['s3fs']) AND count($checks['s3fs']) > 0) {
    foreach ($checks['s3fs'] as $mount => $status) {
        if (!file_exists($mount . '/checkfile.txt')) {
            // TODO: sudo unmount and mount
            exec('sudo umount ' . $mount, $output, $status);
            exec('sudo mount ' . $mount, $output, $status);
        }
        if (file_exists($mount . '/checkfile.txt')) {
            $checks['s3fs'][$mount] = true;
        }
    }
}

// Final loop for checks
$healthy = true;

if (!empty($checks) AND count($checks) > 0) {
    foreach ($checks as $module => $submodule) {
       //echo $module . "<br>";
       if (!empty($submodule) AND count($submodule) > 0 ) {
          foreach ($submodule as $name => $status) {
             //echo "- " . $name . " => " . $status . "<br/>";
             if (empty($status) OR !$status) {
                 $healthy = false;
                 break;
             }
          }
       }
    }
}

// Set the string
if ($healthy) {
    $checks =  array_merge(['healthy' => 'all'], $checks);
} else {
    $checks =  array_merge(['healthy' => false], $checks);
}

echo json_encode($checks);
