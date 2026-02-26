<?php
require './utils.php';

$master_data = LoadJsonFile('masterdata/MasterDataList.json');

$data = [
    'connect_key' => GetConnectKey(),
    'mstlist' => $master_data,
    'success' => true,
];

SendEncryptedResponse('GetMstlistResponse', $data);
