from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from sqlalchemy import create_engine
from app.api.vuelos import router as vuelos_router
from app.database.db import Base, engine

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
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)