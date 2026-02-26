<?php
require './utils.php';

$data = LoadJsonFile('response/get_user_all.json');
$unitData = $data['unit_data'] ?? [];

$userUnitId = 10000000;
$allData = LoadJsonFile('masterdata/UnitMaster.json');
foreach ($allData as $value) {
    $userUnitId++;
    $unitData[] = [
        'unit_structure' => [
            'user_unit_id' => $userUnitId,
            'unit_id' => $value['unit_id'] ?? 0,
            'rarity' => $value['rarity'] ?? 0,
            'attribute' => $value['attribute'] ?? 0,
            'exceed_count' => 5,
            'level' => GetUnitLevel($value['rarity'] ?? 0),
            'exp' => 0,
            'hp' => $value['max_hp'] ?? 0,
            'gp' => $value['max_gp'] ?? 0,
            'skill_level' => 1,
            'favorite' => 1,
            'protect' => 1,
            'supporter_data' => [],
            'image_type' => 0,
            'image_id' => 0,
        ],
    ];
}

$data['unit_data'] = $unitData;

SendEncryptedResponse('GetUserAllResponse', $data);
