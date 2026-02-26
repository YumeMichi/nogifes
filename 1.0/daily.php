<?php
require './utils.php';

$data = [
    'mstlist_version' => GetMasterdataVersion(),
    'connect_key' => GetConnectKey(),
    'login_bonus' => [],
    'campaign_login_bonus' => [],
    'sequential_login_bonus' => [],
    'event_exchange_item_data' => [],
    'success' => true,
];

SendEncryptedResponse('DailyResponse', $data);
