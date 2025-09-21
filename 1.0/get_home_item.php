<?php
require './utils.php';

$key = '4vte5053Dd8fIgATEZYeL4Ee';
$iv = $_SERVER['HTTP_NGZ_IV'];
header('ngz_iv: ' . $iv);

if (!isset($iv) || $iv == '') {
    header('HTTP/1.1 500 Internal Server Error');
}

$data = file_get_contents('response/get_home_item.json');
echo RijndaelEncrypt($key, $iv, $data);
