<?php
require './utils.php';

$key = GetApiKey("DoInheritResponse");
$iv = $_SERVER['HTTP_NGZ_IV'];
header('ngz_iv: ' . $iv);

if (!isset($iv) || $iv == '') {
    header('HTTP/1.1 500 Internal Server Error');
}

$data = file_get_contents('response/do_inherit.json');
echo RijndaelEncrypt($key, $iv, $data);
