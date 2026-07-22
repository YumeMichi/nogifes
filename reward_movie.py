import re

from master_data import get_reward_movie_list, get_unit_girl_list
from utils import (
    build_download_path,
    build_resource_url,
    download_usm_movie,
    load_download_records,
    normalize_unicode,
    sanitize_filename,
    should_download_record,
    update_json_record,
)

REWARD_MOVIE_DATA_PATH = "data/reward_movie.json"


def _display_movie_name(raw_name: str) -> str:
    movie_name_parts = raw_name.split("<br />")
    if len(movie_name_parts) > 1:
        sub_movie_name, main_movie_name = movie_name_parts
        movie_name = f"{main_movie_name} ({sub_movie_name.replace('全ツ', '真夏の全国ツアー')})"
    else:
        movie_name = movie_name_parts[0].replace("全ツ", "真夏の全国ツアー")

    return re.sub(
        r"\[F\]|\s*SP(?: MOVIE|フルフォーカスMOVIE|ライブフォーカスMOVIE|ライブMOVIE|ﾌﾙﾌｫｰｶｽMOVIE|ﾌｫｰｶｽMOVIE)",
        "",
        movie_name,
    )


def download_reward_movie(*, force: bool = False) -> None:
    unit_girl_data = get_unit_girl_list()
    downloaded_movies = load_download_records(REWARD_MOVIE_DATA_PATH, "movie_id")
    for movie_data in get_reward_movie_list():
        girl_name = "、".join(unit_girl_data[movie_data["unit_data"][0]["unit_id"]])
        movie_name = _display_movie_name(movie_data["reward_movie_name"])
        movie_file_name = f"reward_movie_{movie_data['reward_movie_id']:05d}.usme"
        movie_url = build_resource_url("reward_movie", movie_file_name)
        movie_save_name = f"{sanitize_filename(movie_name)}.mp4"
        movie_save_path = build_download_path("reward_movie", girl_name, movie_save_name)
        movie = {
            "movie_id": movie_data["reward_movie_id"],
            "movie_name": normalize_unicode(movie_data["reward_movie_name"]),
            "girl_name": girl_name,
        }

        if not force and not should_download_record(downloaded_movies, movie, "movie_id"):
            continue

        if download_usm_movie(movie_url, movie_file_name, movie_save_path, force=force):
            update_json_record(REWARD_MOVIE_DATA_PATH, movie, "movie_id")
            downloaded_movies[movie["movie_id"]] = movie


if __name__ == "__main__":
    download_reward_movie()
