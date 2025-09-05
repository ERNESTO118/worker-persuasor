import os
import json
import google.generativeai as genai
from supabase import create_client, Client
import time

# --- 1. CONEXIONES Y CONFIGURACIÓN ---
def inicializar_servicios():
    url_supabase = os.environ.get("SUPABASE_URL")
    key_supabase = os.environ.get("SUPABASE_KEY")
    supabase = create_client(url_supabase, key_supabase)

    google_api_key = os.environ.get("GOOGLE_API_KEY")
    genai.configure(api_key=google_api_key)
    model_ia = genai.GenerativeModel('gemini-1.5-flash')

    print("✅ Conexiones a Supabase y Google IA establecidas.")
    return supabase, model_ia

# --- 2. LA MAGIA: GENERAR EL MENSAJE PERSUASIVO ---
def generar_borrador_con_ia(model, nombre_negocio, argumentario):
    prompt = f"""
    Actúa como un copywriter de ventas de élite. Tu tono es empático, profesional y busca genuinamente ayudar.
    
    Estás escribiendo un borrador de correo electrónico para una empresa llamada "{nombre_negocio}".
    
    El objetivo del correo es iniciar una conversación, no cerrar una venta. Debes usar el siguiente argumentario de venta como la idea central para tu mensaje. Adáptalo para que suene natural en un email corto (menos de 150 palabras).

    ARGUMENTARIO BASE:
    ---
    {argumentario}
    ---

    ESTRUCTURA DEL EMAIL:
    1. Saludo cordial al equipo de "{nombre_negocio}".
    2. Un párrafo corto que conecte con su posible necesidad o dolor, usando la idea del argumentario.
    3. Un segundo párrafo que presente la solución de forma clara y concisa.
    4. Una llamada a la acción suave y de baja fricción, como "¿Tendrían 15 minutos la próxima semana para explorar cómo podríamos aplicar esto a su negocio?".
    
    Redacta solo el cuerpo del correo. No incluyas "Asunto:" ni despedidas como "Saludos cordiales".
    """
    try:
        print("  -> 🧠 Enviando prompt a la IA de Google...")
        response = model.generate_content(prompt)
        print("  -> ✨ Borrador recibido de la IA.")
        return response.text
    except Exception as e:
        print(f"  -> ❌ Error al comunicarse con la IA: {e}")
        return None

# --- EL PUNTO DE ENTRADA: main() ---
def main():
    print("--- INICIO DE MISIÓN DEL TRABAJADOR-PERSUASOR v2.0 ---")
    supabase, model_ia = inicializar_servicios()
    
    ID_CAMPANA_ACTUAL = 1 # Usaremos la campaña de prueba

    # 1. Recuperamos la "Biblia de Ventas" que creó el Analista
    print("\n📚 Cargando la 'Biblia de Ventas' de la campaña...")
    response_arg = supabase.table('argumentarios_venta').select('*').eq('campana_id', ID_CAMPANA_ACTUAL).execute()
    if not response_arg.data:
        print("❌ No se encontró la 'Biblia de Ventas' para esta campaña. El Persuasor no puede trabajar. Misión abortada.")
        return
    
    argumentarios = response_arg.data
    print(f"✅ Se cargaron {len(argumentarios)} argumentarios.")

    # 2. Buscamos prospectos que el Analista ya ha calificado
    print("\n🔍 Buscando prospectos en estado 'analizado_calificado'...")
    response_prospectos = supabase.table('prospectos').select('*').eq('estado_prospecto', 'analizado_calificado').limit(5).execute()

    if not response_prospectos.data:
        print("✅ No hay nuevos prospectos calificados para persuadir. Misión completada.")
        return

    prospectos_a_persuadir = response_prospectos.data
    
    # 3. Para cada prospecto, elegimos un argumentario y generamos el mensaje
    for i, prospecto in enumerate(prospectos_a_persuadir):
        print(f"\n--- Persuadiendo a: {prospecto['nombre_negocio']} ---")
        
        # Estrategia simple: rotamos los argumentarios para variar los mensajes
        argumentario_a_usar = argumentarios[i % len(argumentarios)]
        print(f"  -> Usando el argumentario para el dolor: {argumentario_a_usar['dolor_clave']}")

        borrador = generar_borrador_con_ia(model_ia, prospecto['nombre_negocio'], argumentario_a_usar['argumentario_solucion'])

        if borrador:
            supabase.table('prospectos').update({
                'borrador_mensaje': borrador,
                'estado_prospecto': 'listo_para_enviar'
            }).eq('prospecto_id', prospecto['prospecto_id']).execute()
            print(f"  -> ✅ Prospecto actualizado a 'listo_para_enviar'.")
        
        time.sleep(1)

    print("\n🎉 ¡MISIÓN DEL PERSUASOR COMPLETADA!")

if __name__ == "__main__":
    main()
# --- Ejecutamos la función principal en un bucle infinito ---
if __name__ == "__main__":
    while True:
        try:
            main()
        except Exception as e:
            print(f"Ocurrió un error en el ciclo principal: {e}")
        
        # El trabajador se "duerme" por 1 hora antes de volver a buscar trabajo.
        # En el futuro, el Orquestador lo despertará directamente.
        print("\nAnalista en modo de espera por 1 hora...")
        time.sleep(3600)
