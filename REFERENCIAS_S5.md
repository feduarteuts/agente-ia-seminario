# Referencias y Recursos — Sesión 5
## Agentes de IA · Seminario · Semana 3, Sesión 5

---

## 🔧 Documentación oficial

| Recurso | URL | Para qué sirve |
|---|---|---|
| FastAPI Tutorial | https://fastapi.tiangolo.com/tutorial/ | Tutorial completo oficial |
| FastAPI — First Steps | https://fastapi.tiangolo.com/tutorial/first-steps/ | Primeros pasos con rutas |
| FastAPI — Request Body | https://fastapi.tiangolo.com/tutorial/body/ | Cómo recibir JSON con Pydantic |
| FastAPI — Path Parameters | https://fastapi.tiangolo.com/tutorial/path-params/ | Parámetros en la URL |
| FastAPI — HTTP Exceptions | https://fastapi.tiangolo.com/tutorial/handling-errors/ | Manejo de errores |
| Uvicorn | https://www.uvicorn.dev/ | Servidor ASGI para FastAPI |
| Pydantic v2 | https://docs.pydantic.dev/latest/ | Validación de datos |
| Postman Docs | https://learning.postman.com/docs/getting-started/introduction/ | Cómo usar Postman |

---

## 📄 Lectura recomendada

### Por qué FastAPI
> **FastAPI — High performance, easy to learn** — Sebastián Ramírez  
> Link: https://fastapi.tiangolo.com/features/  
> **Qué leer**: La página completa de Features — explica por qué FastAPI es mejor que Flask o Django para APIs de IA.

---

## 💡 Comandos rápidos

```bash
# Instalar dependencias
pip install -r requirements.txt

# ── Arrancar el servidor básico (demo) ───────────────
uvicorn 01_fastapi_basico:app --reload --port 8001

# ── Arrancar el servidor completo ────────────────────
uvicorn main:app --reload --port 8000

# ── O directamente con Python ────────────────────────
python main.py

# ── Probar la API desde Python ───────────────────────
# (en otra terminal con el servidor corriendo)
python 02_probar_api.py

# ── Endpoints disponibles ────────────────────────────
GET  /              → info de la API
GET  /health        → estado del servicio
GET  /health/detail → estado detallado
POST /chat          → conversar con el agente
POST /agent         → ejecutar tarea específica
DELETE /chat/{id}   → limpiar sesión
GET  /docs          → Swagger UI
GET  /redoc         → ReDoc
```

---

## 🧠 Glosario — Sesión 5

| Término | Definición simple |
|---|---|
| **FastAPI** | Framework Python para construir APIs REST de forma rápida y con documentación automática |
| **Uvicorn** | Servidor ASGI que ejecuta FastAPI — recibe las peticiones HTTP |
| **Endpoint** | URL específica de la API que responde a un tipo de petición (GET, POST, etc.) |
| **REST** | Estilo de arquitectura para APIs web — usa métodos HTTP y JSON |
| **GET** | Método HTTP para obtener información (no modifica datos) |
| **POST** | Método HTTP para enviar datos y crear/ejecutar algo |
| **DELETE** | Método HTTP para eliminar recursos |
| **JSON** | Formato de datos que usan las APIs para comunicarse |
| **Swagger UI** | Documentación interactiva automática de FastAPI — en /docs |
| **CORS** | Mecanismo que permite a un frontend en otro dominio llamar a la API |
| **Middleware** | Código que se ejecuta antes/después de cada petición |
| **Router** | Agrupa endpoints relacionados en un módulo separado |
| **Async** | Permite manejar múltiples peticiones simultáneas sin bloquear |

---

## 🗂️ Estructura del proyecto

```
sesion5/
├── main.py                 ← Punto de entrada — registra todos los routers
├── s5_llm_factory.py       ← Helper para crear el LLM
├── .env.example            ← Variables de entorno
├── requirements.txt
├── 01_fastapi_basico.py    ← Demo conceptual en un archivo
├── 02_probar_api.py        ← Pruebas desde Python
├── core/
│   └── agent_core.py       ← El agente encapsulado como servicio
├── models/
│   └── schemas.py          ← Modelos Pydantic entrada/salida
└── routes/
    ├── chat.py             ← POST /chat, DELETE /chat/{id}
    ├── agent.py            ← POST /agent
    └── health.py           ← GET /health, GET /health/detail
```

---

*Próxima sesión: Sesión 6 — Despliegue en Railway con CI/CD*
