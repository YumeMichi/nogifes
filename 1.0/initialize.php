<?php
require './utils.php';

$key = '8ihNytHPB3WawDsULyDKwh5T';
$iv = $_SERVER['HTTP_NGZ_IV'];
header('ngz_iv: ' . $iv);

if (!isset($iv) || $iv == '') {
    header('HTTP/1.1 500 Internal Server Error');
}

$data = file_get_contents('response/initialize.json');
echo RijndaelEncrypt($key, $iv, $data);
