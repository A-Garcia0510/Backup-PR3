import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime

from app.database import Base
from app.models.character import Character
from app.models.mission import Mission
from app.models.character_mission import CharacterMission
from app.tda.queue import MissionQueue

# Create test database engine
SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///./test_rpg_missions.db"
engine = create_engine(
    SQLALCHEMY_TEST_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Setup and teardown for tests
@pytest.fixture(scope="function")
def db():
    # Create test database tables
    Base.metadata.create_all(bind=engine)
    
    # Create a session
    session = TestingSessionLocal()
    
    try:
        yield session
    finally:
        session.close()
        # Drop test database tables
        Base.metadata.drop_all(bind=engine)

def test_mission_queue_operations(db):
    """Test the basic operations of the mission queue"""
    # Create a test character
    character = Character(name="Test Character", level=1, experience=0)
    db.add(character)
    db.commit()
    
    # Create test missions
    mission1 = Mission(title="Mission 1", description="First test mission", xp_reward=100, difficulty=1)
    mission2 = Mission(title="Mission 2", description="Second test mission", xp_reward=200, difficulty=2)
    mission3 = Mission(title="Mission 3", description="Third test mission", xp_reward=300, difficulty=3)
    db.add_all([mission1, mission2, mission3])
    db.commit()
    
    # Create mission queue
    queue = MissionQueue(db, character.id)
    
    # Test is_empty and size
    assert queue.is_empty() == True
    assert queue.size() == 0
    
    # Test enqueue
    queue.enqueue(mission1.id)
    assert queue.is_empty() == False
    assert queue.size() == 1
    
    queue.enqueue(mission2.id)
    queue.enqueue(mission3.id)
    assert queue.size() == 3
    
    # Test first
    first_mission = queue.first()
    assert first_mission.mission_id == mission1.id
    assert first_mission.status == "pending"
    
    # Test start_next_mission
    started_mission = queue.start_next_mission()
    assert started_mission.mission_id == mission1.id
    assert started_mission.status == "in_progress"
    
    # Test dequeue (completing the mission)
    completed_mission = queue.dequeue()
    assert completed_mission.mission_id == mission1.id
    assert completed_mission.status == "completed"
    
    # Verify new first mission
    new_first = queue.first()
    assert new_first.mission_id == mission2.id
    
    # Test size after completion
    assert queue.size() == 2