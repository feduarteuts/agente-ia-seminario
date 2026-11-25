"""
============================================================
  01_fastapi_basico.py — FastAPI desde cero en un archivo
  Seminario: Agentes de IA · Sesión 5

  Antes de ver la estructura completa del proyecto,
  este archivo muestra FastAPI en su forma más simple:
  todo en un solo archivo, sin carpetas ni imports.

  Objetivo: entender los conceptos base de FastAPI
  antes de ver la arquitectura completa.

  Arrancar:
      uvicorn 01_fastapi_basico:app --reload --port 8001

  Ver docs:
      http://localhost:8001/docs

  ✏️ Experimenta modificando las rutas y los modelos.
============================================================
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

# ─────────────────────────────────────────────────────────
#  PASO 1 — Crear la aplicación
#  ✏️ MODIFICA AQUÍ: cambia el título y descripción
# ─────────────────────────────────────────────────────────
app = FastAPI(
    title="Mi Primera API con FastAPI",
    description="API de ejemplo para aprender los conceptos básicos",
    version="1.0.0",
)


# ─────────────────────────────────────────────────────────
#  PASO 2 — Definir modelos Pydantic
#  FastAPI los usa para validar y documentar automáticamente
#  ✏️ MODIFICA AQUÍ: agrega o cambia campos
# ─────────────────────────────────────────────────────────
class MensajeRequest(BaseModel):
    texto:  str           = Field(..., description="Texto del mensaje", min_length=1)
    nombre: Optional[str] = Field(default="Anónimo", description="Nombre del remitente")

    class Config:
        json_schema_extra = {
            "example": {"texto": "Hola, ¿cómo estás?", "nombre": "César"}
        }


class MensajeResponse(BaseModel):
    respuesta:  str      = Field(..., description="Respuesta del servidor")
    recibido_de:str      = Field(..., description="Nombre del remitente")
    timestamp:  datetime = Field(default_factory=datetime.now)


# ─────────────────────────────────────────────────────────
#  PASO 3 — Definir endpoints
#  Cada endpoint es una función Python con un decorador
# ─────────────────────────────────────────────────────────

# GET /  — endpoint raíz, devuelve info básica
@app.get("/", tags=["Info"])
async def raiz():
    """Endpoint raíz — información de la API"""
    return {"mensaje": "API funcionando", "docs": "/docs"}


# GET /health — endpoint de monitoreo
@app.get("/health", tags=["Monitoreo"])
async def health():
    """Verificar que el servidor está vivo"""
    return {"status": "ok", "timestamp": datetime.now()}


# POST /echo — recibe un mensaje y lo devuelve transformado
@app.post("/echo", response_model=MensajeResponse, tags=["Demo"])
async def echo(request: MensajeRequest):
    """
    Recibe un mensaje y lo devuelve en mayúsculas.
    Demo de validación automática con Pydantic.
    """
    return MensajeResponse(
        # ✏️ MODIFICA AQUÍ: cambia la transformación del mensaje
        respuesta=f"Recibí tu mensaje: '{request.texto.upper()}'",
        recibido_de=request.nombre,
    )


# GET /items/{item_id} — parámetro en la URL
@app.get("/items/{item_id}", tags=["Demo"])
async def obtener_item(item_id: int, categoria: Optional[str] = None):
    """
    Ejemplo de parámetro de ruta y query parameter.
    URL: /items/42?categoria=electronicos
    """
    if item_id <= 0:
        # ✏️ Así se lanza un error HTTP en FastAPI
        raise HTTPException(status_code=400, detail="El ID debe ser positivo")
    return {
        "item_id":   item_id,
        "categoria": categoria or "sin categoría",
        "mensaje":   f"Item {item_id} encontrado",
    }


# ─────────────────────────────────────────────────────────
#  ARRANQUE DIRECTO
# ─────────────────────────────────────────────────────────
if __name__ == "__main__":
    import uvicorn
    print("\n  🚀 Servidor básico en: http://localhost:8001")
    print("  📖 Docs Swagger en:   http://localhost:8001/docs\n")
    uvicorn.run("01_fastapi_basico:app", host="0.0.0.0", port=8001, reload=True)
