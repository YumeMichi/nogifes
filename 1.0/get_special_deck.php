<?php
require './utils.php';

$data = [
    'mstlist_version' => GetMasterdataVersion(),
    'connect_key' => GetConnectKey(),
    'main_member_data' => [],
    'sub_member_data' => [],
    'success' => true,
];

SendEncryptedResponse('GetSpecialDeckResponse', $data);
