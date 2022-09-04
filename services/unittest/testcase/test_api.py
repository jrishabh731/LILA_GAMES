import copy
import json
import sys
from unittest.mock import Mock

sys.path.append("/by/source/")
print(sys.path)
from handlers.multiplayer_mode_handler import EngineInspection
from schema.AreaMode import EngineInspectionSchema

get_results = []


class SessionMocker:
    def __init__(self, *args, **kwargs):
        pass

    def query(self, *args, **kwargs):
        return self

    def get(self, *args, **kwargs):
        return get_results

    def add_all(self, *args, **kwargs):
        pass

    def commit(self, *args, **kwargs):
        pass

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass


def test_get_engine_inspection():
    global get_results
    get_results = []
    results = EngineInspection(SessionMocker).get_engine_inspection("123")
    assert results == {"record": []}

    with open(r"/by/unittest/testdata/valid_data.json") as fd:
        data = json.load(fd)
    get_results = data
    test = EngineInspection(SessionMocker).get_engine_inspection("123")
    assert test == {"record": data}


def test_post_engine_inspection():
    # When schema is valid
    with open(r"/by/unittest/testdata/valid_post_data.json") as fd:
        full_data = json.load(fd)

    obj = EngineInspection(SessionMocker)
    obj.get_all_records_with_filter = Mock(return_value=[])
    results = obj.post_engine_inspection(full_data["valid_scenario"]["input"])
    assert results == full_data["valid_scenario"]["output"]

    # When inspection date is invalid
    obj = EngineInspection(SessionMocker)
    obj.get_all_records_with_filter = Mock(return_value=[])
    results = obj.post_engine_inspection(full_data["invalid_inspection_date"]["input"])
    assert results == full_data["invalid_inspection_date"]["output"]

    # When month is invalid
    obj = EngineInspection(SessionMocker)
    obj.get_all_records_with_filter = Mock(return_value=[])
    results = obj.post_engine_inspection(full_data["invalid_month"]["input"])
    assert results == full_data["invalid_month"]["output"]

    # When start time is invalid
    obj = EngineInspection(SessionMocker)
    obj.get_all_records_with_filter = Mock(return_value=[])
    results = obj.post_engine_inspection(full_data["invalid_start_time"]["input"])
    assert results == full_data["invalid_start_time"]["output"]

    # When record already exists in the db
    obj = EngineInspection(SessionMocker)
    dummy_obj = copy.deepcopy(full_data["already_exists_in_db"]["input"][0])
    dummy_obj["inspectionDate"] = dummy_obj.pop("inspection date", None)
    dummy_obj["inspectionStartTime"] = dummy_obj.pop("inspection time", "")
    obj.get_all_records_with_filter = Mock(
        return_value=[EngineInspectionSchema(**dummy_obj)]
    )
    results = obj.post_engine_inspection(full_data["already_exists_in_db"]["input"])
    assert results == full_data["already_exists_in_db"]["output"]
