<?php
require './utils.php';

$data = [
    'mstlist_version' => GetMasterdataVersion(),
    'connect_key' => GetConnectKey(),
    'home_photo_data' => [],
    'success' => true,
];

SendEncryptedResponse('InitializeResponse', $data);
