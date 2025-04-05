from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models.character import Character
from app.models.character_mission import CharacterMission
from app.schemas.character import Character as CharacterSchema
from app.schemas.character import CharacterCreate, CharacterDetail
from app.schemas.mission import MissionQueueItem

router = APIRouter(
    prefix="/characters",
    tags=["characters"]
)

@router.post("/", response_model=CharacterSchema)
def create_character(character: CharacterCreate, db: Session = Depends(get_db)):
    """Create a new character"""
    db_character = Character(**character.dict())
    db.add(db_character)
    db.commit()
    db.refresh(db_character)
    return db_character

@router.get("/", response_model=List[CharacterSchema])
def get_characters(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Get a list of characters"""
    characters = db.query(Character).offset(skip).limit(limit).all()
    return characters

@router.get("/{character_id}", response_model=CharacterDetail)
def get_character(character_id: int, db: Session = Depends(get_db)):
    """Get a character by ID with mission stats"""
    character = db.query(Character).filter(Character.id == character_id).first()
    if not character:
        raise HTTPException(status_code=404, detail="Character not found")
    
    # Get mission counts for the character details
    result = CharacterDetail.from_orm(character)
    result.mission_count = db.query(CharacterMission).filter(
        CharacterMission.character_id == character_id
    ).count()
    result.pending_missions = db.query(CharacterMission).filter(
        CharacterMission.character_id == character_id,
        CharacterMission.status.in_(["pending", "in_progress"])
    ).count()
    
    return result

@router.get("/{character_id}/missions", response_model=List[MissionQueueItem])
def get_character_missions(character_id: int, db: Session = Depends(get_db)):
    """Get all missions for a character in queue order"""
    character = db.query(Character).filter(Character.id == character_id).first()
    if not character:
        raise HTTPException(status_code=404, detail="Character not found")
    
    # Get all missions with join to get mission details
    missions = db.query(
        CharacterMission.id,
        CharacterMission.status,
        CharacterMission.queue_position,
        CharacterMission.accepted_at,
        Character.id.label("character_id"),
        Character.name.label("character_name"),
        db.model.Mission.id.label("mission_id"),
        db.model.Mission.title,
        db.model.Mission.description,
        db.model.Mission.xp_reward,
        db.model.Mission.difficulty
    ).join(
        db.model.Mission, CharacterMission.mission_id == db.model.Mission.id
    ).filter(
        CharacterMission.character_id == character_id
    ).order_by(CharacterMission.queue_position.asc()).all()
    
    return missions