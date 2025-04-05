from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.character_mission import CharacterMission

class MissionQueue:
    """
    Implementation of a Queue (FIFO) data structure for managing character missions
    using SQLAlchemy for persistence.
    """
    
    def __init__(self, db: Session, character_id: int):
        """Initialize the mission queue for a specific character"""
        self.db = db
        self.character_id = character_id
    
    def is_empty(self) -> bool:
        """Check if the mission queue is empty"""
        return self.size() == 0
    
    def size(self) -> int:
        """Return the number of missions in the queue"""
        return self.db.query(CharacterMission).filter(
            CharacterMission.character_id == self.character_id,
            CharacterMission.status.in_(["pending", "in_progress"])
        ).count()
    
    def enqueue(self, mission_id: int) -> CharacterMission:
        """Add a mission to the end of the queue"""
        # Get the next queue position
        max_position = self.db.query(func.max(CharacterMission.queue_position)).filter(
            CharacterMission.character_id == self.character_id
        ).scalar() or 0
        
        # Create new character mission with the next position
        character_mission = CharacterMission(
            character_id=self.character_id,
            mission_id=mission_id,
            queue_position=max_position + 1,
            status="pending"
        )
        
        self.db.add(character_mission)
        self.db.commit()
        self.db.refresh(character_mission)
        
        return character_mission
    
    def dequeue(self) -> CharacterMission:
        """Remove and return the mission at the front of the queue (mark as completed)"""
        # Get the mission with the lowest queue position that is not completed
        mission = self.first()
        
        if mission:
            # Mark as completed
            mission.status = "completed"
            mission.completed_at = func.now()
            self.db.commit()
            self.db.refresh(mission)
        
        return mission
    
    def first(self) -> CharacterMission:
        """Return the mission at the front of the queue without removing it"""
        return self.db.query(CharacterMission).filter(
            CharacterMission.character_id == self.character_id,
            CharacterMission.status.in_(["pending", "in_progress"])
        ).order_by(CharacterMission.queue_position).first()
    
    def get_all(self):
        """Return all missions in the queue in order"""
        return self.db.query(CharacterMission).filter(
            CharacterMission.character_id == self.character_id
        ).order_by(CharacterMission.queue_position).all()
    
    def start_next_mission(self) -> CharacterMission:
        """Start the next pending mission (first in queue)"""
        # Get the first pending mission
        mission = self.db.query(CharacterMission).filter(
            CharacterMission.character_id == self.character_id,
            CharacterMission.status == "pending"
        ).order_by(CharacterMission.queue_position).first()
        
        if mission:
            mission.status = "in_progress"
            self.db.commit()
            self.db.refresh(mission)
        
        return mission