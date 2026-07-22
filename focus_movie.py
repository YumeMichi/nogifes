import re

from master_data import (
    get_focus_movie_by_unit_id,
    get_girl_by_girl_id,
    get_girl_list,
    get_reward_movie_by_unit_id,
    get_unit_by_girl_id,
)
from utils import (
    build_download_path,
    build_resource_url,
    download_cpk_movie,
    download_usm_movie,
    load_download_records,
    normalize_unicode,
    sanitize_filename,
    should_download_record,
    update_json_record,
)

FOCUS_MOVIE_DATA_PATH = "data/focus_movie.json"
REWARD_FOCUS_MOVIE_DATA_PATH = "data/reward_focus_movie.json"


def download_focus_movie(girl_id: int) -> None:
    girl_data = get_girl_by_girl_id(girl_id)
    if girl_data is None:
        return

    match_index = 0
    downloaded_movies = load_download_records(FOCUS_MOVIE_DATA_PATH, "movie_id")
    for unit in get_unit_by_girl_id(girl_id):
        if "[F]" not in unit["unit_name"] or unit["rarity"] % 2 != 1:
            continue

        movie_data = get_focus_movie_by_unit_id(unit["unit_id"])
        if movie_data is None:
            continue

        match_index += 1
        movie_name = f"{movie_data['focus_movie_name']} ({movie_data['live_name']})"
        movie_file_name = f"focus_data_{movie_data['focus_movie_id']:05d}.cpk"
        movie_url = build_resource_url("focus_movie", movie_file_name)
        movie_save_name = f"{match_index}、{sanitize_filename(movie_name)}.mp4"
        movie_save_path = build_download_path("focus_movie", girl_data["girl_name"], movie_save_name)

        if movie_data["high_quality"] == 1:
            movie_save_path = build_download_path("high_focus_movie", girl_data["girl_name"], movie_save_name)
            movie_file_name = f"focus_data_high_{movie_data['focus_movie_id']:05d}.cpk"
            movie_url = build_resource_url("high_focus_movie", movie_file_name)

        movie = {
            "movie_id": movie_data["focus_movie_id"],
            "movie_name": normalize_unicode(movie_data["focus_movie_name"]),
            "live_name": normalize_unicode(movie_data["live_name"]),
            "live_date": movie_data["live_date"],
            "live_location": normalize_unicode(movie_data["live_location"]),
            "high_quality": movie_data["high_quality"],
            "girl_name": girl_data["girl_name"],
        }

        if not should_download_record(
            downloaded_movies, movie, "movie_id", quality_key="high_quality"
        ):
            continue

        if download_cpk_movie(movie_url, movie_file_name, movie_save_path):
            update_json_record(FOCUS_MOVIE_DATA_PATH, movie, "movie_id")
            downloaded_movies[movie["movie_id"]] = movie


def download_reward_focus_movie(girl_id: int) -> None:
    girl_data = get_girl_by_girl_id(girl_id)
    if girl_data is None:
        return

    downloaded_movies = load_download_records(REWARD_FOCUS_MOVIE_DATA_PATH, "movie_id")
    for unit in get_unit_by_girl_id(girl_id):
        movie_data = get_reward_movie_by_unit_id(unit["unit_id"])
        if movie_data is None or "[F]" not in movie_data["reward_movie_name"]:
            continue

        movie_name_parts = movie_data["reward_movie_name"].split("<br />")
        if len(movie_name_parts) > 1:
            sub_movie_name, main_movie_name = movie_name_parts
            movie_name = f"{main_movie_name} ({sub_movie_name.replace('全ツ', '真夏の全国ツアー')})"
        else:
            movie_name = movie_name_parts[0].replace("全ツ", "真夏の全国ツアー")

        movie_name = re.sub(
            r"\[F\]|\s*SP(?: MOVIE|フルフォーカスMOVIE|ライブフォーカスMOVIE|ライブMOVIE|ﾌﾙﾌｫｰｶｽMOVIE|ﾌｫｰｶｽMOVIE)",
            "",
            movie_name,
        )
        movie_file_name = f"reward_movie_{movie_data['reward_movie_id']:05d}.usme"
        movie_url = build_resource_url("reward_movie", movie_file_name)
        movie_save_name = f"{sanitize_filename(movie_name)}.mp4"
        movie_save_path = build_download_path("reward_focus_movie", girl_data["girl_name"], movie_save_name)

        movie = {
            "movie_id": movie_data["reward_movie_id"],
            "movie_name": normalize_unicode(movie_data["reward_movie_name"]),
            "girl_name": girl_data["girl_name"],
        }

        if not should_download_record(downloaded_movies, movie, "movie_id"):
            continue

        if download_usm_movie(movie_url, movie_file_name, movie_save_path):
            update_json_record(REWARD_FOCUS_MOVIE_DATA_PATH, movie, "movie_id")
            downloaded_movies[movie["movie_id"]] = movie


if __name__ == "__main__":
    for girl in get_girl_list():
        download_focus_movie(girl["girl_id"])
        download_reward_focus_movie(girl["girl_id"])
