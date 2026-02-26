import base64
import crijndael
import json
import hashlib
import requests
import secrets

from pathlib import Path
from utils import download

APPLICATION_VERSION = 21401
STORE_ID = 2  # Android

KEY_SIZE = 24
BLOCK_SIZE = 32
CBC_MODE = 0
ECB_MODE = 1

def padding(data: bytes, block_size=BLOCK_SIZE) -> bytes:
    pad_len = block_size - (len(data) % block_size)
    return data + b"\x00" * pad_len

def unpadding(data: bytes) -> bytes:
    return data.rstrip(b'\x00')

def rj256_encrypt_cbc(key_str: str, iv_str: str, plain_text: bytes | str) -> bytes:
    if isinstance(plain_text, str):
        plain_text = plain_text.encode("utf-8")

    return base64.b64encode(
        crijndael.encrypt(
            padding(plain_text, BLOCK_SIZE),
            key_str.encode(),
            iv_str.encode(),
            BLOCK_SIZE * 8,
            KEY_SIZE * 8,
            CBC_MODE
        )
    )

def rj256_decrypt_cbc(key_str: str, iv_str: str, b64_ciphertext: str) -> str:
    return (
        unpadding(
            crijndael.decrypt(
                base64.b64decode(b64_ciphertext),
                key_str.encode(),
                iv_str.encode(),
                BLOCK_SIZE * 8,
                KEY_SIZE * 8,
                CBC_MODE
            )
        ).decode("utf-8")
    )

def rj256_decrypt_ecb(key_str: str, b64_ciphertext: str) -> str:
    return (
        unpadding(
            crijndael.decrypt(
                base64.b64decode(b64_ciphertext),
                key_str.encode(),
                b'',
                BLOCK_SIZE * 8,
                KEY_SIZE * 8,
                ECB_MODE
            )
        ).decode("utf-8")
    )

def generate_iv() -> str:
    return secrets.token_hex(16)

def snake_to_pascal(name: str) -> str:
    return "".join(word.capitalize() for word in name.split("_"))

def sha256_file(path: str) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()

def nogifes_request(url: str, body: dict[str, str], decrypt_key: str) -> dict[str, str]:
    iv = generate_iv()
    headers = {
        "ngz_iv": iv,
    }

    encrypted_body = rj256_encrypt_cbc(
        decrypt_key,
        iv,
        json.dumps(body).encode("utf-8"),
    )

    response = requests.post(url, headers=headers, data=encrypted_body)
    response.raise_for_status()

    return json.loads(
        rj256_decrypt_cbc(
            decrypt_key,
            response.headers["ngz_iv"],
            response.content,
        )
    )

def download_master_data() -> None:
    # ======================
    # initialize
    # ======================
    initialize_body = {
        "user_token": "EZJbBbC5yaG7uRso",
        "locale": "ChineseSimplified",
        "model": "Xiaomi 24031PN0DC",
        "device_name": "2206123SC",
        "os_name": "Android",
        "os_version": "12",
        "device_token": "",
        "device_id": "c068d7e0-bcdf-4ba7-8cb0-94d8da9500881766628714",
        "application_version": APPLICATION_VERSION,
        "store_id": STORE_ID,
        "user_id": 20426802,
    }

    ret = nogifes_request(
        "https://v2api.nogifes.jp/1.0/initialize.php",
        initialize_body,
        "8ihNytHPB3WawDsULyDKwh5T"
    )

    if not ret["success"]:
        print(ret["error_data"]["userMessage"])
        return

    version_file = Path("mstlist_version.txt")
    local_version = int(version_file.read_text()) if version_file.exists() else 0

    if local_version == ret["mstlist_version"]:
        print(f"Current master data version: {local_version}")
        return

    print(f"New master data version: {ret['mstlist_version']} found!")
    version_file.write_text(str(ret["mstlist_version"]))

    # ======================
    # get masterdata list
    # ======================
    get_mst_body = {
        "application_version": APPLICATION_VERSION,
        "store_id": STORE_ID,
        "connect_key": ret["connect_key"],
        "user_id": 20426802,
    }

    ret = nogifes_request(
        "https://v2api.nogifes.jp/1.0/get_mstlist.php",
        get_mst_body,
        "Re2485NXmdqS37nGLK29U8Nb"
    )

    if not ret["success"]:
        print(ret["error_data"]["userMessage"])
        return

    masterdata_list_path = Path(f"1.0/masterdata/MasterDataList.json")
    masterdata_list_path.parent.mkdir(parents=True, exist_ok=True)
    masterdata_list_path.write_text(json.dumps(ret["mstlist"], ensure_ascii=False, indent=4) + "\n")

    # ======================
    # download masterdata
    # ======================
    temp_dir = Path("temp")
    temp_dir.mkdir(exist_ok=True)

    key_map = json.loads(Path("1.0/rijndael_keys.json").read_text())

    for mst in ret["mstlist"]:
        file_name = snake_to_pascal(mst["name"]) + "Master"
        temp_path = temp_dir / file_name

        if temp_path.exists():
            if sha256_file(temp_path) == mst["hash"]:
                print(f"{file_name} is up to date.")
                continue

        url = f"https://v2static.nogifes.jp/resource/mst/{mst['file']}?ver={mst['version']}"
        # print(f"Downloading {url}")

        for i in range(3):
            try:
                if download(url, file_name):
                    break
            except Exception:
                print(f"[{i+1}/3] Failed to download {mst['name']}")
                if i == 2:
                    raise

        file_key = key_map[file_name]
        decrypted = rj256_decrypt_ecb(file_key, Path(f"{temp_dir}/{file_name}").read_bytes())

        pretty = json.dumps(
            json.loads(decrypted),
            ensure_ascii=False,
            indent=4,
        )

        out_path = Path(f"1.0/masterdata/{file_name}.json")
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(pretty + "\n")

if __name__ == "__main__":
    download_master_data()
