<?php

function UpdateAllMovie()
{
    $bonusMovieData = [];
    $unitMovieData = [];
    $highQualityMovieData = [];

    // get_all_movie
    $response = json_decode(file_get_contents("response/get_all_movie.json"), true);

    // unit_list
    $unitList = json_decode(file_get_contents("masterdata/UnitMaster.json"), true);
    foreach ($unitList as $unit) {
        // bonus_movie_data
        if ($unit['bonus_movie_id'] != 0) {
            $bonusMovieData[] = [
                'bonus_movie_type' => $unit['bonus_movie_type'],
                'bonus_movie_id' => $unit['bonus_movie_id'],
            ];
        }
    }

    // high_quality_movie_data (FocusMovieMaster)
    $focusMovieData = json_decode(file_get_contents("masterdata/FocusMovieMaster.json"), true);
    foreach ($focusMovieData as $movie) {
        if ($movie['high_quality'] == 1) {
            $highQualityMovieData[] = [
                'type' => 2,
                'id' => $movie['focus_movie_id']
            ];
        }
    }

    // high_quality_movie_data (OtherMovieMaster)
    $otherMovieData = json_decode(file_get_contents("masterdata/OtherMovieMaster.json"), true);
    foreach ($otherMovieData as $movie) {
        if ($movie['high_quality'] == 1) {
            $highQualityMovieData[] = [
                'type' => 3,
                'id' => $movie['other_movie_id']
            ];
        }
    }

    // high_quality_movie_data (LiveMaster)
    $liveData = json_decode(file_get_contents("masterdata/LiveMaster.json"), true);
    foreach ($liveData as $movie) {
        if ($movie['high_quality'] == 1) {
            $highQualityMovieData[] = [
                'type' => 1,
                'id' => $movie['live_id']
            ];
        }
    }

    // get_all_movie
    $response['bonus_movie_data'] = $bonusMovieData;
    $response['high_quality_movie_data'] = $highQualityMovieData;
    file_put_contents("response/get_all_movie.json", json_encode($response));
}

function UpdateAllLive()
{
    $liveList = [];

    // get_live_lite
    $response = json_decode(file_get_contents("response/get_live_lite.json"), true);

    // live_data
    $liveData = json_decode(file_get_contents("masterdata/LiveMaster.json"), true);
    foreach ($liveData as $live) {
        if ($live['unconditional'] == '1') {
            continue;
        }
        $liveList[] = [
            'live_id' => $live['live_id'],
        ];
    }

    // get_live_lite
    $response['live_data'] = $liveList;
    file_put_contents("response/get_live_lite.json", json_encode($response));
}

UpdateAllMovie();
UpdateAllLive();
