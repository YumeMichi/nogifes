<?php
require './utils.php';

$key = 'p5Lj2Z3RHaSWu7iUEgz9tWnt';
$iv = $_SERVER['HTTP_NGZ_IV'];
header('ngz_iv: ' . $iv);

if (!isset($iv) || $iv == '') {
    header('HTTP/1.1 500 Internal Server Error');
}

$data = json_decode(file_get_contents('response/get_user_all.json'), true);
$unitData = $data['unit_data'];

$userUnitId = 10000000;
$movieList = [];
$allData = json_decode(file_get_contents('masterdata/UnitMaster.json'), true);
foreach ($allData as $kk => $value) {
    $userUnitId++;
    $unitData[] = [
        'unit_structure' => [
            'user_unit_id' => $userUnitId,
            'unit_id' => $value['unit_id'],
            'rarity' => $value['rarity'],
            'attribute' => $value['attribute'],
            'exceed_count' => 5,
            'level' => GetUnitLevel($value['rarity']),
            'exp' => 0,
            'hp' => $value['max_hp'],
            'gp' => $value['max_gp'],
            'skill_level' => 1,
            'favorite' => 1,
            'protect' => 1,
            'supporter_data' => [],
            'image_type' => 0,
            'image_id' => 0,
        ],
    ];

    if ($value['bonus_movie_type'] != 0) {
        $movieList[] = [
            'bonus_movie_type' => $value['bonus_movie_type'],
            'bonus_movie_id' => $value['bonus_movie_id']
        ];
    }
}

$data['unit_data'] = $unitData;
$newData = json_encode($data);
echo RijndaelEncrypt($key, $iv, $newData);
