import shutil
import UnityPy

from master_data import *
from utils import *

def download_member_standing():
    girl_map = get_girl_map()

    asset_bundle_name = "Android" # Android
    asset_bundle_path = os.path.join(TEMP_DIR, asset_bundle_name)
    if os.path.exists(asset_bundle_path):
        os.remove(asset_bundle_path)

    asset_bundle_url = f"{RESOURCE_PATH['asset_bundle']}{asset_bundle_name}"
    if download(asset_bundle_url, asset_bundle_name):
        env = UnityPy.load(asset_bundle_path)
        for obj in env.objects:
            if obj.type.name == "AssetBundleManifest":
                data = obj.parse_as_dict()
                for item in data["AssetBundleNames"]:
                    if "standing" in item[1]:
                        standing_data = item[1].split("/")
                        standing_url = f"{RESOURCE_PATH["asset_bundle"]}{item[1]}"
                        girl_name = girl_map[int(standing_data[2])]
                        standing_file_name = standing_data[3]
                        standing_save_path = f"{DOWNLOAD_PATH["member_standing"]}{girl_name}/{standing_file_name}"

                        standing_path = os.path.join(TEMP_DIR, standing_file_name)
                        if os.path.exists(standing_path):
                            os.remove(standing_path)

                        if not check_complete(standing_save_path):
                            if os.path.exists(standing_save_path):
                                shutil.rmtree(standing_save_path)
                            os.makedirs(standing_save_path, exist_ok=True)

                            if download(standing_url, standing_file_name):
                                for file_name in extract_unity_assets(standing_path):
                                    shutil.move(file_name, standing_save_path)
                                os.remove(standing_path)
                                write_complete(standing_save_path)

if __name__ == "__main__":
    download_member_standing()
