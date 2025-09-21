<?php
require './utils.php';

$key = '28wqSLLEpKrcTDw0SZvJJJnU';
$iv = $_SERVER['HTTP_NGZ_IV'];
header('ngz_iv: ' . $iv);

if (!isset($iv) || $iv == '') {
    header('HTTP/1.1 500 Internal Server Error');
}

$data = file_get_contents('response/get_home_current.json');
echo RijndaelEncrypt($key, $iv, $data);
