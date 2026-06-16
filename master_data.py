import json
import functools
from pathlib import Path
from typing import Any

MASTER_DATA_PATH = Path("./1.0/masterdata/")

@functools.cache
def _load_master_data_cached(data_name: str) -> tuple[Any, ...]:
    with open(MASTER_DATA_PATH / f"{data_name}.json", encoding="utf-8") as f:
        return tuple(json.load(f))

def load_master_data(data_name: str) -> list[Any]:
    return list(_load_master_data_cached(data_name))

def get_girl_list() -> list[Any]:
    return load_master_data("GirlMaster")

def get_girl_map() -> dict[int, str]:
    return {item["girl_id"]: item["girl_name"].replace(" ", "") for item in get_girl_list()}

@functools.cache
def _girl_by_id_map() -> dict[int, dict[str, Any]]:
    return {item["girl_id"]: item for item in _load_master_data_cached("GirlMaster")}

def get_girl_by_girl_id(girl_id: int) -> dict[str, Any] | None:
    item = _girl_by_id_map().get(girl_id)
    if item is None:
        return None
    return {**item, "girl_name": item["girl_name"].replace(" ", "")}

def get_unit_list() -> list[Any]:
    return load_master_data("UnitMaster")

@functools.cache
def _unit_by_girl_id_map() -> dict[int, list[Any]]:
    result: dict[int, list[Any]] = {}
    for item in _load_master_data_cached("UnitMaster"):
        result.setdefault(item["girl_id1"], []).append(item)
        if item["girl_id2"] != 0:
            result.setdefault(item["girl_id2"], []).append(item)
    return result

def get_unit_by_girl_id(girl_id: int) -> list[Any]:
    return list(_unit_by_girl_id_map().get(girl_id, []))

def get_unit_girl_list() -> dict[int, list[str]]:
    girl_data = get_girl_map()
    unit_girl_list = {}

    for item in load_master_data("UnitMaster"):
        girl_names = [girl_data[item["girl_id1"]]]
        if item["girl_id2"] != 0:
            girl_names.append(girl_data[item["girl_id2"]])
        unit_girl_list[item["unit_id"]] = girl_names

    return unit_girl_list

@functools.cache
def _focus_movie_by_unit_id_map() -> dict[int, dict[str, Any]]:
    result = {}
    for item in _load_master_data_cached("FocusMovieMaster"):
        for unit in item["unit_data"]:
            result[unit["unit_id"]] = item
    return result

def get_focus_movie_by_unit_id(unit_id: int) -> dict[str, Any] | None:
    return _focus_movie_by_unit_id_map().get(unit_id)

def get_reward_movie_list() -> list[Any]:
    return load_master_data("RewardMovieMaster")

@functools.cache
def _reward_movie_by_unit_id_map() -> dict[int, dict[str, Any]]:
    result = {}
    for item in _load_master_data_cached("RewardMovieMaster"):
        for unit in item["unit_data"]:
            result[unit["unit_id"]] = item
    return result

def get_reward_movie_by_unit_id(unit_id: int) -> dict[str, Any] | None:
    return _reward_movie_by_unit_id_map().get(unit_id)

def get_live_bg_list() -> list[Any]:
    return load_master_data("LiveBgMaster")

def get_resource_list() -> list[Any]:
    return load_master_data("ResourceMaster")

def get_other_movie_list() -> list[Any]:
    return load_master_data("OtherMovieMaster")

def get_unit_movie_list() -> list[Any]:
    return load_master_data("UnitMovieMaster")

def get_splash_movie_list() -> list[Any]:
    return load_master_data("SplashMaster")
