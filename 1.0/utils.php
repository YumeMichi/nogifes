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

function RijndaelDecryptECB($key, $cipherText)
{
    $b64Cipher = base64_decode($cipherText);

    $cipher = new Rijndael('ecb');
    $cipher->setBlockLength(256);
    $cipher->setKey($key);
    $cipher->disablePadding();

    $plainText = $cipher->decrypt($b64Cipher);

    return rtrim($plainText, "\x00");
}

function Post($url, $header, $data, $proxy = false)
{
    $ch = curl_init();

    curl_setopt($ch, CURLOPT_URL, $url);
    curl_setopt($ch, CURLOPT_HTTPHEADER, $header);
    curl_setopt($ch, CURLOPT_POST, 1);
    curl_setopt($ch, CURLOPT_POSTFIELDS, $data);
    curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
    curl_setopt($ch, CURLOPT_HEADER, true);
    curl_setopt($ch, CURLOPT_VERBOSE, true);
    if ($proxy) {
        curl_setopt($ch, CURLOPT_PROXY, "127.0.0.1:1082");
        curl_setopt($ch, CURLOPT_VERBOSE, false);
    }

    $response = curl_exec($ch);
    curl_close($ch);

    // 分离响应头和响应体
    $parts = preg_split("/\r?\n\r?\n/", $response, 3);
    $headerText = $parts[1] ?? '';
    $body = $parts[2] ?? '';

    // 将响应 header 转成数组
    $headers = [];
    foreach (explode("\n", $headerText) as $line) {
        $line = trim($line);
        if (strpos($line, ':') !== false) {
            list($key, $value) = explode(':', $line, 2);
            $headers[trim($key)] = trim($value);
        }
    }

    // 提取指定字段
    $ngz_iv = $headers['ngz_iv'] ?? null;
    $error_type = $headers['error_type'] ?? null;
    $error_code = $headers['error_code'] ?? null;

    return [
        'ngz_iv' => $ngz_iv,
        'error_type' => $error_type,
        'error_code' => $error_code,
        'body' => $body
    ];
}

function Get($url, $proxy = false)
{
    $ch = curl_init();

    curl_setopt($ch, CURLOPT_URL, $url);
    curl_setopt($ch, CURLOPT_POST, 0);
    curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
    if ($proxy) {
        curl_setopt($ch, CURLOPT_PROXY, "127.0.0.1:1082");
    }

    $response = curl_exec($ch);
    curl_close($ch);

    return $response;
}

function GenerateCommonHeader($ngz_iv)
{
    return array(
        'Accept-Encoding: deflate, gzip',
        'Content-Type: application/octet-stream',
        'User-Agent: UnityPlayer/6000.0.58f2 (UnityWebRequest/1.0, libcurl/8.10.1-DEV)',
        'X-Unity-Version: 6000.0.58f2',
        'ngz_iv: ' . $ngz_iv,
    );
}

function GenerateIV()
{
    return bin2hex(random_bytes(16));
}

function SnakeToPascal($name)
{
    $name = str_replace('_', ' ', $name);
    $name = ucwords($name);

    return str_replace(' ', '', $name);
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
