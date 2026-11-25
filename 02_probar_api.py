"""
============================================================
  02_probar_api.py — Prueba la API con requests desde Python
  Seminario: Agentes de IA · Sesión 5

  Alternativa a Postman — prueba todos los endpoints
  directamente desde Python.

  IMPORTANTE: el servidor debe estar corriendo antes de
  ejecutar este script.

  Arrancar el servidor en una terminal:
      uvicorn main:app --reload --port 8000

  Luego en otra terminal:
      python 02_probar_api.py

  ✏️ MODIFICA AQUÍ: cambia los mensajes de prueba
============================================================
"""

import requests
import json

# ✏️ MODIFICA AQUÍ: cambia el puerto si usas uno diferente
BASE_URL = "http://localhost:8000"


def separador(titulo):
    print(f"\n{'─'*50}")
    print(f"  {titulo}")
    print('─'*50)


def prueba_get(endpoint, descripcion):
    """Prueba un endpoint GET y muestra el resultado."""
    separador(f"GET {endpoint} — {descripcion}")
    try:
        r = requests.get(f"{BASE_URL}{endpoint}", timeout=10)
        print(f"  Status: {r.status_code}")
        print(f"  Respuesta:")
        print(json.dumps(r.json(), indent=4, ensure_ascii=False))
    except requests.ConnectionError:
        print(f"  ❌ No se puede conectar a {BASE_URL}")
        print(f"     Asegúrate de que el servidor esté corriendo:")
        print(f"     uvicorn main:app --reload --port 8000")
    except Exception as e:
        print(f"  ❌ Error: {e}")


def prueba_post(endpoint, body, descripcion):
    """Prueba un endpoint POST y muestra el resultado."""
    separador(f"POST {endpoint} — {descripcion}")
    try:
        r = requests.post(
            f"{BASE_URL}{endpoint}",
            json=body,
            timeout=30,
        )
        print(f"  Status: {r.status_code}")
        print(f"  Body enviado:")
        print(json.dumps(body, indent=4, ensure_ascii=False))
        print(f"  Respuesta:")
        print(json.dumps(r.json(), indent=4, ensure_ascii=False))
    except requests.ConnectionError:
        print(f"  ❌ No se puede conectar a {BASE_URL}")
    except Exception as e:
        print(f"  ❌ Error: {e}")


def main():
    print(f"\n{'═'*50}")
    print(f"  Pruebas de API — {BASE_URL}")
    print('═'*50)

    # ── GET /  ───────────────────────────────────────────
    prueba_get("/", "Endpoint raíz")

    # ── GET /health ──────────────────────────────────────
    prueba_get("/health", "Estado del servicio")

    # ── GET /health/detail ───────────────────────────────
    prueba_get("/health/detail", "Estado detallado")

    # ── POST /chat ───────────────────────────────────────
    # ✏️ MODIFICA AQUÍ: cambia el mensaje de prueba
    prueba_post("/chat", {
        "mensaje":    "Hola, ¿qué puedes hacer?",
        "session_id": "test_001"
    }, "Primer mensaje de chat")

    # ── POST /chat — pregunta con tool ───────────────────
    # ✏️ MODIFICA AQUÍ: prueba con una pregunta que use herramientas
    prueba_post("/chat", {
        "mensaje":    "¿Cuánto es la raíz cuadrada de 144?",
        "session_id": "test_001"
    }, "Pregunta con herramienta calculadora")

    # ── POST /chat — memoria ─────────────────────────────
    prueba_post("/chat", {
        "mensaje":    "¿Cuál fue mi primera pregunta?",
        "session_id": "test_001"
    }, "Prueba de memoria (misma sesión)")

    # ── POST /agent ──────────────────────────────────────
    # ✏️ MODIFICA AQUÍ: cambia la tarea según tu dominio
    prueba_post("/agent", {
        "tarea":      "Explica en 3 puntos qué es un agente de IA",
        "contexto":   "Para estudiantes universitarios sin experiencia previa",
        "session_id": "test_agente_001"
    }, "Tarea con contexto")

    print(f"\n{'═'*50}")
    print(f"  ✅ Pruebas completadas")
    print(f"  Ver documentación en: {BASE_URL}/docs")
    print('═'*50 + "\n")


if __name__ == "__main__":
    main()
