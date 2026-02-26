<?php
require './utils.php';

$bonusMovieData = [];
$highQualityMovieData = [];

// bonus_movie_data (UnitMaster)
$unitList = LoadJsonFile('masterdata/UnitMaster.json');
foreach ($unitList as $unit) {
    if (($unit['bonus_movie_id'] ?? 0) != 0) {
        $bonusMovieData[] = [
            'bonus_movie_type' => $unit['bonus_movie_type'] ?? 0,
            'bonus_movie_id' => $unit['bonus_movie_id'] ?? 0,
        ];
    }
}

// high_quality_movie_data (FocusMovieMaster)
$focusMovieData = LoadJsonFile('masterdata/FocusMovieMaster.json');
foreach ($focusMovieData as $movie) {
    if (($movie['high_quality'] ?? 0) == 1) {
        $highQualityMovieData[] = [
            'type' => 2,
            'id' => $movie['focus_movie_id'] ?? 0,
        ];
    }
}

// high_quality_movie_data (OtherMovieMaster)
$otherMovieData = LoadJsonFile('masterdata/OtherMovieMaster.json');
foreach ($otherMovieData as $movie) {
    if (($movie['high_quality'] ?? 0) == 1) {
        $highQualityMovieData[] = [
            'type' => 3,
            'id' => $movie['other_movie_id'] ?? 0,
        ];
    }
}

// high_quality_movie_data (LiveMaster)
$liveData = LoadJsonFile('masterdata/LiveMaster.json');
foreach ($liveData as $movie) {
    if (($movie['high_quality'] ?? 0) == 1) {
        $highQualityMovieData[] = [
            'type' => 1,
            'id' => $movie['live_id'] ?? 0,
        ];
    }
}

$data = [
    'mstlist_version' => GetMasterdataVersion(),
    'connect_key' => GetConnectKey(),
    'bonus_movie_data' => $bonusMovieData,
    'unit_movie_data' => [],
    'high_quality_movie_data' => $highQualityMovieData,
    'success' => true,
];

SendEncryptedResponse('GetAllMovieResponse', $data);
