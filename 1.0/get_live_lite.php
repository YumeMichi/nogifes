<?php
require './utils.php';

$live_data = [];
$live_master = LoadJsonFile('masterdata/LiveMaster.json');
foreach ($live_master as $live) {
    if (($live['unconditional'] ?? '') === '1') {
        continue;
    }
    $live_data[] = [
        'live_id' => $live['live_id'] ?? 0,
    ];
}

$data = [
    'mstlist_version' => GetMasterdataVersion(),
    'connect_key' => GetConnectKey(),
    'live_data' => $live_data,
    'success' => true,
];

SendEncryptedResponse('GetLiveLiteResponse', $data);
