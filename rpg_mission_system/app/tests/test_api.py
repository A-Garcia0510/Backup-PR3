import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base, get_db
from app.main import app

# Create test database
SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///./test_api_rpg_missions.db"
engine = create_engine(
    SQLALCHEMY_TEST_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Override the get_db dependency to use test database
@pytest.fixture(scope="module")
def test_db():
    # Create test database tables
    Base.metadata.create_all(bind=engine)
    
    # Create a session
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        # Drop test database tables
        Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="module")
def client(test_db):
    def override_get_db():
        try:
            yield test_db
        finally:
            test_db.close()
    
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides = {}

def test_read_root(client):
    response = client.get("/")
    assert response.status_code == 200
    assert "message" in response.json()
    assert "docs" in response.json()

def test_create_character(client):
    response = client.post(
        "/characters/",
        json={"name": "API Test Character", "level": 1, "experience": 0}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "API Test Character"
    assert "id" in data
    
    # Store character ID for future tests
    character_id = data["id"]
    return character_id

def test_create_mission(client):
    response = client.post(
        "/missions/",
        json={
            "title": "API Test Mission",
            "description": "Test mission created from API test", 
            "xp_reward": 150,
            "difficulty": 2
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "API Test Mission"
    assert "id" in data
    
    # Store mission ID for future tests
    mission_id = data["id"]
    return mission_id

def test_mission_workflow(client):
    # Create character and mission
    character_id = test_create_character(client)
    mission_id = test_create_mission(client)
    
    # Accept mission
    response = client.post(f"/missions/{mission_id}/accept?character_id={character_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["mission_id"] == mission_id
    assert data["character_id"] == character_id
    assert data["status"] == "pending"
    
    # Start mission
    response = client.post(f"/missions/{mission_id}/start?character_id={character_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "in_progress"
    
    # Get character missions
    response = client.get(f"/characters/{character_id}/missions")
    assert response.status_code == 200
    missions = response.json()
    assert len(missions) >= 1
    assert any(mission["status"] == "in_progress" for mission in missions)
    
    # Complete mission
    response = client.post(f"/missions/{mission_id}/complete?character_id={character_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "completed"
    
    # Check character got XP
    response = client.get(f"/characters/{character_id}")
    assert response.status_code == 200
    character = response.json()
    assert character["experience"] > 0