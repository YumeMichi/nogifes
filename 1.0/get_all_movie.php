<?php
require './utils.php';

$bonusMovieData = [];
$highQualityMovieData = [];
$unitMovieData = [];

// bonus_movie_data (UnitMaster)
$unitMaster = LoadJsonFile('masterdata/UnitMaster.json');
foreach ($unitMaster as $unit) {
    if (($unit['bonus_movie_id'] ?? 0) != 0) {
        $bonusMovieData[] = [
            'bonus_movie_type' => $unit['bonus_movie_type'] ?? 0,
            'bonus_movie_id' => $unit['bonus_movie_id'] ?? 0,
        ];
    }
}

// high_quality_movie_data (FocusMovieMaster)
$focusMovieMaster = LoadJsonFile('masterdata/FocusMovieMaster.json');
foreach ($focusMovieMaster as $movie) {
    if (($movie['high_quality'] ?? 0) == 1) {
        $highQualityMovieData[] = [
            'type' => 2,
            'id' => $movie['focus_movie_id'] ?? 0,
        ];
    }
}

// high_quality_movie_data (OtherMovieMaster)
$otherMovieMaster = LoadJsonFile('masterdata/OtherMovieMaster.json');
foreach ($otherMovieMaster as $movie) {
    if (($movie['high_quality'] ?? 0) == 1) {
        $highQualityMovieData[] = [
            'type' => 3,
            'id' => $movie['other_movie_id'] ?? 0,
        ];
    }
}

// high_quality_movie_data (LiveMaster)
$liveMaster = LoadJsonFile('masterdata/LiveMaster.json');
foreach ($liveMaster as $movie) {
    if (($movie['high_quality'] ?? 0) == 1) {
        $highQualityMovieData[] = [
            'type' => 1,
            'id' => $movie['live_id'] ?? 0,
        ];
    }
}

// unit_movie_data (UnitMovieMaster)
$unitMovieMaster = LoadJsonFile('masterdata/UnitMovieMaster.json');
foreach ($unitMovieMaster as $movie) {
    $unitMovieData[] = [
        'unit_movie_id' => $movie['unit_movie_id'] ?? 0,
    ];
}

$data = [
    'mstlist_version' => GetMasterdataVersion(),
    'connect_key' => GetConnectKey(),
    'bonus_movie_data' => $bonusMovieData,
    'unit_movie_data' => $unitMovieData,
    'high_quality_movie_data' => $highQualityMovieData,
    'success' => true,
];

SendEncryptedResponse('GetAllMovieResponse', $data);
