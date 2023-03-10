import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

from main import app, get_session


@pytest.fixture(name="session")
def session_fixture():
    engine = create_engine(
        "sqlite:///./pytest.db",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


@pytest.fixture(name="client")
def client_fixture(session: Session):
    def get_session_override():
        return session

    app.dependency_overrides[get_session] = get_session_override
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


def test_create_property(client: TestClient, timestamp_str: str):
    response = client.get(
        f"/user/test_user/create/property/test_prop_per_api_{timestamp_str}"
    )
    assert response.status_code == 200
    print(f"{response.json()=}")
    # TODO check response content


def test_two_vetos(client: TestClient, timestamp_str: str):
    prop_name = f"test_prop_controversial_{timestamp_str}"

    response = client.get(f"/user/test_user_pro/create/property/{prop_name}")
    assert response.status_code == 200
    print(f"{response.json()=}")
    # TODO check response content

    response = client.get(f"/user/test_user_contra_1/veto/property/{prop_name}")
    assert response.status_code == 200
    print(f"{response.json()=}")
    # TODO check response content

    response = client.get(f"/user/test_user_contra_2/veto/property/{prop_name}")
    assert response.status_code == 200
    print(f"{response.json()=}")
    # TODO check response content