# app/routers/__init__.py
from app.routers.characters import router as characters_router
from app.routers.missions import router as missions_router

# Reasignar nombres para mayor claridad
router as personajes_router = characters_router
router as misiones_router = missions_router