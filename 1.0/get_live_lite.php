<?php
require './utils.php';

$key = 'Pn56dWkGjcBDsaGHc2VQ8s2L';
$iv = $_SERVER['HTTP_NGZ_IV'];
header('ngz_iv: ' . $iv);

if (!isset($iv) || $iv == '') {
    header('HTTP/1.1 500 Internal Server Error');
}

$data = file_get_contents('response/get_live_lite.json');
echo RijndaelEncrypt($key, $iv, $data);
