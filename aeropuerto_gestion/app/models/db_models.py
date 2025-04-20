from sqlalchemy import Column, Integer, String, DateTime, Enum, ForeignKey
from datetime import datetime
from app.models.vuelo import EstadoVuelo, TipoVuelo
from app.database.db import Base  # Importar Base desde db.py en lugar de redefinirla

class VueloModel(Base):
    """Modelo SQLAlchemy para la tabla de vuelos."""
    
    __tablename__ = 'vuelos'
    
    id = Column(Integer, primary_key=True)
    codigo = Column(String(20), unique=True, nullable=False)
    aerolinea = Column(String(100), nullable=False)
    origen = Column(String(100), nullable=False)
    destino = Column(String(100), nullable=False)
    hora_programada = Column(DateTime, nullable=False)
    tipo = Column(Enum(TipoVuelo), default=TipoVuelo.COMERCIAL)
    estado = Column(Enum(EstadoVuelo), default=EstadoVuelo.PROGRAMADO)
    prioridad = Column(Integer, default=0)
    hora_actualizacion = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    def to_vuelo(self):
        """Convierte el modelo de base de datos a un objeto Vuelo."""
        from app.models.vuelo import Vuelo
        
        return Vuelo(
            id=self.id,
            codigo=self.codigo,
            aerolinea=self.aerolinea,
            origen=self.origen,
            destino=self.destino,
            hora_programada=self.hora_programada,
            tipo=self.tipo,
            estado=self.estado,
            prioridad=self.prioridad
        )
    
    @classmethod
    def from_vuelo(cls, vuelo):
        """Crea un modelo de base de datos a partir de un objeto Vuelo."""
        return cls(
            id=vuelo.id,
            codigo=vuelo.codigo,
            aerolinea=vuelo.aerolinea,
            origen=vuelo.origen,
            destino=vuelo.destino,
            hora_programada=vuelo.hora_programada,
            tipo=vuelo.tipo,
            estado=vuelo.estado,
            prioridad=vuelo.prioridad,
            hora_actualizacion=vuelo.hora_actualizacion
        )