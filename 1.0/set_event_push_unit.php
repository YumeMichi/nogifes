<?php
require './utils.php';

$key = 'ACj3XbMVFaSBjVJ9iUnvqySA';
$iv = $_SERVER['HTTP_NGZ_IV'];
header('ngz_iv: ' . $iv);

if (!isset($iv) || $iv == '') {
    header('HTTP/1.1 500 Internal Server Error');
}

$data = file_get_contents('response/set_event_push_unit.json');
echo RijndaelEncrypt($key, $iv, $data);
