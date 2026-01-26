<?php
ini_set('memory_limit', '1024M');

require './1.0/utils.php';

$applicationVersion = 21401;
$storeID = 2; // Android

$commonIv = GenerateIV();
$commonHeader = GenerateCommonHeader($commonIv);

$initializeBody = [
    'user_token' => 'EZJbBbC5yaG7uRso',
    'locale' => 'ChineseSimplified',
    'model' => 'Xiaomi 24031PN0DC',
    'device_name' => '2206123SC',
    'os_name' => 'Android',
    'os_version' => '12',
    'device_token' => '',
    'device_id' => 'c068d7e0-bcdf-4ba7-8cb0-94d8da9500881766628714',
    'application_version' => $applicationVersion,
    'store_id' => $storeID,
    'user_id' => 20426802
];
$encryptedInitializeBody = RijndaelEncrypt("8ihNytHPB3WawDsULyDKwh5T", $commonIv, json_encode($initializeBody));

$ret = Post('https://v2api.nogifes.jp/1.0/initialize.php', $commonHeader, $encryptedInitializeBody, true);
$ret = json_decode(RijndaelDecrypt("8ihNytHPB3WawDsULyDKwh5T", $ret['ngz_iv'], $ret['body']), true);

if (!$ret['success']) {
    echo $ret['error_data']['userMessage'] . PHP_EOL;
    die;
}

$masterDataVersion = 0;
if (file_exists("mstlist_version.txt")) {
    $masterDataVersion = (int)file_get_contents("mstlist_version.txt");
}

if ($masterDataVersion != $ret['mstlist_version']) {
    echo "New master data version: " . $ret['mstlist_version'] . ' found!' . PHP_EOL;
    file_put_contents("mstlist_version.txt", $ret['mstlist_version']);
} else {
    echo "Current master data version: " . $masterDataVersion . PHP_EOL;
    die;
}

if (!file_exists('temp')) {
    mkdir('temp', 0755, true);
}

$mstList = json_decode(file_get_contents("mstlist.json"), true);
foreach ($mstList['mstlist'] as $mst) {
    $fileName = SnakeToPascal($mst['name']) . 'Master';
    $filePath = "temp/" . $fileName;

    if (file_exists($filePath)) {
        $fileHash = hash_file('sha256', $filePath);
        if ($fileHash == $mst['hash']) {
            echo $fileName . ' is up to date.' . PHP_EOL;
            continue;
        }
    }

    $fileURL = 'https://v2static.nogifes.jp/resource/mst/' . $mst['file'] . '?ver=' . $mst['version'];
    $fileContent = '';
    echo 'Downloading ' . $fileURL . PHP_EOL;
    for ($i = 0; $i < 3; $i++) {
        $fileContent = Get($fileURL, false);
        if ($fileContent) {
            file_put_contents("temp/" . $fileName, $fileContent);
            break;
        } else {
            echo sprintf("[%d/3] Failed to download %s\n", $i + 1, $mst['name']);
            if ($i == 2) {
                die;
            }
        }
    }

    $keyMap = json_decode(file_get_contents("./1.0/rijndael_keys.json"), true);
    $fileKey = $keyMap[$fileName];
    $fileDecrypted = RijndaelDecryptECB($fileKey, $fileContent);
    $fileEncoded = json_encode(
        json_decode($fileDecrypted, true),
        JSON_UNESCAPED_SLASHES | JSON_UNESCAPED_UNICODE | JSON_PRETTY_PRINT
    );
    file_put_contents("1.0/masterdata/" . SnakeToPascal($mst['name']) . 'Master.json', $fileEncoded . PHP_EOL);
}
