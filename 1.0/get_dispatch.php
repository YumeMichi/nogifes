<?php
require './utils.php';

$data = [
    'mstlist_version' => GetMasterdataVersion(),
    'connect_key' => GetConnectKey(),
    'gold_update_count' => 0,
    'dispatch_data' => [],
    'lots_date' => 1758170227,
    'success' => true,
];

SendEncryptedResponse('GetDispatchResponse', $data);
