<?php
require 'vendor/autoload.php';

use phpseclib3\Crypt\Rijndael;

function CreateRijndaelCipher($mode, $key, $iv = null)
{
    $cipher = new Rijndael($mode);
    $cipher->setBlockLength(256);
    $cipher->setKey($key);
    if ($iv !== null && $mode === 'cbc') {
        $cipher->setIV($iv);
    }
    $cipher->disablePadding();

    return $cipher;
}

function RijndaelEncrypt($key, $iv, $data)
{
    $plainText = json_encode($data);
    $blockSize = 32;
    $padLen = $blockSize - (strlen($plainText) % $blockSize);
    $plainTextPadded = $plainText . str_repeat("\x00", $padLen);

    $cipher = CreateRijndaelCipher('cbc', $key, $iv);

    $cipherText = $cipher->encrypt($plainTextPadded);

    return base64_encode($cipherText);
}

function RijndaelDecrypt($key, $iv, $cipherText)
{
    $b64Cipher = base64_decode($cipherText, true);
    if ($b64Cipher === false) {
        return '';
    }

    $cipher = CreateRijndaelCipher('cbc', $key, $iv);

    $plainText = $cipher->decrypt($b64Cipher);

    return rtrim($plainText, "\x00");
}

function RijndaelDecryptECB($key, $cipherText)
{
    $b64Cipher = base64_decode($cipherText, true);
    if ($b64Cipher === false) {
        return '';
    }

    $cipher = CreateRijndaelCipher('ecb', $key);

    $plainText = $cipher->decrypt($b64Cipher);

    return rtrim($plainText, "\x00");
}

function GetMasterdataVersion()
{
    return 351;
}

function GetConnectKey()
{
    $chars = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789';
    $charLength = strlen($chars);
    $length = 16;
    $result = '';

    for ($i = 0; $i < $length; $i++) {
        $result .= $chars[random_int(0, $charLength - 1)];
    }

    return $result;
}

function GetApiKey($name)
{
    static $keyList = null;
    if ($keyList === null) {
        $keyList = LoadJsonFile('rijndael_keys.json');
        if (!is_array($keyList)) {
            $keyList = [];
        }
    }

    return $keyList[$name] ?? '';
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

function LoadJsonFile($filePath, $useCache = true)
{
    static $jsonCache = [];

    if ($useCache && array_key_exists($filePath, $jsonCache)) {
        return $jsonCache[$filePath];
    }

    $content = file_get_contents($filePath);
    if ($content === false) {
        return [];
    }

    $decoded = json_decode($content, true);
    if (json_last_error() !== JSON_ERROR_NONE) {
        return [];
    }

    if ($useCache) {
        $jsonCache[$filePath] = $decoded;
    }

    return $decoded;
}

function GetNgzIvOrAbort()
{
    $iv = $_SERVER['HTTP_NGZ_IV'] ?? '';
    if ($iv === '') {
        http_response_code(400);
        exit;
    }

    header('ngz_iv: ' . $iv);
    return $iv;
}

function SendEncryptedResponse($apiName, $data)
{
    $key = GetApiKey($apiName);
    if ($key === '') {
        http_response_code(500);
        exit;
    }

    $iv = GetNgzIvOrAbort();
    echo RijndaelEncrypt($key, $iv, $data);
}
