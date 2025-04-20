from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field

from app.models.vuelo import Vuelo, EstadoVuelo, TipoVuelo
from app.services.vuelo_service import vuelo_service
from app.database.db import get_db

router = APIRouter(prefix="/vuelos", tags=["vuelos"])

# Modelos Pydantic para la API
class VueloBase(BaseModel):
    codigo: str
    aerolinea: str
    origen: str
    destino: str
    hora_programada: datetime
    tipo: TipoVuelo = TipoVuelo.COMERCIAL
    estado: EstadoVuelo = EstadoVuelo.PROGRAMADO
    prioridad: int = Field(default=0, ge=0, le=100)

class VueloCreate(VueloBase):
    pass

class VueloUpdate(BaseModel):
    codigo: Optional[str] = None
    aerolinea: Optional[str] = None
    origen: Optional[str] = None
    destino: Optional[str] = None
    hora_programada: Optional[datetime] = None
    tipo: Optional[TipoVuelo] = None
    estado: Optional[EstadoVuelo] = None
    prioridad: Optional[int] = Field(default=None, ge=0, le=100)

class VueloResponse(VueloBase):
    id: int
    hora_actualizacion: datetime
    
    class Config:
        orm_mode = True

class PositionUpdate(BaseModel):
    posicion: int = Field(..., ge=0, description="Nueva posición en la lista")

# Endpoints
@router.post("/", response_model=VueloResponse, status_code=status.HTTP_201_CREATED)
async def crear_vuelo(vuelo_data: VueloCreate, db: Session = Depends(get_db)):
    """Crea un nuevo vuelo y lo añade a la lista."""
    try:
        # Convertir de modelo Pydantic a objeto Vuelo
        vuelo = Vuelo(
            codigo=vuelo_data.codigo,
            aerolinea=vuelo_data.aerolinea,
            origen=vuelo_data.origen,
            destino=vuelo_data.destino,
            hora_programada=vuelo_data.hora_programada,
            tipo=vuelo_data.tipo,
            estado=vuelo_data.estado,
            prioridad=vuelo_data.prioridad
        )
        
        # Añadir el vuelo usando el servicio
        vuelo_creado = vuelo_service.agregar_vuelo(vuelo, db)
        
        return vuelo_creado
    except Exception as e:
        # Registrar el error para depuración
        print(f"Error al crear vuelo: {str(e)}")
        # Re-lanzar para que FastAPI pueda manejarlo con un mensaje más descriptivo
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al crear vuelo: {str(e)}"
        )

@router.get("/", response_model=List[VueloResponse])
async def obtener_todos_los_vuelos(db: Session = Depends(get_db)):
    """Obtiene todos los vuelos en el orden actual de la lista."""
    try:
        return vuelo_service.obtener_todos_los_vuelos(db)
    except Exception as e:
        print(f"Error al obtener vuelos: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener vuelos: {str(e)}"
        )

@router.get("/proximo", response_model=VueloResponse)
async def obtener_proximo_vuelo(db: Session = Depends(get_db)):
    """Obtiene el próximo vuelo (primero en la lista)."""
    try:
        vuelo = vuelo_service.obtener_proximo_vuelo(db)
        if not vuelo:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No hay vuelos programados"
            )
        return vuelo
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error al obtener próximo vuelo: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener próximo vuelo: {str(e)}"
        )

@router.get("/{vuelo_id}", response_model=VueloResponse)
async def obtener_vuelo_por_id(vuelo_id: int, db: Session = Depends(get_db)):
    """Obtiene un vuelo específico por su ID."""
    try:
        vuelo = vuelo_service.obtener_vuelo_por_id(vuelo_id, db)
        if not vuelo:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Vuelo con ID {vuelo_id} no encontrado"
            )
        return vuelo
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error al obtener vuelo: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener vuelo: {str(e)}"
        )

@router.put("/{vuelo_id}", response_model=VueloResponse)
async def actualizar_vuelo(vuelo_id: int, vuelo_data: VueloUpdate, db: Session = Depends(get_db)):
    """Actualiza un vuelo existente."""
    try:
        # Filtrar campos no nulos
        datos_actualizacion = {k: v for k, v in vuelo_data.dict().items() if v is not None}
        
        vuelo_actualizado = vuelo_service.actualizar_vuelo(vuelo_id, datos_actualizacion, db)
        if not vuelo_actualizado:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Vuelo con ID {vuelo_id} no encontrado"
            )
        
        return vuelo_actualizado
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error al actualizar vuelo: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al actualizar vuelo: {str(e)}"
        )

@router.delete("/{vuelo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def eliminar_vuelo(vuelo_id: int, db: Session = Depends(get_db)):
    """Elimina un vuelo del sistema."""
    try:
        eliminado = vuelo_service.eliminar_vuelo(vuelo_id, db)
        if not eliminado:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Vuelo con ID {vuelo_id} no encontrado"
            )
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error al eliminar vuelo: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al eliminar vuelo: {str(e)}"
        )

@router.post("/{vuelo_id}/emergencia", response_model=VueloResponse)
async def establecer_emergencia(vuelo_id: int, db: Session = Depends(get_db)):
    """Establece un vuelo como emergencia y lo mueve al frente de la lista."""
    try:
        vuelo_actualizado = vuelo_service.establecer_emergencia(vuelo_id, db)
        if not vuelo_actualizado:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Vuelo con ID {vuelo_id} no encontrado"
            )
        
        return vuelo_actualizado
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error al establecer emergencia: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al establecer emergencia: {str(e)}"
        )

@router.post("/{vuelo_id}/posicion", response_model=VueloResponse)
async def mover_a_posicion(vuelo_id: int, posicion_data: PositionUpdate, db: Session = Depends(get_db)):
    """Mueve un vuelo a una posición específica en la lista."""
    try:
        vuelo_movido = vuelo_service.mover_vuelo_a_posicion(vuelo_id, posicion_data.posicion, db)
        if not vuelo_movido:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Vuelo con ID {vuelo_id} no encontrado"
            )
        return vuelo_movido
    except HTTPException as e:
        raise e
    except Exception as e:
        print(f"Error al mover vuelo: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al mover vuelo: {str(e)}"
        )