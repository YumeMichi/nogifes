<?php
require './utils.php';

$data = [
    'mstlist_version' => GetMasterdataVersion(),
    'connect_key' => GetConnectKey(),
    'total_shine_point' => 0,
    'shine_point_data' => [],
    'success' => true,
];

SendEncryptedResponse('GetShinePointResponse', $data);
