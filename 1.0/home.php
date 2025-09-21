<?php
require './utils.php';

$key = 'Zve3ruTjzsgjTPTUUnM9fTWw';
$iv = $_SERVER['HTTP_NGZ_IV'];
header('ngz_iv: ' . $iv);

if (!isset($iv) || $iv == '') {
    header('HTTP/1.1 500 Internal Server Error');
}

$data = file_get_contents('response/home.json');
echo RijndaelEncrypt($key, $iv, $data);
