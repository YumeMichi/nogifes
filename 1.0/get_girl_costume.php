<?php
require './utils.php';

$data = [
    'mstlist_version' => GetMasterdataVersion(),
    'connect_key' => GetConnectKey(),
    'costume_data' => [],
    'success' => true,
];

SendEncryptedResponse('GetGirlCostumeResponse', $data);
