import shutil

from focus_movie import update_movie_data
from master_data import *
from utils import *

OTHER_MOVIE_DATA_PATH = "data/other_movie.json"

def download_other_movie():
    other_movie_data = get_other_movie_list()

    for movie_data in other_movie_data:
        movie_id = movie_data["other_movie_id"]
        movie_name = movie_data["other_movie_name"].split("_")[0]
        movie_file_name = f"other_data_{movie_id:05d}.cpk"
        movie_url = f"{RESOURCE_PATH['other_movie']}{movie_file_name}"
        movie_save_name = f"{sanitize_filename(f"{movie_name} ({movie_data["live_name"]})")}.mp4"
        movie_save_path = f"{DOWNLOAD_PATH["other_movie"]}{movie_save_name}"

        if movie_data["high_quality"] == 1:
            movie_file_name = f"other_data_high_{movie_id:05d}.cpk"
            movie_url = f"{RESOURCE_PATH['high_other_movie']}{movie_file_name}"
            movie_save_path = f"{DOWNLOAD_PATH["high_other_movie"]}{movie_save_name}"

        movie = {
            'movie_id': movie_id,
            'movie_name': movie_data["other_movie_name"],
            'live_name': movie_data["live_name"],
            'live_date': movie_data["live_date"],
            'live_location': normalize_unicode(movie_data["live_location"]),
            'high_quality': movie_data["high_quality"],
        }

        if os.path.exists(movie_save_path):
            print(f"{movie_save_name} already exists")
            continue

        cpk_path = os.path.join(TEMP_DIR, movie_file_name)
        if os.path.exists(cpk_path):
            os.remove(cpk_path)

        if download(movie_url, movie_file_name):
            if extrack_cpk(cpk_path):
                extracted_path = cpk_path[:-4]
                movie_path = f"{extracted_path}/movie"
                music_path = f"{extracted_path}/music"
                if extract_usm(movie_path) and extract_acb(music_path):
                    video_path = f"{TEMP_DIR}/movie.264_med"
                    audio_path = f"{TEMP_DIR}/0.wav"
                    if remux_video(video_path, audio_path, movie_save_path):
                        os.remove(video_path)
                        os.remove(audio_path)
                        os.remove(cpk_path)
                        shutil.rmtree(extracted_path)
                        update_movie_data(OTHER_MOVIE_DATA_PATH, movie)
                        print(f"Successfully extracted {movie_save_name}")

if __name__ == '__main__':
    download_other_movie()
