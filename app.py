import os
import litellm
from dotenv import load_dotenv
from crewai import Agent, Task, Crew, Process, LLM
from langchain_community.tools import DuckDuckGoSearchRun
from crewai.tools import tool

# ======================================================================
# EL PARCHE NINJA
# ======================================================================
_funcion_original = litellm.completion

def filtro_limpiador(*args, **kwargs):
    if 'messages' in kwargs:
        for mensaje in kwargs['messages']:
            if 'cache_breakpoint' in mensaje:
                del mensaje['cache_breakpoint']
    return _funcion_original(*args, **kwargs)

litellm.completion = filtro_limpiador
# ======================================================================

load_dotenv()

llm_blindado = LLM(
    model="groq/llama-3.1-8b-instant",
    api_key=os.getenv("GROQ_API_KEY"),
    temperature=0.7
)

@tool("Buscador Web DuckDuckGo")
def buscador_web(query: str) -> str:
    """Busca información en internet sobre negocios locales y tendencias."""
    search = DuckDuckGoSearchRun()
    return search.run(query)

# ---------------------------------------------------------
# CARGAR EL ADN DE DISEÑO PREMIUM
# ---------------------------------------------------------
try:
    with open("plantilla_maestra.html", "r", encoding="utf-8") as file:
        plantilla_premium = file.read()
except FileNotFoundError:
    print("⚠️ No se encontró 'plantilla_maestra.html'. El agente usará su diseño por defecto.")
    plantilla_premium = "Crea un diseño web moderno y elegante."

# ---------------------------------------------------------
# EL EQUIPO DE AGENTES
# ---------------------------------------------------------

prospector = Agent(
    role='Especialista en Extracción de Datos y Prospección',
    goal='Buscar en internet negocios locales reales en una ciudad específica y recopilar su información básica.',
    backstory='Eres un sabueso digital. Sabes usar motores de búsqueda para encontrar empresas locales que necesitan modernizarse. Extraes nombres reales y a qué se dedican.',
    verbose=True,
    allow_delegation=False,
    tools=[buscador_web],
    llm=llm_blindado
)

investigador_comercial = Agent(
    role='Especialista en Prospección y Ventas B2B', 
    goal='Diseñar una propuesta de valor basada en los datos reales encontrados por el Prospector.', 
    backstory='Eres un experto en marketing digital. Tomas la información de un negocio real y redactas un correo de venta irresistible.', 
    verbose=True,                                  
    allow_delegation=False,
    llm=llm_blindado  
)

desarrollador_web = Agent(
    role='Desarrollador Web Frontend Senior',
    goal='Clonar de manera exacta la estructura y estilos visuales de una plantilla premium y adaptarla al nuevo cliente.',
    backstory='Eres un desarrollador de élite especializado en crear interfaces de altísima conversión, dominando variables CSS, glassmorfismo y animaciones.',
    verbose=True,
    allow_delegation=False,
    llm=llm_blindado
)

# ---------------------------------------------------------
# LAS TAREAS (Transferencia de Estilo)
# ---------------------------------------------------------

def crear_flujo_agencia(nicho, ciudad):
    tarea_busqueda = Task(
        description=f'''Busca en internet 1 negocio real del nicho "{nicho}" en la ciudad de "{ciudad}". 
        Extrae su nombre real, a qué se dedican exactamente y si logras ver algún detalle sobre ellos. 
        Si no encuentras uno específico rápido, simula uno altamente realista basado en los resultados de búsqueda.''',
        expected_output='El nombre de un negocio real y una breve descripción de sus servicios.',
        agent=prospector
    )

    tarea_venta = Task(
        description='''Toma el nombre y descripción del negocio que acaba de encontrar el Prospector.
        Genera un correo corto ofreciendo la creación de una Landing Page moderna. Habla en términos de beneficio para ese negocio en específico.''',
        expected_output='Un correo electrónico listo para enviar.',
        agent=investigador_comercial
    )

    tarea_codigo = Task(
        description=f'''Basándote en el negocio encontrado y la propuesta de ventas, crea la Landing Page.
        
        AQUÍ ESTÁ TU MANUAL DE DISEÑO OBLIGATORIO (Plantilla Premium):
        {plantilla_premium}
        
        REGLAS DE CLONACIÓN:
        1. Mantén INTACTA toda la etiqueta <style> de la plantilla. No borres el código del glassmorfismo, ni las animaciones.
        2. Mantén INTACTOS los scripts de la parte inferior de la plantilla (Notificaciones toast, cursores, observadores de scroll).
        3. REEMPLAZA ÚNICAMENTE el texto, los servicios, los testimonios y los datos de contacto del HTML para que pertenezcan EXCLUSIVAMENTE al negocio que encontró el prospector.
        4. Devuelve ÚNICAMENTE el código HTML puro, sin texto introductorio ni comentarios extra.''',
        expected_output='Código HTML5 premium adaptado al nuevo cliente.',
        agent=desarrollador_web
    )
    
    return [tarea_busqueda, tarea_venta, tarea_codigo]

# ---------------------------------------------------------
# EJECUCIÓN DEL SISTEMA
# ---------------------------------------------------------
if __name__ == "__main__":
    print("🌐 Iniciando Motor Autónomo con clonación de diseño Premium...")
    
    nicho_buscar = "Clínicas Odontológicas"
    ciudad_buscar = "Barquisimeto"
    
    tareas = crear_flujo_agencia(nicho_buscar, ciudad_buscar)
    
    crew = Crew(
        agents=[prospector, investigador_comercial, desarrollador_web],           
        tasks=tareas,                             
        process=Process.sequential
    )
    
    resultado = crew.kickoff()
    
    print("\n================ GUARDANDO ARCHIVOS ================\n")
    
    codigo_crudo = str(tareas[2].output.raw)
    codigo_limpio = codigo_crudo.replace("```html", "").replace("```", "").strip()
    
    correo_texto = str(tareas[1].output.raw)
    
    if not os.path.exists("cliente_nuevo"):
        os.makedirs("cliente_nuevo")
        
    with open("cliente_nuevo/index.html", "w", encoding="utf-8") as f:
        f.write(codigo_limpio)
        
    with open("cliente_nuevo/correo_venta.txt", "w", encoding="utf-8") as f:
        f.write(correo_texto)
        
    print("✅ ¡Éxito! Revisa la carpeta 'cliente_nuevo'. Abre el nuevo index.html para ver la magia de la transferencia de estilo.")