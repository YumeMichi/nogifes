<?php
require './utils.php';

$data = [
    'mstlist_version' => GetMasterdataVersion(),
    'connect_key' => GetConnectKey(),
    'general_mission_num' => 0,
    'daily_mission_num' => 1,
    'weekly_mission_num' => 0,
    'special_mission_num' => 0,
    'beginner_mission_num' => 0,
    'presentbox_num' => 9,
    'beginner_mission_all_clear' => false,
    'success' => true,
];

SendEncryptedResponse('HomeResponse', $data);
