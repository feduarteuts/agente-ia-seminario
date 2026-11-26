"""
============================================================
  main.py — Servidor FastAPI principal
  Seminario: Agentes de IA · Sesión 5

  Punto de entrada de la aplicación.
  Registra todos los routers y configura la API.

  Arrancar el servidor:
      uvicorn main:app --reload --port 8000

  Ver documentación Swagger:
      http://localhost:8000/docs

  Ver documentación ReDoc:
      http://localhost:8000/redoc

  Ver interfaz web de soporte:
      http://localhost:8000/soporte
============================================================
"""

import os
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from routes.chat import router as chat_router
from routes.agent import router as agent_router
from routes.health import router as health_router
from routes.excel import router as excel_router

load_dotenv()

# ═══════════════════════════════════════════════════════════
#  Metadata de la API
# ═══════════════════════════════════════════════════════════
NOMBRE_AGENTE = os.getenv("AGENT_NAME", "SoporteTI")
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "static")

app = FastAPI(
    title=f"API — {NOMBRE_AGENTE}",
    description=f"""
## Agente Inteligente: {NOMBRE_AGENTE}

API REST para interactuar con el agente de soporte técnico construido durante el seminario.

### Endpoints disponibles:
- **POST /chat** — Conversar con el agente (con memoria por sesión)
- **POST /agent** — Ejecutar tareas específicas con contexto
- **GET /health** — Verificar estado del servicio
- **GET /health/detail** — Estado detallado con herramientas
- **GET /soporte** — Interfaz web de soporte técnico

### Documentación:
- Swagger UI: `/docs`
- ReDoc: `/redoc`
    """,
    version="1.0.0",
    contact={
        "name": "Seminario Agentes IA",
        "email": "tu@email.com",
    },
    license_info={
        "name": "MIT",
    },
)

# ═══════════════════════════════════════════════════════════
#  CORS — permite que frontends externos llamen a la API
# ═══════════════════════════════════════════════════════════
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ═══════════════════════════════════════════════════════════
#  ARCHIVOS ESTÁTICOS E INTERFAZ WEB
# ═══════════════════════════════════════════════════════════
if os.path.isdir(STATIC_DIR):
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.get("/soporte", tags=["Interfaz"])
async def pagina_soporte():
    """GET /soporte — interfaz web para chatear con el agente de soporte"""
    ruta_html = os.path.join(STATIC_DIR, "index.html")
    if not os.path.isfile(ruta_html):
        return {
            "error": "No se encontró static/index.html",
            "ruta_esperada": ruta_html,
        }
    return FileResponse(ruta_html)


# ═══════════════════════════════════════════════════════════
#  ROUTERS — registra todos los endpoints
# ═══════════════════════════════════════════════════════════
app.include_router(health_router, tags=["Monitoreo"])
app.include_router(chat_router, tags=["Chat"])
app.include_router(agent_router, tags=["Agente"])
app.include_router(excel_router)


# ═══════════════════════════════════════════════════════════
#  ENDPOINT RAÍZ
# ═══════════════════════════════════════════════════════════
@app.get("/", tags=["Info"])
async def root():
    """GET / — información básica de la API"""
    return {
        "api": f"Agente IA — {NOMBRE_AGENTE}",
        "version": "1.0.0",
        "soporte": "/soporte",
        "docs": "/docs",
        "health": "/health",
    }


# ═══════════════════════════════════════════════════════════
#  ARRANQUE DIRECTO
#  Ejecuta con:  python main.py
#  O con:        uvicorn main:app --reload
# ═══════════════════════════════════════════════════════════
if __name__ == "__main__":
    import uvicorn

    host = os.getenv("API_HOST", "0.0.0.0")
    port = int(os.getenv("API_PORT", "8000"))
    debug = os.getenv("API_DEBUG", "True").lower() == "true"

    print(f"\n{'─' * 50}")
    print("  🚀 Servidor arrancando...")
    print(f"  Agente:  {NOMBRE_AGENTE}")
    print(f"  URL:     http://localhost:{port}")
    print(f"  Soporte: http://localhost:{port}/soporte")
    print(f"  Docs:    http://localhost:{port}/docs")
    print(f"{'─' * 50}\n")

    uvicorn.run("main:app", host=host, port=port, reload=debug)