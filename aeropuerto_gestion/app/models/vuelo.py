from enum import Enum
from datetime import datetime
from typing import Optional

class EstadoVuelo(str, Enum):
    """Enumeración para representar los posibles estados de un vuelo."""
    PROGRAMADO = "PROGRAMADO"
    EN_PISTA = "EN_PISTA"
    DESPEGANDO = "DESPEGANDO"
    EN_VUELO = "EN_VUELO"
    ATERRIZANDO = "ATERRIZANDO"
    FINALIZADO = "FINALIZADO"
    RETRASADO = "RETRASADO"
    CANCELADO = "CANCELADO"
    EMERGENCIA = "EMERGENCIA"

class TipoVuelo(str, Enum):
    """Enumeración para representar los tipos de vuelo."""
    COMERCIAL = "COMERCIAL"
    PRIVADO = "PRIVADO"
    CARGA = "CARGA"
    MILITAR = "MILITAR"
    EMERGENCIA_MEDICA = "EMERGENCIA_MEDICA"

class Vuelo:
    """Clase para representar un vuelo en el sistema."""
    
    def __init__(self, 
                 codigo: str, 
                 aerolinea: str, 
                 origen: str, 
                 destino: str, 
                 hora_programada: datetime,
                 tipo: TipoVuelo = TipoVuelo.COMERCIAL,
                 estado: EstadoVuelo = EstadoVuelo.PROGRAMADO,
                 prioridad: int = 0,
                 id: Optional[int] = None):
        """
        Inicializa un nuevo vuelo.
        
        Args:
            codigo: Código único del vuelo (ej: IB6830)
            aerolinea: Nombre de la aerolínea
            origen: Aeropuerto de origen
            destino: Aeropuerto de destino
            hora_programada: Hora programada de despegue o aterrizaje
            tipo: Tipo de vuelo (comercial, privado, etc.)
            estado: Estado actual del vuelo
            prioridad: Nivel de prioridad (mayor número = mayor prioridad)
            id: Identificador único en la base de datos (opcional)
        """
        self.id = id
        self.codigo = codigo
        self.aerolinea = aerolinea
        self.origen = origen
        self.destino = destino
        self.hora_programada = hora_programada
        self.tipo = tipo
        self.estado = estado
        self.prioridad = prioridad
        self.hora_actualizacion = datetime.now()
    
    def __repr__(self):
        """Representación en string del vuelo."""
        return f"Vuelo({self.codigo}, {self.aerolinea}, {self.origen}->{self.destino}, {self.estado})"
    
    def establecer_emergencia(self):
        """Establece el vuelo en estado de emergencia con máxima prioridad."""
        self.estado = EstadoVuelo.EMERGENCIA
        self.prioridad = 100  # Máxima prioridad
        self.hora_actualizacion = datetime.now()
        return self
    
    def actualizar_estado(self, nuevo_estado: EstadoVuelo):
        """Actualiza el estado del vuelo."""
        self.estado = nuevo_estado
        self.hora_actualizacion = datetime.now()
        return self
    
    def actualizar_prioridad(self, nueva_prioridad: int):
        """Actualiza la prioridad del vuelo."""
        self.prioridad = nueva_prioridad
        self.hora_actualizacion = datetime.now()
        return self