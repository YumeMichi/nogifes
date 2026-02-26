<?php
require './utils.php';

$data = [
    'mstlist_version' => GetMasterdataVersion(),
    'connect_key' => GetConnectKey(),
    'campaign_payment' => true,
    'beginner' => true,
    'success' => true,
];

SendEncryptedResponse('GetGnaviStatusResponse', $data);
