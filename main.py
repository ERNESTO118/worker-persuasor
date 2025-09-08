import os, json, time
from supabase import create_client
import google.generativeai as genai

def inicializar_servicios():
    supabase = create_client(os.environ.get("SUPABASE_URL"), os.environ.get("SUPABASE_KEY"))
    genai.configure(api_key=os.environ.get("GOOGLE_API_KEY"))
    model_ia = genai.GenerativeModel('gemini-1.5-flash')
    print("✅ Conexiones a Supabase y Google IA establecidas.")
    return supabase, model_ia

def generar_borrador_con_ia(model, nombre_negocio, argumentario):
    prompt = f'Actúa como un copywriter de ventas de élite. Escribe un email corto y empático para "{nombre_negocio}". La idea central del mensaje debe ser este argumentario: "{argumentario}". Termina con una llamada a la acción suave. Redacta solo el cuerpo del email.'
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        print(f"  -> ❌ Error al comunicarse con la IA: {e}")
        return None

def main():
    print("--- INICIO DE MISIÓN DEL PERSUASOR ---")
    supabase, model_ia = inicializar_servicios()

    # Buscamos una campaña en estado 'persuadiendo'
    response_campana = supabase.table('campanas').select('*').eq('estado_campana', 'persuadiendo').limit(1).execute()
    if not response_campana.data:
        print("No hay campañas activas para persuadir.")
        return
    
    campana_actual = response_campana.data[0]
    
    # Recuperamos la "Biblia de Ventas"
    response_arg = supabase.table('argumentarios_venta').select('*').eq('campana_id', campana_actual['id']).execute()
    if not response_arg.data:
        print("❌ No se encontró la 'Biblia de Ventas'. Abortando.")
        return
    
    argumentarios = response_arg.data
    
    # Buscamos prospectos calificados
    response_prospectos = supabase.table('prospectos').select('*').eq('estado_prospecto', 'analizado_calificado').eq('campana_id', campana_actual['id']).limit(5).execute()
    if not response_prospectos.data:
        print("✅ No hay nuevos prospectos calificados para persuadir.")
        # Si no hay más prospectos, marcamos la campaña como completada
        supabase.table('campanas').update({'estado_campana': 'completada'}).eq('id', campana_actual['id']).execute()
        return

    for i, prospecto in enumerate(response_prospectos.data):
        print(f"\n--- Persuadiendo a: {prospecto['nombre_negocio']} ---")
        argumentario_a_usar = argumentarios[i % len(argumentarios)]
        borrador = generar_borrador_con_ia(model_ia, prospecto['nombre_negocio'], argumentario_a_usar['argumentario_solucion'])

        if borrador:
            supabase.table('prospectos').update({'borrador_mensaje': borrador, 'estado_prospecto': 'listo_para_enviar'}).eq('prospecto_id', prospecto['prospecto_id']).execute()
            print(f"  -> ✅ Prospecto actualizado a 'listo_para_enviar'.")
    
    print("\n🎉 ¡MISIÓN DEL PERSUASOR COMPLETADA!")

if __name__ == "__main__":
    while True:
        try:
            main()
        except Exception as e:
            print(f"Ocurrió un error en el ciclo principal del Persuasor: {e}")
        
        print(f"\nPersuasor en modo de espera por 1 hora...")
        time.sleep(3600)
