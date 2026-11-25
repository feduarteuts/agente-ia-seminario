"""
============================================================
  core/agent_core.py — Agente de Soporte Técnico encapsulado
  Seminario: Agentes de IA · Sesión 5
============================================================
"""

import os
import math
import sys
from datetime import datetime
from zoneinfo import ZoneInfo
from dotenv import load_dotenv
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage
from langchain.agents import create_agent
from langchain_community.chat_message_histories import ChatMessageHistory

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from s5_llm_factory import crear_llm

load_dotenv()

# ═══════════════════════════════════════════════════════════
#  SECCIÓN 1 — Identidad y System Prompt de Soporte Técnico
# ═══════════════════════════════════════════════════════════
NOMBRE_AGENTE = os.getenv("AGENT_NAME", "SoporteTI")
ROL_AGENTE = os.getenv(
    "AGENT_ROLE",
    "especialista de soporte técnico en computadoras, programas, impresoras y Windows",
)
ZONA_HORARIA = os.getenv("TZ_DEFAULT", "America/Bogota")

SYSTEM_PROMPT = f"""Eres {NOMBRE_AGENTE}, un {ROL_AGENTE}.
Responde siempre en español, de forma clara, ordenada y práctica.

Metodología de soporte técnico:
1. Diagnostica antes de cambiar configuraciones críticas: prioriza revisar procesos activos, servicios, cola de impresión, red y espacio disponible antes de sugerir reinicios generales o reinstalaciones.
2. Si falta información clave para dar un paso exacto, pide brevemente solo lo necesario (sistema operativo, si es PC o portátil, si el fallo es local o en red, mensaje de error exacto y si ocurrió tras una actualización o cambio).
3. Ordena las soluciones de la prueba más rápida y segura a la más profunda, indicando cómo verificar si funcionó.
4. Advierte con claridad cuando un paso pueda cerrar programas sin guardar o requerir permisos de administrador.
5. Usa tus herramientas cuando necesites la fecha/hora actual, cálculos o una lista de verificación base."""


# ═══════════════════════════════════════════════════════════
#  SECCIÓN 2 — Herramientas
# ═══════════════════════════════════════════════════════════

@tool
def fecha_hora_actual(zona: str = ZONA_HORARIA) -> str:
    """Devuelve la fecha y hora actual para ubicar incidentes, logs o actualizaciones."""
    try:
        return datetime.now(ZoneInfo(zona)).strftime(f"%A %d de %B de %Y, %H:%M en {zona}")
    except Exception:
        return datetime.now().strftime("%A %d de %B de %Y, %H:%M")


@tool
def calculadora(expresion: str) -> str:
    """Calcula expresiones matemáticas (por ejemplo, espacio en disco, MB/GB o cuotas)."""
    try:
        ctx = {k: getattr(math, k) for k in dir(math) if not k.startswith("_")}
        ctx.update({"abs": abs, "round": round})
        return f"{expresion} = {eval(expresion, {'__builtins__': {}}, ctx)}"
    except Exception as e:
        return f"Error en cálculo: {e}"


@tool
def checklist_soporte(categoria: str) -> str:
    """
    Devuelve puntos base de revisión para fallos comunes de soporte técnico.
    Categorías sugeridas: impresora, windows_update, programa, red.
    """
    clave = categoria.strip().lower()
    guias = {
        "impresora": (
            "- Verificar conexión física (USB/Ethernet) o red Wi-Fi y que la impresora esté encendida y sin atascos/alertas en panel.\n"
            "- Revisar si está marcada como 'Sin conexión' o 'Pausada' y limpiar trabajos atorados en la cola.\n"
            "- Verificar puerto/IP asignada (en impresoras de red) y el estado del servicio 'Cola de impresión' (Print Spooler)."
        ),
        "windows_update": (
            "- Comprobar conexión a internet estable y espacio libre suficiente en la unidad del sistema.\n"
            "- Revisar el código de error exacto en Configuración > Windows Update > Historial de actualizaciones.\n"
            "- Ejecutar el solucionador de problemas de Windows Update y verificar servicios relacionados ('wuauserv', 'bits')."
        ),
        "programa": (
            "- Identificar si el fallo es lentitud, congelamiento, cierre inesperado o error al abrir.\n"
            "- Revisar uso de CPU, memoria RAM y disco antes de forzar cierre de procesos.\n"
            "- Validar si el problema ocurre en un archivo específico o en toda la aplicación, y si hay actualizaciones o complementos conflictivos."
        ),
        "red": (
            "- Confirmar si el problema afecta a un solo equipo o a varios en la misma red.\n"
            "- Revisar adaptador activo (Wi-Fi/Ethernet), dirección IP/puerta de enlace y resolución DNS.\n"
            "- Probar conectividad local y externa antes de restablecer la configuración de red."
        ),
    }
    return guias.get(
        clave,
        "Categoría no catalogada; aplica diagnóstico general: reproducir fallo, anotar error exacto, revisar procesos/servicios y validar tras cada paso.",
    )


TOOLS = [fecha_hora_actual, calculadora, checklist_soporte]


# ═══════════════════════════════════════════════════════════
#  CLASE AGENTE — Singleton reutilizable por FastAPI
# ═══════════════════════════════════════════════════════════

class AgentService:
    def __init__(self):
        self._executor = None
        self._historiales: dict[str, ChatMessageHistory] = {}
        self._modelo = os.getenv("GROQ_MODEL", os.getenv("OLLAMA_MODEL", "desconocido"))
        self._proveedor = os.getenv("LLM_PROVIDER", "groq")
        self._inicializar()

    def _inicializar(self):
        try:
            llm = crear_llm()
            self._executor = create_agent(model=llm, tools=TOOLS, system_prompt=SYSTEM_PROMPT)
            print(f"✅ AgentService inicializado — {self._proveedor} / {self._modelo}")
        except Exception as e:
            print(f"❌ Error inicializando AgentService: {e}")
            raise

    def _obtener_historial(self, session_id: str) -> ChatMessageHistory:
        if session_id not in self._historiales:
            self._historiales[session_id] = ChatMessageHistory()
        return self._historiales[session_id]

    def _fecha_actual_texto(self) -> str:
        try:
            return datetime.now(ZoneInfo(ZONA_HORARIA)).strftime("%Y-%m-%d %H:%M")
        except Exception:
            return datetime.now().strftime("%Y-%m-%d %H:%M")

    def chat(self, mensaje: str, session_id: str = "default") -> str:
        historial = self._obtener_historial(session_id)
        mensaje_con_fecha = f"[Fecha actual del sistema: {self._fecha_actual_texto()}]\n{mensaje}"

        try:
            resultado = self._executor.invoke({
                "messages": historial.messages + [HumanMessage(content=mensaje_con_fecha)],
            })
            respuesta = resultado["messages"][-1].content
            historial.add_user_message(mensaje)
            historial.add_ai_message(respuesta)
            return respuesta
        except Exception as e:
            raise RuntimeError(f"Error en el agente: {e}")

    def ejecutar_tarea(self, tarea: str, contexto: str = None, session_id: str = "default") -> str:
        entrada = tarea
        if contexto:
            entrada = f"Contexto: {contexto}\n\nTarea: {tarea}"
        return self.chat(entrada, session_id)

    def limpiar_sesion(self, session_id: str) -> bool:
        if session_id in self._historiales:
            del self._historiales[session_id]
            return True
        return False

    @property
    def nombre(self) -> str:
        return NOMBRE_AGENTE

    @property
    def proveedor(self) -> str:
        return self._proveedor

    @property
    def modelo(self) -> str:
        return self._modelo

    @property
    def herramientas(self) -> list:
        return [t.name for t in TOOLS]


agente_service = AgentService()