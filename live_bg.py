from master_data import get_live_bg_list, get_resource_list
from utils import (
    build_download_path,
    build_resource_url,
    download_cpk_movie,
    load_download_records,
    sanitize_filename,
    should_download_record,
    update_json_record,
)

LIVE_BG_RESOURCE_TYPE = (8, 33)
LIVE_BG_DATA_PATH = "data/live_bg.json"


def download_live_bg(*, force: bool = False) -> None:
    resources_by_background: dict[int, list[dict]] = {}
    downloaded_backgrounds = load_download_records(LIVE_BG_DATA_PATH, "live_bg_id")
    for resource in get_resource_list():
        if resource["resource_type"] in LIVE_BG_RESOURCE_TYPE:
            resources_by_background.setdefault(resource["sub_id"], []).append(resource)

    for live_bg in get_live_bg_list():
        if live_bg["live_bg_type"] != 1:
            continue

        for resource in resources_by_background.get(live_bg["live_bg_id"], []):
            bg_name = live_bg["live_bg_name"]
            bg_file_name = resource["filename"]
            is_high_quality = resource["resource_type"] == 33
            resource_key = "high_live_bg" if is_high_quality else "live_bg"
            bg_url = build_resource_url(resource_key, bg_file_name)
            bg_save_name = f"{sanitize_filename(bg_name)}.mp4"
            if live_bg["live_name"] != "--":
                display_name = f"{bg_name} ({live_bg['live_name']})"
                bg_save_name = f"{sanitize_filename(display_name)}.mp4"
            bg_save_path = build_download_path(resource_key, bg_save_name)

            bg = {
                "live_bg_id": live_bg["live_bg_id"],
                "live_bg_name": bg_name,
                "live_bg_has_high_quality": int(is_high_quality),
            }

            if not force and not should_download_record(
                downloaded_backgrounds,
                bg,
                "live_bg_id",
                quality_key="live_bg_has_high_quality",
            ):
                continue

            if download_cpk_movie(bg_url, bg_file_name, bg_save_path, force=force):
                update_json_record(LIVE_BG_DATA_PATH, bg, "live_bg_id")
                downloaded_backgrounds[bg["live_bg_id"]] = bg


if __name__ == "__main__":
    download_live_bg()
