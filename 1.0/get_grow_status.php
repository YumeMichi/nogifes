<?php
require './utils.php';

$data = [
    'mstlist_version' => GetMasterdataVersion(),
    'connect_key' => GetConnectKey(),
    'girl_data' => [],
    'success' => true,
];

SendEncryptedResponse('GetGrowStatusResponse', $data);
