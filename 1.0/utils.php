<?php
require 'vendor/autoload.php';

use phpseclib3\Crypt\Rijndael;

function RijndaelEncrypt($key, $iv, $plainText)
{
    $blockSize = 32;
    $padLen = $blockSize - (strlen($plainText) % $blockSize);
    $plainTextPadded = $plainText . str_repeat("\x00", $padLen);

    $cipher = new Rijndael('cbc');
    $cipher->setBlockLength(256);
    $cipher->setKey($key);
    $cipher->setIV($iv);
    $cipher->disablePadding();

    $cipherText = $cipher->encrypt($plainTextPadded);

    return base64_encode($cipherText);
}

function RijndaelDecrypt($key, $iv, $cipherText)
{
    $b64Cipher = base64_decode($cipherText);

    $cipher = new Rijndael('cbc');
    $cipher->setBlockLength(256);
    $cipher->setKey($key);
    $cipher->setIV($iv);
    $cipher->disablePadding();

    $plainText = $cipher->decrypt($b64Cipher);

    return rtrim($plainText, "\x00");
}

function GetApiKey($name)
{
    $keyList = json_decode(file_get_contents("rijndael_keys.json"), true);
    return $keyList[$name];
}

function GetUnitLevel($rarity)
{
    $levelMap = [
        '1' => '20',
        '2' => '40',
        '3' => '60',
        '4' => '70',
        '5' => '80',
        '6' => '90',
        '7' => '80',
        '8' => '90'
    ];
    return $levelMap[$rarity] ?? 0;
}
