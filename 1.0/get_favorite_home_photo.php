<?php
require './utils.php';

$key = 'jKXNiD5f97AqF4QxTL8rVbYQ';
$iv = $_SERVER['HTTP_NGZ_IV'];
header('ngz_iv: ' . $iv);

if (!isset($iv) || $iv == '') {
    header('HTTP/1.1 500 Internal Server Error');
}

$data = file_get_contents('response/get_favorite_home_photo.json');
echo RijndaelEncrypt($key, $iv, $data);
