<?php
require './utils.php';

$data = [
    'mstlist_version' => GetMasterdataVersion(),
    'connect_key' => GetConnectKey(),
    'message_num' => 0,
    'success' => true,
];

SendEncryptedResponse('CountMessageResponse', $data);
