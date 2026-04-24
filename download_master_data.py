import base64
import crijndael
import json
import hashlib
import requests
import secrets

from collections import defaultdict
from pathlib import Path
from typing import Any
from config import API_BASE_URL, STATIC_BASE_URL
from utils import download

APPLICATION_VERSION = 21402
STORE_ID = 2  # Android
API_VERSION_PATH = "1.0"

KEY_SIZE = 24
BLOCK_SIZE = 32
CBC_MODE = 0
ECB_MODE = 1
VIDEO_RELATED_MASTERS = (
    "GirlMaster",
    "UnitMaster",
    "FocusMovieMaster",
    "RewardMovieMaster",
    "OtherMovieMaster",
    "LiveBgMaster",
    "ResourceMaster",
    "UnitMovieMaster",
)

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

def sha256_file(path: Path) -> str:
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

def load_master_list(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []

    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return []

    if isinstance(data, list):
        return [item for item in data if isinstance(item, dict)]
    return []

def snapshot_video_related_masterdata() -> dict[str, list[dict[str, Any]]]:
    base_dir = Path("1.0/masterdata")
    snapshot: dict[str, list[dict[str, Any]]] = {}
    for name in VIDEO_RELATED_MASTERS:
        snapshot[name] = load_master_list(base_dir / f"{name}.json")
    return snapshot

def build_girl_name_map(girl_master: list[dict[str, Any]]) -> dict[int, str]:
    return {
        item["girl_id"]: str(item["girl_name"]).replace(" ", "")
        for item in girl_master
        if "girl_id" in item and "girl_name" in item
    }

def build_unit_girl_map(
    unit_master: list[dict[str, Any]],
    girl_name_map: dict[int, str],
) -> dict[int, list[str]]:
    unit_girl_map: dict[int, list[str]] = {}
    for unit in unit_master:
        unit_id = unit.get("unit_id")
        girl_id1 = unit.get("girl_id1")
        girl_id2 = unit.get("girl_id2", 0)

        if not isinstance(unit_id, int):
            continue

        names: list[str] = []
        if isinstance(girl_id1, int) and girl_id1 in girl_name_map:
            names.append(girl_name_map[girl_id1])
        if isinstance(girl_id2, int) and girl_id2 != 0 and girl_id2 in girl_name_map:
            names.append(girl_name_map[girl_id2])

        unit_girl_map[unit_id] = names
    return unit_girl_map

def resolve_members(unit_data: list[dict[str, Any]], unit_girl_map: dict[int, list[str]]) -> str:
    names: list[str] = []
    for unit in unit_data:
        unit_id = unit.get("unit_id")
        if not isinstance(unit_id, int):
            continue
        for girl_name in unit_girl_map.get(unit_id, []):
            if girl_name not in names:
                names.append(girl_name)
    if names:
        return "、".join(names)
    return "未知成员"

def quality_text(has_high_quality: int) -> str:
    return "高画质" if has_high_quality == 1 else "低画质"

def live_bg_quality_map(resource_master: list[dict[str, Any]]) -> dict[int, dict[str, bool]]:
    quality: dict[int, dict[str, bool]] = defaultdict(lambda: {"low": False, "high": False})
    for item in resource_master:
        resource_type = item.get("resource_type")
        bg_id = item.get("sub_id")
        if not isinstance(bg_id, int) or resource_type not in (8, 33):
            continue
        if resource_type == 8:
            quality[bg_id]["low"] = True
        if resource_type == 33:
            quality[bg_id]["high"] = True
    return dict(quality)

def live_bg_quality_text(quality: dict[str, bool] | None) -> str:
    if not quality:
        return "未知画质"
    if quality.get("high", False):
        return "高画质"
    if quality.get("low", False):
        return "低画质"
    return "未知画质"

def compare_focus_movie(
    old_focus: list[dict[str, Any]],
    new_focus: list[dict[str, Any]],
    unit_girl_map: dict[int, list[str]],
) -> list[str]:
    lines: list[str] = []
    old_map = {item["focus_movie_id"]: item for item in old_focus if "focus_movie_id" in item}
    new_map = {item["focus_movie_id"]: item for item in new_focus if "focus_movie_id" in item}

    new_items = []
    upgraded_items = []
    for movie_id, item in new_map.items():
        members = resolve_members(item.get("unit_data", []), unit_girl_map)
        title = str(item.get("focus_movie_name", movie_id))
        quality = quality_text(int(item.get("high_quality", 0)))
        old_item = old_map.get(movie_id)
        if old_item is None:
            new_items.append((movie_id, members, title, quality))
            continue

        old_q = int(old_item.get("high_quality", 0))
        new_q = int(item.get("high_quality", 0))
        if old_q == 0 and new_q == 1:
            upgraded_items.append((movie_id, members, title, "低画质 -> 高画质"))

    if new_items:
        lines.append(f"新增: {len(new_items)}")
        for movie_id, members, title, quality in sorted(new_items, key=lambda x: x[0]):
            lines.append(f"  - {members}: {title} (ID:{movie_id}, {quality}, 新增)")
    if upgraded_items:
        lines.append(f"画质升级: {len(upgraded_items)}")
        for movie_id, members, title, transition in sorted(upgraded_items, key=lambda x: x[0]):
            lines.append(f"  - {members}: {title} (ID:{movie_id}, {transition})")

    return lines

def compare_other_movie(
    old_other: list[dict[str, Any]],
    new_other: list[dict[str, Any]],
    unit_girl_map: dict[int, list[str]],
) -> list[str]:
    lines: list[str] = []
    old_map = {item["other_movie_id"]: item for item in old_other if "other_movie_id" in item}
    new_map = {item["other_movie_id"]: item for item in new_other if "other_movie_id" in item}

    new_items = []
    upgraded_items = []
    for movie_id, item in new_map.items():
        members = resolve_members(item.get("unit_data", []), unit_girl_map)
        title = str(item.get("other_movie_name", movie_id))
        quality = quality_text(int(item.get("high_quality", 0)))
        old_item = old_map.get(movie_id)
        if old_item is None:
            new_items.append((movie_id, members, title, quality))
            continue

        old_q = int(old_item.get("high_quality", 0))
        new_q = int(item.get("high_quality", 0))
        if old_q == 0 and new_q == 1:
            upgraded_items.append((movie_id, members, title, "低画质 -> 高画质"))

    if new_items:
        lines.append(f"新增: {len(new_items)}")
        for movie_id, members, title, quality in sorted(new_items, key=lambda x: x[0]):
            lines.append(f"  - {members}: {title} (ID:{movie_id}, {quality}, 新增)")
    if upgraded_items:
        lines.append(f"画质升级: {len(upgraded_items)}")
        for movie_id, members, title, transition in sorted(upgraded_items, key=lambda x: x[0]):
            lines.append(f"  - {members}: {title} (ID:{movie_id}, {transition})")

    return lines

def compare_reward_movie(
    old_reward: list[dict[str, Any]],
    new_reward: list[dict[str, Any]],
    unit_girl_map: dict[int, list[str]],
) -> list[str]:
    old_ids = {
        item["reward_movie_id"]
        for item in old_reward
        if "reward_movie_id" in item
    }

    new_items = []
    for item in new_reward:
        movie_id = item.get("reward_movie_id")
        if movie_id in old_ids:
            continue
        members = resolve_members(item.get("unit_data", []), unit_girl_map)
        title = str(item.get("reward_movie_name", movie_id))
        new_items.append((movie_id, members, title))

    lines: list[str] = []
    if new_items:
        lines.append(f"新增: {len(new_items)}")
        for movie_id, members, title in sorted(new_items, key=lambda x: x[0]):
            lines.append(f"  - {members}: {title} (ID:{movie_id}, 新增)")
    return lines

def compare_unit_movie(
    old_unit_movie: list[dict[str, Any]],
    new_unit_movie: list[dict[str, Any]],
    unit_girl_map: dict[int, list[str]],
) -> list[str]:
    old_ids = {
        item["unit_movie_id"]
        for item in old_unit_movie
        if "unit_movie_id" in item
    }

    new_items = []
    for item in new_unit_movie:
        movie_id = item.get("unit_movie_id")
        if movie_id in old_ids:
            continue
        members = resolve_members(item.get("unit_data", []), unit_girl_map)
        title = str(item.get("unit_movie_name", movie_id))
        new_items.append((movie_id, members, title))

    lines: list[str] = []
    if new_items:
        lines.append(f"新增: {len(new_items)}")
        for movie_id, members, title in sorted(new_items, key=lambda x: x[0]):
            lines.append(f"  - {members}: {title} (ID:{movie_id}, 新增)")
    return lines

def compare_live_bg(
    old_live_bg: list[dict[str, Any]],
    new_live_bg: list[dict[str, Any]],
    old_resource: list[dict[str, Any]],
    new_resource: list[dict[str, Any]],
) -> list[str]:
    old_map = {item["live_bg_id"]: item for item in old_live_bg if "live_bg_id" in item}
    new_map = {item["live_bg_id"]: item for item in new_live_bg if "live_bg_id" in item}
    old_quality_map = live_bg_quality_map(old_resource)
    new_quality_map = live_bg_quality_map(new_resource)

    new_items = []
    upgraded_items = []
    for bg_id, item in new_map.items():
        title = str(item.get("live_bg_name", bg_id))
        live_name = str(item.get("live_name", "--"))
        quality_now = new_quality_map.get(bg_id)

        old_item = old_map.get(bg_id)
        if old_item is None:
            new_items.append((bg_id, title, live_name, live_bg_quality_text(quality_now)))
            continue

        old_quality = old_quality_map.get(bg_id, {"low": False, "high": False})
        new_quality = new_quality_map.get(bg_id, {"low": False, "high": False})
        if old_quality.get("high", False) is False and new_quality.get("high", False) is True:
            upgraded_items.append((bg_id, title, live_name, "低画质 -> 高画质"))

    lines: list[str] = []
    if new_items:
        lines.append(f"新增: {len(new_items)}")
        for bg_id, title, live_name, quality in sorted(new_items, key=lambda x: x[0]):
            if live_name != "--":
                lines.append(f"  - {title} ({live_name}) (ID:{bg_id}, {quality}, 新增)")
            else:
                lines.append(f"  - {title} (ID:{bg_id}, {quality}, 新增)")
    if upgraded_items:
        lines.append(f"画质升级: {len(upgraded_items)}")
        for bg_id, title, live_name, transition in sorted(upgraded_items, key=lambda x: x[0]):
            if live_name != "--":
                lines.append(f"  - {title} ({live_name}) (ID:{bg_id}, {transition})")
            else:
                lines.append(f"  - {title} (ID:{bg_id}, {transition})")
    return lines

def compare_unit_based_movies(
    old_unit: list[dict[str, Any]],
    new_unit: list[dict[str, Any]],
    unit_girl_map: dict[int, list[str]],
) -> tuple[list[str], list[str]]:
    old_map = {item["unit_id"]: item for item in old_unit if "unit_id" in item}
    new_map = {item["unit_id"]: item for item in new_unit if "unit_id" in item}

    gacha_new = []
    live_finish_new = []
    for unit_id, item in new_map.items():
        old_item = old_map.get(unit_id)
        members = "、".join(unit_girl_map.get(unit_id, [])) or "未知成员"
        unit_name = str(item.get("unit_name", unit_id))

        if int(item.get("gacha_movie", 0)) == 1 and (old_item is None or int(old_item.get("gacha_movie", 0)) == 0):
            gacha_new.append((unit_id, members, unit_name))

        old_live_finish_id = int(old_item.get("live_finish_movie_resource_id", 0)) if old_item else 0
        new_live_finish_id = int(item.get("live_finish_movie_resource_id", 0))
        if new_live_finish_id > 0 and old_live_finish_id == 0:
            live_finish_new.append((unit_id, members, unit_name, new_live_finish_id))

    gacha_lines: list[str] = []
    if gacha_new:
        gacha_lines.append(f"新增: {len(gacha_new)}")
        for unit_id, members, unit_name in sorted(gacha_new, key=lambda x: x[0]):
            gacha_lines.append(f"  - {members}: {unit_name} (UnitID:{unit_id}, 新增)")

    live_finish_lines: list[str] = []
    if live_finish_new:
        live_finish_lines.append(f"新增: {len(live_finish_new)}")
        for unit_id, members, unit_name, movie_id in sorted(live_finish_new, key=lambda x: x[0]):
            live_finish_lines.append(
                f"  - {members}: {unit_name} (UnitID:{unit_id}, MovieID:{movie_id}, 新增)"
            )

    return gacha_lines, live_finish_lines

def print_video_update_report(
    old_snapshot: dict[str, list[dict[str, Any]]],
    new_snapshot: dict[str, list[dict[str, Any]]],
) -> None:
    had_old_data = any(old_snapshot.get(name) for name in VIDEO_RELATED_MASTERS)
    if not had_old_data:
        print("更新报告: 未找到历史 master 快照，已跳过差异输出。")
        return

    new_girl_map = build_girl_name_map(new_snapshot.get("GirlMaster", []))
    new_unit_girl_map = build_unit_girl_map(new_snapshot.get("UnitMaster", []), new_girl_map)

    section_lines = {
        "FocusMovie": compare_focus_movie(
            old_snapshot.get("FocusMovieMaster", []),
            new_snapshot.get("FocusMovieMaster", []),
            new_unit_girl_map,
        ),
        "OtherMovie": compare_other_movie(
            old_snapshot.get("OtherMovieMaster", []),
            new_snapshot.get("OtherMovieMaster", []),
            new_unit_girl_map,
        ),
        "RewardMovie": compare_reward_movie(
            old_snapshot.get("RewardMovieMaster", []),
            new_snapshot.get("RewardMovieMaster", []),
            new_unit_girl_map,
        ),
        "UnitMovie": compare_unit_movie(
            old_snapshot.get("UnitMovieMaster", []),
            new_snapshot.get("UnitMovieMaster", []),
            new_unit_girl_map,
        ),
        "LiveBg": compare_live_bg(
            old_snapshot.get("LiveBgMaster", []),
            new_snapshot.get("LiveBgMaster", []),
            old_snapshot.get("ResourceMaster", []),
            new_snapshot.get("ResourceMaster", []),
        ),
    }

    unit_gacha_lines, live_finish_lines = compare_unit_based_movies(
        old_snapshot.get("UnitMaster", []),
        new_snapshot.get("UnitMaster", []),
        new_unit_girl_map,
    )
    section_lines["UnitGachaMovie"] = unit_gacha_lines
    section_lines["LiveFinishMovie"] = live_finish_lines

    if not any(section_lines.values()):
        print("更新报告: 本次 master 更新中未发现视频资源新增或画质升级。")
        return

    print("\n============ 更新报告 ============")
    for section, lines in section_lines.items():
        if not lines:
            continue
        print(f"\n[{section}]")
        for line in lines:
            print(line)
    print("\n===================================")

def download_master_data() -> None:
    # ======================
    # initialize
    # ======================
    initialize_body = {
        "user_token": "hCv7Nb9q3dyPhzcp",
        "locale": "ChineseSimplified",
        "model": "Xiaomi 24031PN0DC",
        "device_name": "2206123SC",
        "os_name": "Android",
        "os_version": "12",
        "device_token": "",
        "device_id": "abc0324d-b03f-433f-ac16-2c22404500621766798650",
        "application_version": APPLICATION_VERSION,
        "store_id": STORE_ID,
        "user_id": 20428873,
    }

    ret = nogifes_request(
        f"{API_BASE_URL}/{API_VERSION_PATH}/initialize.php",
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
        "user_id": 20428873,
    }

    ret = nogifes_request(
        f"{API_BASE_URL}/{API_VERSION_PATH}/get_mstlist.php",
        get_mst_body,
        "Re2485NXmdqS37nGLK29U8Nb"
    )

    if not ret["success"]:
        print(ret["error_data"]["userMessage"])
        return

    masterdata_list_path = Path(f"1.0/masterdata/MasterDataList.json")
    masterdata_list_path.parent.mkdir(parents=True, exist_ok=True)
    masterdata_list_path.write_text(json.dumps(ret["mstlist"], ensure_ascii=False, indent=4) + "\n")

    old_snapshot = snapshot_video_related_masterdata()

    # ======================
    # download masterdata
    # ======================
    temp_dir = Path("temp")
    temp_dir.mkdir(exist_ok=True)

    key_map = json.loads(Path("1.0/rijndael_keys.json").read_text())

    for mst in ret["mstlist"]:
        file_name = snake_to_pascal(mst["name"]) + "Master"
        temp_path = temp_dir / file_name

        if temp_path.exists() and sha256_file(temp_path) == mst["hash"]:
            print(f"{file_name} is up to date.")
            continue

        url = f"{STATIC_BASE_URL}/resource/mst/{mst['file']}?ver={mst['version']}"

        for i in range(3):
            try:
                if download(url, file_name):
                    break
            except Exception:
                print(f"[{i+1}/3] Failed to download {mst['name']}")
                if i == 2:
                    raise

        file_key = key_map[file_name]
        decrypted = rj256_decrypt_ecb(file_key, temp_path.read_bytes())
        pretty = json.dumps(json.loads(decrypted), ensure_ascii=False, indent=4)

        out_path = Path(f"1.0/masterdata/{file_name}.json")
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(pretty + "\n")

    new_snapshot = snapshot_video_related_masterdata()
    print_video_update_report(old_snapshot, new_snapshot)

if __name__ == "__main__":
    download_master_data()
