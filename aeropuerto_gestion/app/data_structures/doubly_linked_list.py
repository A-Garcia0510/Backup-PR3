class DoublyLinkedList:
    """Implementación de una lista doblemente enlazada para gestionar vuelos."""
    
    class _Node:
        """Clase interna para representar un nodo en la lista doblemente enlazada."""
        __slots__ = '_element', '_prev', '_next'
        
        def __init__(self, element, prev=None, next=None):
            self._element = element  # Referencia al vuelo
            self._prev = prev        # Referencia al nodo anterior
            self._next = next        # Referencia al nodo siguiente
    
    def __init__(self):
        """Crea una lista vacía."""
        self._header = self._Node(None)  # Nodo centinela (no contiene elemento)
        self._trailer = self._Node(None) # Nodo centinela (no contiene elemento)
        self._header._next = self._trailer  # El header apunta al trailer
        self._trailer._prev = self._header  # El trailer apunta al header
        self._size = 0  # Número de elementos en la lista
    
    def __len__(self):
        """Retorna el número de elementos en la lista."""
        return self._size
    
    def longitud(self):
        """Retorna el número total de vuelos en la lista."""
        return len(self)
    
    def esta_vacia(self):
        """Retorna True si la lista está vacía."""
        return self._size == 0
    
    def _insertar_entre(self, e, predecessor, successor):
        """Inserta un elemento entre dos nodos existentes."""
        nuevo = self._Node(e, predecessor, successor)  # Crea un nuevo nodo
        predecessor._next = nuevo  # Enlaza el predecesor al nuevo nodo
        successor._prev = nuevo    # Enlaza el sucesor al nuevo nodo
        self._size += 1            # Incrementa el tamaño
        return nuevo
    
    def _eliminar_nodo(self, node):
        """Elimina un nodo de la lista y retorna su elemento."""
        predecessor = node._prev
        successor = node._next
        predecessor._next = successor
        successor._prev = predecessor
        self._size -= 1
        element = node._element    # Guarda el elemento
        node._prev = node._next = node._element = None  # Limpia el nodo
        return element
    
    def insertar_al_frente(self, e):
        """Añade un vuelo al inicio de la lista (para emergencias)."""
        return self._insertar_entre(e, self._header, self._header._next)
    
    def insertar_al_final(self, e):
        """Añade un vuelo al final de la lista (vuelos regulares)."""
        return self._insertar_entre(e, self._trailer._prev, self._trailer)
    
    def obtener_primero(self):
        """Retorna (sin remover) el primer vuelo de la lista."""
        if self.esta_vacia():
            raise Exception("Lista vacía")
        return self._header._next._element
    
    def obtener_ultimo(self):
        """Retorna (sin remover) el último vuelo de la lista."""
        if self.esta_vacia():
            raise Exception("Lista vacía")
        return self._trailer._prev._element
    
    def eliminar_primero(self):
        """Elimina y retorna el primer vuelo de la lista."""
        if self.esta_vacia():
            raise Exception("Lista vacía")
        return self._eliminar_nodo(self._header._next)
    
    def eliminar_ultimo(self):
        """Elimina y retorna el último vuelo de la lista."""
        if self.esta_vacia():
            raise Exception("Lista vacía")
        return self._eliminar_nodo(self._trailer._prev)
    
    def _obtener_nodo_en_posicion(self, posicion):
        """Obtiene el nodo en la posición especificada."""
        if not 0 <= posicion < self._size:
            raise IndexError("Posición fuera de rango")
        
        if posicion < self._size // 2:  # Más cercano al inicio
            current = self._header._next
            for _ in range(posicion):
                current = current._next
        else:  # Más cercano al final
            current = self._trailer._prev
            for _ in range(self._size - 1 - posicion):
                current = current._prev
        
        return current
    
    def insertar_en_posicion(self, e, posicion):
        """Inserta un vuelo en una posición específica."""
        if not 0 <= posicion <= self._size:
            raise IndexError("Posición fuera de rango")
        
        if posicion == 0:
            return self.insertar_al_frente(e)
        elif posicion == self._size:
            return self.insertar_al_final(e)
        else:
            node = self._obtener_nodo_en_posicion(posicion)
            return self._insertar_entre(e, node._prev, node)
    
    def extraer_de_posicion(self, posicion):
        """Remueve y retorna el vuelo en la posición dada."""
        if self.esta_vacia():
            raise Exception("Lista vacía")
        
        if posicion == 0:
            return self.eliminar_primero()
        elif posicion == self._size - 1:
            return self.eliminar_ultimo()
        else:
            node = self._obtener_nodo_en_posicion(posicion)
            return self._eliminar_nodo(node)
    
    def __iter__(self):
        """Iterador para recorrer la lista del principio al final."""
        current = self._header._next
        while current is not self._trailer:
            yield current._element
            current = current._next