<?php
require './utils.php';

$data = [
    'mstlist_version' => GetMasterdataVersion(),
    'connect_key' => GetConnectKey(),
    'live_data' => [],
    'favorite_data' => [],
    'success' => true,
];

SendEncryptedResponse('GetLiveResponse', $data);
