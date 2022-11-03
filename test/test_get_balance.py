from unittest.mock import Mock
from fastapi.testclient import TestClient

from routers import add_balance
from schemas import BalanceInput, User, Balance
from expenses import app

client = TestClient(app)


def test_get_cars():
    response = client.get("/api/balance/")
    assert response.status_code == 200
    cars = response.json()
    # assert all(["doors" in c for c in cars])
    # assert all(["size" in c for c in cars])

def test_add_car():
    response = client.post("/api/cars/",
                           json={
                               "doors": 7,
                               "size": "xxl"
                           }, headers={'Authorization': 'Bearer reindert'}
                           )
    assert response.status_code == 200
    car = response.json()
    assert car['doors'] == 7
    assert car['size'] == 'xxl'


def test_add_car_with_mock_session():
    mock_session = Mock()
    input = BalanceInput(periodo="202312")
    user = User(username="reindert")
    result = add_balance(balance_input=input, session=mock_session, user=user)

    mock_session.add.assert_called_once()
    mock_session.commit.assert_called_once()
    mock_session.refresh.assert_called_once()
    assert isinstance(result, Balance)
    #assert result.doors == 2
    #assert result.size == "xl"