<?php
require './utils.php';

$data = [
    'mstlist_version' => GetMasterdataVersion(),
    'connect_key' => GetConnectKey(),
    'event_item_data' => [],
    'success' => true,
];

SendEncryptedResponse('GetEventItemStatusResponse', $data);
