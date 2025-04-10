from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
from typing import List, Optional, Dict, Any

from app.data_structures.doubly_linked_list import DoublyLinkedList
from app.models.vuelo import Vuelo, EstadoVuelo, TipoVuelo
from app.models.db_models import VueloModel
from app.database.db import get_db

class VueloService:
    """Servicio para gestionar vuelos utilizando la lista doblemente enlazada y la base de datos."""
    
    def __init__(self):
        """Inicializa el servicio con una lista doblemente enlazada vacía."""
        self.lista_vuelos = DoublyLinkedList()
        self._cargar_vuelos_desde_db = False
        
    def _cargar_db_si_necesario(self, db: Session):
        """Carga los vuelos desde la base de datos si no se han cargado todavía."""
        if not self._cargar_vuelos_desde_db:
            # Obtener todos los vuelos y ordenarlos por prioridad (descendente) y hora programada
            vuelos_db = db.query(VueloModel).order_by(
                VueloModel.prioridad.desc(),
                VueloModel.hora_programada
            ).all()
            
            # Limpiar la lista actual
            while not self.lista_vuelos.esta_vacia():
                self.lista_vuelos.eliminar_primero()
            
            # Cargar vuelos en la lista
            for vuelo_db in vuelos_db:
                vuelo = vuelo_db.to_vuelo()
                self.lista_vuelos.insertar_al_final(vuelo)
            
            self._cargar_vuelos_desde_db = True
    
    def agregar_vuelo(self, vuelo: Vuelo, db: Session) -> Vuelo:
        """
        Agrega un nuevo vuelo al sistema.
        Si es una emergencia, se inserta al frente; de lo contrario, al final.
        """
        # Asegurarse de que la lista esté actualizada
        self._cargar_db_si_necesario(db)
        
        # Crear y guardar en la base de datos
        vuelo_db = VueloModel.from_vuelo(vuelo)
        db.add(vuelo_db)
        db.commit()
        db.refresh(vuelo_db)
        
        # Actualizar el ID del vuelo
        vuelo.id = vuelo_db.id
        
        # Insertar en la lista según prioridad/estado
        if vuelo.estado == EstadoVuelo.EMERGENCIA or vuelo.prioridad >= 90:
            self.lista_vuelos.insertar_al_frente(vuelo)
        else:
            self.lista_vuelos.insertar_al_final(vuelo)
        
        return vuelo
    
    def obtener_todos_los_vuelos(self, db: Session) -> List[Vuelo]:
        """Retorna todos los vuelos en el orden actual de la lista."""
        self._cargar_db_si_necesario(db)
        return list(self.lista_vuelos)
    
    def obtener_vuelo_por_id(self, vuelo_id: int, db: Session) -> Optional[Vuelo]:
        """Obtiene un vuelo por su ID."""
        vuelo_db = db.query(VueloModel).filter(VueloModel.id == vuelo_id).first()
        if not vuelo_db:
            return None
        return vuelo_db.to_vuelo()
    
    def obtener_proximo_vuelo(self, db: Session) -> Optional[Vuelo]:
        """Obtiene el próximo vuelo en la lista (el primero)."""
        self._cargar_db_si_necesario(db)
        
        if self.lista_vuelos.esta_vacia():
            return None
        
        return self.lista_vuelos.obtener_primero()
    
    def actualizar_vuelo(self, vuelo_id: int, datos_vuelo: Dict[str, Any], db: Session) -> Optional[Vuelo]:
        """Actualiza un vuelo existente y reordena la lista si es necesario."""
        # Buscar en la base de datos
        vuelo_db = db.query(VueloModel).filter(VueloModel.id == vuelo_id).first()
        if not vuelo_db:
            return None
        
        # Actualizar campos
        for key, value in datos_vuelo.items():
            if hasattr(vuelo_db, key):
                setattr(vuelo_db, key, value)
        
        vuelo_db.hora_actualizacion = datetime.now()
        db.commit()
        db.refresh(vuelo_db)
        
        # Convertir a objeto Vuelo
        vuelo_actualizado = vuelo_db.to_vuelo()
        
        # Reordenar en la lista (eliminar y volver a insertar)
        self._cargar_db_si_necesario(db)
        
        # Buscar y eliminar de la lista actual
        posicion = 0
        for vuelo in self.lista_vuelos:
            if vuelo.id == vuelo_id:
                self.lista_vuelos.extraer_de_posicion(posicion)
                break
            posicion += 1
        
        # Volver a insertar según prioridad/estado
        if vuelo_actualizado.estado == EstadoVuelo.EMERGENCIA or vuelo_actualizado.prioridad >= 90:
            self.lista_vuelos.insertar_al_frente(vuelo_actualizado)
        else:
            self.lista_vuelos.insertar_al_final(vuelo_actualizado)
        
        return vuelo_actualizado
    
    def eliminar_vuelo(self, vuelo_id: int, db: Session) -> bool:
        """Elimina un vuelo del sistema."""
        # Buscar en la base de datos
        vuelo_db = db.query(VueloModel).filter(VueloModel.id == vuelo_id).first()
        if not vuelo_db:
            return False
        
        # Eliminar de la base de datos
        db.delete(vuelo_db)
        db.commit()
        
        # Actualizar la lista
        self._cargar_db_si_necesario(db)
        
        # Buscar y eliminar de la lista
        posicion = 0
        for vuelo in self.lista_vuelos:
            if vuelo.id == vuelo_id:
                self.lista_vuelos.extraer_de_posicion(posicion)
                return True
            posicion += 1
        
        return True
    
    def mover_vuelo_a_posicion(self, vuelo_id: int, nueva_posicion: int, db: Session) -> Optional[Vuelo]:
        """Mueve un vuelo a una posición específica en la lista."""
        self._cargar_db_si_necesario(db)
        
        # Verificar límites
        if nueva_posicion < 0 or nueva_posicion >= self.lista_vuelos.longitud():
            raise HTTPException(status_code=400, detail="Posición fuera de rango")
        
        # Encontrar el vuelo en la lista actual
        vuelo_encontrado = None
        posicion_actual = 0
        
        for vuelo in self.lista_vuelos:
            if vuelo.id == vuelo_id:
                vuelo_encontrado = vuelo
                break
            posicion_actual += 1
        
        if not vuelo_encontrado:
            return None
        
        # Extraer el vuelo de su posición actual
        self.lista_vuelos.extraer_de_posicion(posicion_actual)
        
        # Insertar en la nueva posición
        self.lista_vuelos.insertar_en_posicion(vuelo_encontrado, nueva_posicion)
        
        return vuelo_encontrado
    
    def establecer_emergencia(self, vuelo_id: int, db: Session) -> Optional[Vuelo]:
        """Establece un vuelo como emergencia y lo mueve al frente de la lista."""
        # Buscar en la base de datos
        vuelo_db = db.query(VueloModel).filter(VueloModel.id == vuelo_id).first()
        if not vuelo_db:
            return None
        
        # Actualizar estado y prioridad
        vuelo_db.estado = EstadoVuelo.EMERGENCIA
        vuelo_db.prioridad = 100  # Máxima prioridad
        vuelo_db.hora_actualizacion = datetime.now()
        db.commit()
        db.refresh(vuelo_db)
        
        # Convertir a objeto Vuelo
        vuelo_actualizado = vuelo_db.to_vuelo()
        
        # Reordenar en la lista
        self._cargar_db_si_necesario(db)
        
        # Buscar y eliminar de la lista actual
        posicion = 0
        for vuelo in self.lista_vuelos:
            if vuelo.id == vuelo_id:
                self.lista_vuelos.extraer_de_posicion(posicion)
                break
            posicion += 1
        
        # Insertar al frente
        self.lista_vuelos.insertar_al_frente(vuelo_actualizado)
        
        return vuelo_actualizado

# Instancia global del servicio
vuelo_service = VueloService()