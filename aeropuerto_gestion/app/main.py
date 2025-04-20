from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# Importaciones de base de datos
from app.database.db import Base, engine

# Importar explícitamente todos los modelos antes de crear las tablas
from app.models.db_models import VueloModel

# Importaciones de rutas
from app.api.vuelos import router as vuelos_router

# Crear las tablas en la base de datos
Base.metadata.create_all(bind=engine)

# Crear la aplicación FastAPI
app = FastAPI(
    title="Sistema de Gestión de Vuelos",
    description="API para gestionar vuelos en un aeropuerto utilizando una lista doblemente enlazada",
    version="1.0.0",
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permite todas las origins en desarrollo
    allow_credentials=True,
    allow_methods=["*"],  # Permite todos los métodos
    allow_headers=["*"],  # Permite todos los headers
)

# Incluir los routers
app.include_router(vuelos_router)

# Ruta principal
@app.get("/")
async def root():
    return {
        "mensaje": "Bienvenido al Sistema de Gestión de Vuelos",
        "documentacion": "/docs",
    }

if __name__ == "__main__":
    # Verificar las tablas creadas (ayuda para depuración)
    from sqlalchemy import inspect
    inspector = inspect(engine)
    print("Tablas creadas en la base de datos:")
    for table_name in inspector.get_table_names():
        print(f"- {table_name}")
    
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)