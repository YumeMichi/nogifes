<?php
require './utils.php';

$data = [
    'mstlist_version' => GetMasterdataVersion(),
    'connect_key' => GetConnectKey(),
    'trophy_id' => 0,
    'success' => true,
];

SendEncryptedResponse('GetTrophyResponse', $data);
