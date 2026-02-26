<?php
require './utils.php';

$data = [
    'mstlist_version' => GetMasterdataVersion(),
    'connect_key' => GetConnectKey(),
    'user_id' => 20302870,
    'user_token' => 'mHK0ll2Q9nDse5yK',
    'friend_id' => '855096050',
    'restriction_end_date' => 1757261798,
    'success' => true,
];

SendEncryptedResponse('DoInheritResponse', $data);
