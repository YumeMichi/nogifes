from master_data import get_other_movie_list
from utils import (
    build_download_path,
    build_resource_url,
    download_cpk_movie,
    load_download_records,
    normalize_unicode,
    sanitize_filename,
    should_download_record,
    update_json_record,
)

OTHER_MOVIE_DATA_PATH = "data/other_movie.json"


def download_other_movie(*, force: bool = False) -> None:
    downloaded_movies = load_download_records(OTHER_MOVIE_DATA_PATH, "movie_id")
    for movie_data in get_other_movie_list():
        movie_id = movie_data["other_movie_id"]
        movie_name = movie_data["other_movie_name"].split("_")[0]
        movie_file_name = f"other_data_{movie_id:05d}.cpk"
        resource_key = "other_movie"
        display_name = f"{movie_name} ({movie_data['live_name']})"
        movie_save_name = f"{sanitize_filename(display_name)}.mp4"

        if movie_data["high_quality"] == 1:
            movie_file_name = f"other_data_high_{movie_id:05d}.cpk"
            resource_key = "high_other_movie"

        movie_url = build_resource_url(resource_key, movie_file_name)
        movie_save_path = build_download_path(resource_key, movie_save_name)
        movie = {
            "movie_id": movie_id,
            "movie_name": movie_data["other_movie_name"],
            "live_name": movie_data["live_name"],
            "live_date": movie_data["live_date"],
            "live_location": normalize_unicode(movie_data["live_location"]),
            "high_quality": movie_data["high_quality"],
        }

        if not force and not should_download_record(
            downloaded_movies, movie, "movie_id", quality_key="high_quality"
        ):
            continue

        if download_cpk_movie(movie_url, movie_file_name, movie_save_path, force=force):
            update_json_record(OTHER_MOVIE_DATA_PATH, movie, "movie_id")
            downloaded_movies[movie["movie_id"]] = movie


if __name__ == "__main__":
    download_other_movie()
