import shutil

from master_data import *
from utils import *

def download_member_card():
    girl_map = get_girl_map()
    unit_data = get_unit_list()
    for unit in unit_data:
        girl_name = girl_map[unit["girl_id1"]]
        if unit["girl_id2"] != 0:
            girl_name = f"{girl_map[unit["girl_id1"]]}、{girl_map[unit["girl_id2"]]}"

        card_id = f"{unit["unit_id"]:07d}"
        card_file_name = f"card_{card_id}"
        card_l_file_name = f"card_l_{card_id}"
        card_url = f"{RESOURCE_PATH["asset_bundle"]}card/{card_id}/{card_file_name}"
        card_l_url = f"{RESOURCE_PATH["asset_bundle"]}card/{card_id}/{card_l_file_name}"
        card_save_path = f"{DOWNLOAD_PATH["member_card"]}{girl_name}/{card_id}"

        # card = {
        #     "card_id": unit["unit_id"],
        #     "card_url": card_url,
        #     "card_l_url": card_l_url,
        #     "girl_name": girl_name,
        # }
        # print(card)

        card_path = os.path.join(TEMP_DIR, card_file_name)
        if os.path.exists(card_path):
            os.remove(card_path)

        card_l_path = os.path.join(TEMP_DIR, card_l_file_name)
        if os.path.exists(card_l_path):
            os.remove(card_l_path)

        if not os.path.exists(card_save_path):
            os.makedirs(card_save_path, exist_ok=True)

        if not os.path.exists(os.path.join(card_save_path, "card_m.png")):
            if download(card_url, card_file_name):
                extract_unity_assets(card_path)
                if os.path.exists(os.path.join(TEMP_DIR, "card_m.png")):
                    shutil.move(os.path.join(TEMP_DIR, "card_m.png"), card_save_path)
                if os.path.exists(os.path.join(TEMP_DIR, "card_s.png")):
                    shutil.move(os.path.join(TEMP_DIR, "card_s.png"), card_save_path)
                if os.path.exists(os.path.join(TEMP_DIR, "icon.png")):
                    shutil.move(os.path.join(TEMP_DIR, "icon.png"), card_save_path)
                os.remove(card_path)

        if not os.path.exists(os.path.join(card_save_path, "card_l.png")):
            if download(card_l_url, card_l_file_name):
                extract_unity_assets(card_l_path)
                if os.path.exists(os.path.join(TEMP_DIR, "card_l.png")):
                    shutil.move(os.path.join(TEMP_DIR, "card_l.png"), card_save_path)
                os.remove(card_l_path)

if __name__ == '__main__':
    download_member_card()
