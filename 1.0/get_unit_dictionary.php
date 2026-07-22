<?php
require './utils.php';

$unitData = [];

$unitMaster = LoadJsonFile('masterdata/UnitMaster.json');
foreach ($unitMaster as $unit) {
    $unitData[] = [
        'unit_id' => $unit['unit_id'],
    ];
}

$data = [
    'mstlist_version' => GetMasterdataVersion(),
    'connect_key' => GetConnectKey(),
    'unit_data' => $unitData,
    'success' => true,
];

SendEncryptedResponse('GetUnitDictionaryResponse', $data);
