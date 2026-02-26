<?php
require './utils.php';

$data = [
    'mstlist_version' => GetMasterdataVersion(),
    'connect_key' => GetConnectKey(),
    'home_bg_data' => [],
    'home_costume_data' => [],
    'home_photo_data' => [],
    'success' => true,
];

SendEncryptedResponse('GetHomeItemResponse', $data);
