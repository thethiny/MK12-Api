import json
import pytest
import os

from src.utils.random_data import get_random_collection, get_static_collection
from src.x_ag import json_to_ag
from src.x_ag import ag_to_json

@pytest.fixture
def random_data_fixture():
    return get_random_collection()

@pytest.fixture
def static_data_fixture():
    return get_static_collection()

@pytest.fixture
def shop_data_fixture():
    with open(os.path.join("tests", "test_data", "mk11_example.json")) as file:
        return json.load(file)

def test_random_collection(random_data_fixture):
    converted = json_to_ag(random_data_fixture)

def test_json_collection(shop_data_fixture):
    converted = json_to_ag(shop_data_fixture)

def test_static_collection(static_data_fixture):
    converted = json_to_ag(static_data_fixture)

def test_random_collection_both(random_data_fixture):
    converted = json_to_ag(random_data_fixture)
    converted = ag_to_json(converted)

def test_json_collection_both(shop_data_fixture):
    converted = json_to_ag(shop_data_fixture)
    converted = ag_to_json(converted)

def test_static_collection_both(static_data_fixture):
    converted = json_to_ag(static_data_fixture)
    converted = ag_to_json(converted)


if __name__ == "__main__":
    with open(os.path.join("tests", "test_data", "mk11_example.json")) as file:
        shop_data = json.load(file)
    bson_data = get_random_collection()
    static_data = get_static_collection()

    test_random_collection(bson_data)
    test_json_collection(shop_data)
    test_static_collection(static_data)
    
    test_random_collection_both(bson_data)
    test_json_collection_both(shop_data)
    test_static_collection_both(static_data)
