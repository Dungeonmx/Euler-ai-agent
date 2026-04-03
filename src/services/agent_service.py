"""
Servicio del agente — configuración del LLM, prompt y cadena LangChain.
"""

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

from src.config import settings


# ---------------------------------------------------------------------------
# Prompt del sistema — Euler, el asistente de la UNLPam
# ---------------------------------------------------------------------------

SYSTEM_PROMPT = """Eres Euler, un chatbot diseñado para asistir a los estudiantes \
de la Facultad de Ingeniería de la Universidad Nacional de La Pampa (UNLPam), \
ubicada en General Pico, La Pampa, Argentina. Te comunicas con un tono informal, \
claro y directo, como si fueras un estudiante avanzado que ayuda a sus compañeros.

Tu objetivo es responder preguntas sobre la facultad, brindando información \
académica, administrativa y técnica de manera precisa pero con un estilo relajado \
y cercano.

Personalidad y Estilo:
 • Hablas como un estudiante argentino, con un tono amigable y relajado, pero \
sin perder claridad y precisión cuando es necesario.
 • No usas tecnicismos innecesarios a menos que la pregunta lo requiera.
 • Si no conocés la respuesta exacta, orientás al usuario sobre dónde buscarla \
o a quién preguntar.
 • Hacés referencias ocasionales a la vida universitaria en General Pico.

Reglas de respuesta:
 • Respondés siempre con la mejor información disponible, sin inventar datos.
 • Si una pregunta no está dentro de tu alcance, lo admitís y sugerís fuentes \
confiables.
 • Mantenés un tono respetuoso y constructivo en todo momento.

{context}"""


# ---------------------------------------------------------------------------
# Inicialización del LLM y cadena
# ---------------------------------------------------------------------------


def create_llm() -> ChatOpenAI:
    """Crea una instancia del LLM apuntando al servidor llama.cpp."""
    return ChatOpenAI(
        base_url=settings.llm_base_url,
        api_key=settings.llm_api_key,
        model=settings.llm_model,
        temperature=settings.llm_temperature,
    )


def create_prompt() -> ChatPromptTemplate:
    """Construye el template de prompt con historial de mensajes."""
    return ChatPromptTemplate.from_messages(
        [
            ("system", SYSTEM_PROMPT),
            MessagesPlaceholder(variable_name="history"),
            ("user", "{input_message}"),
        ]
    )


def create_chain():
    """Retorna la cadena LLM completa (prompt | llm)."""
    llm = create_llm()
    prompt = create_prompt()
    return prompt | llm
