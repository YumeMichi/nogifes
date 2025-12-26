<?php
require './1.0/utils.php';

$encoded = '';
$error = '';

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $key = trim($_POST['key'] ?? '');
    $iv = trim($_POST['iv'] ?? '');
    $data = trim($_POST['data'] ?? '');

    if ($key && $iv && $data) {
        try {
            $decoded = json_decode(RijndaelDecrypt($key, $iv, $data), true);
            $encoded = json_encode($decoded, JSON_UNESCAPED_UNICODE | JSON_PRETTY_PRINT);
        } catch (Exception $e) {
            $error = '解密失败: ' . htmlspecialchars($e->getMessage());
        }
    } else {
        $error = '请输入完整的 Key, IV 和 Data。';
    }
}
?>

<!DOCTYPE html>
<html>

<head>
    <meta charset="UTF-8">
    <title>NogiFes 解密工具</title>
    <style>
        pre {
            background: #f4f4f4;
            padding: 10px;
            border: 1px solid #ccc;
            white-space: pre-wrap;
            max-width: 60%;
        }

        .error {
            color: red;
        }
    </style>
</head>

<body>
    <h2>NogiFes 解密工具</h2>
    <form method="post">
        <label for="key">Rijndael Key</label><br>
        <input name="key" id="key" size="32" maxlength="24" value="<?= htmlspecialchars($_POST['key'] ?? '') ?>" /><br><br>

        <label for="iv">Rijndael IV</label><br>
        <input name="iv" id="iv" size="32" maxlength="32" value="<?= htmlspecialchars($_POST['iv'] ?? '') ?>" /><br><br>

        <label for="data">Data (Base64)</label><br>
        <textarea name="data" id="data" cols="100" rows="10"><?= htmlspecialchars($_POST['data'] ?? '') ?></textarea><br><br>

        <div class="buttons">
            <button type="submit">解密</button>
            <?php if ($encoded): ?>
                <button type="button" onclick="copyToClipboard()">复制结果</button>
            <?php endif; ?>
        </div>
    </form>

    <?php if ($error): ?>
        <p class="error"><?= $error ?></p>
    <?php elseif ($encoded): ?>
        <h3>解密结果</h3>
        <pre id="output"><?= htmlspecialchars($encoded) ?></pre>
    <?php endif; ?>

    <script>
        function copyToClipboard() {
            const output = document.getElementById("output");
            if (!output) {
                alert("没有结果可复制");
                return;
            }

            const text = output.innerText;

            if (navigator.clipboard && navigator.clipboard.writeText) {
                navigator.clipboard.writeText(text).then(function() {
                    alert("结果已复制到剪贴板");
                }).catch(function(err) {
                    fallbackCopy(text);
                });
            } else {
                fallbackCopy(text);
            }
        }

        function fallbackCopy(text) {
            const textarea = document.createElement("textarea");
            textarea.value = text;
            textarea.style.position = "fixed"; // 防止页面跳动
            document.body.appendChild(textarea);
            textarea.focus();
            textarea.select();

            try {
                const successful = document.execCommand('copy');
                if (successful) {
                    //alert("结果已复制到剪贴板（兼容模式）");
                } else {
                    alert("复制失败，请手动复制");
                }
            } catch (err) {
                alert("复制失败: " + err);
            }

            document.body.removeChild(textarea);
        }
    </script>

</body>

</html>
