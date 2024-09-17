import json
import pytest

from src.utils.random_data import get_random_collection
from src.x_ag import json_to_ag
from src.x_ag import ag_to_json

@pytest.fixture
def random_data_fixture():
    return get_random_collection()

@pytest.fixture
def shop_data_fixture():
    with open("premium_shop.json") as file:
        return json.load(file)

def test_random_collection(random_data_fixture):
    print(random_data_fixture)
    converted = json_to_ag(random_data_fixture)
    print(converted)

def test_json_collection(shop_data_fixture):
    converted = json_to_ag(shop_data_fixture)
    print(converted)
