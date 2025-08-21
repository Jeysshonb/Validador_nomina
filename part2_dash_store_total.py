#tiendas
import pandas as pd

def agregar_tiendas_directo(ruta_csv, ruta_excel, ruta_salida):
    """Agrega tiendas SIN JODER los datos originales"""
    print("🔥 MERGE DIRECTO - SIN JODER")
    
    # Leer CSV SIN CAMBIAR TIPOS - FORZAR STRING EN COLUMNAS NUMÉRICAS
    df_csv = pd.read_csv(ruta_csv, encoding='utf-8-sig', 
                        dtype={'numero_de_personal': str, 
                               'numero_id': str,
                               'centro_de_coste': str,
                               'clase_absentpres': str,
                               'dias_presencabs': str,
                               'dias_naturales': str})
    print(f"📖 CSV: {len(df_csv)} registros")
    
    # MOSTRAR TIPOS DE DATOS DEL CSV
    print(f"📊 TIPOS CSV:")
    cols_importantes = ['numero_de_personal', 'numero_id', 'centro_de_coste', 'clase_absentpres']
    for col in cols_importantes:
        if col in df_csv.columns:
            print(f"   {col}: {df_csv[col].dtype} | Muestra: {df_csv[col].head(3).tolist()}")
    
    # Leer Excel
    df_excel = pd.read_excel(ruta_excel)
    print(f"📖 Excel: {len(df_excel)} tiendas")
    
    # MOSTRAR TIPOS DE DATOS DEL EXCEL
    print(f"📊 TIPOS EXCEL:")
    print(f"   myCECO: {df_excel['myCECO'].dtype} | Muestra: {df_excel['myCECO'].head(3).tolist()}")
    
    # Seleccionar solo las columnas que REALMENTE existen y son útiles
    columnas_utiles = ['myCECO']
    ceco_col = 'myCECO'
    
    # Agregar otras columnas útiles que SÍ existen
    cols_disponibles = {
        'Tienda': 'value_tienda',
        'Alias': 'nombre_tienda',          # Cambié de no_tienda a nombre_tienda
        'Region': 'region',
        'Zona': 'zona',
        'Ciudad Corregida': 'nombre_de_la_tienda',
        'Departamento Corregido': 'direccion_laboral'
    }
    
    mapeo = {}
    for col_excel, col_salida in cols_disponibles.items():
        if col_excel in df_excel.columns:
            columnas_utiles.append(col_excel)
            mapeo[col_excel] = col_salida
            print(f"✅ {col_excel} → {col_salida}")
    
    # Preparar datos de tiendas
    df_tiendas = df_excel[columnas_utiles].copy()
    df_tiendas = df_tiendas.rename(columns=mapeo)
    
    # LIMPIAR LA COLUMNA value_tienda QUE TIENE 0 ADICIONAL
    if 'value_tienda' in df_tiendas.columns:
        print(f"🔧 LIMPIANDO value_tienda (quitar SOLO EL ÚLTIMO 0):")
        print(f"   ANTES: {df_tiendas['value_tienda'].head(5).tolist()}")
        
        # Quitar SOLO EL ÚLTIMO 0 si termina en 0
        def quitar_ultimo_cero(valor):
            valor_str = str(valor)
            if valor_str.endswith('0') and len(valor_str) > 1:
                return valor_str[:-1]  # Quitar solo el último carácter
            return valor_str
        
        df_tiendas['value_tienda'] = df_tiendas['value_tienda'].apply(quitar_ultimo_cero)
        
        print(f"   DESPUÉS: {df_tiendas['value_tienda'].head(5).tolist()}")
    
    # MOSTRAR TIPOS DE DATOS DE TIENDAS DESPUÉS DE LIMPIAR
    print(f"📊 TIPOS TIENDAS (después de limpiar):")
    for col in ['value_tienda', 'nombre_tienda']:
        if col in df_tiendas.columns:
            print(f"   {col}: Muestra: {df_tiendas[col].head(3).tolist()}")
    
    # NORMALIZAR TODO PARA QUE COINCIDA PERFECTO - SIN CAMBIAR DATOS ORIGINALES
    def limpiar_numero(serie):
        """Limpia números para que coincidan SIN JODER DATOS ORIGINALES"""
        return (serie.astype(str)
                   .str.replace('.0', '')      # Quitar .0
                   .str.replace(',', '')       # Quitar comas
                   .str.strip()                # Quitar espacios
                   .str.replace('nan', '')     # Quitar nan
                   .replace('', '0'))          # Vacíos = 0
    
    # Normalizar SOLO para el merge
    df_tiendas['ceco_limpio'] = limpiar_numero(df_tiendas[ceco_col])
    df_csv['centro_limpio'] = limpiar_numero(df_csv['centro_de_coste'])
    
    print(f"🔍 Muestras NORMALIZADAS:")
    print(f"   CSV centro: {df_csv['centro_limpio'].head(5).tolist()}")
    print(f"   Excel CECO: {df_tiendas['ceco_limpio'].head(5).tolist()}")
    
    # Verificar coincidencias
    csv_valores = set(df_csv['centro_limpio'].unique())
    excel_valores = set(df_tiendas['ceco_limpio'].unique())
    coincidencias = csv_valores.intersection(excel_valores)
    print(f"🎯 Coincidencias: {len(coincidencias)} de {len(csv_valores)} valores CSV")
    
    # Merge SIMPLE
    df_resultado = pd.merge(
        df_csv,
        df_tiendas.drop(ceco_col, axis=1),
        left_on='centro_limpio',
        right_on='ceco_limpio',
        how='left'
    )
    
    # Quitar columnas temporales
    df_resultado = df_resultado.drop(['centro_limpio', 'ceco_limpio'], axis=1)
    
    # Llenar vacíos
    df_resultado = df_resultado.fillna('')
    
    # VERIFICAR QUE NO SE JODAN LOS DATOS ORIGINALES
    print(f"🔍 VERIFICACIÓN POST-MERGE:")
    cols_verificar = ['numero_de_personal', 'numero_id', 'centro_de_coste']
    for col in cols_verificar:
        if col in df_resultado.columns:
            print(f"   {col} original: {df_csv[col].head(3).tolist()}")
            print(f"   {col} resultado: {df_resultado[col].head(3).tolist()}")
            print(f"   ¿Iguales? {df_csv[col].head(3).tolist() == df_resultado[col].head(3).tolist()}")
    
    # Guardar
    df_resultado.to_csv(ruta_salida, index=False, encoding='utf-8-sig')
    
    # Stats
    nuevas_cols = [col for col in df_resultado.columns if col not in df_csv.columns]
    if nuevas_cols:
        primera = nuevas_cols[0]
        con_data = (df_resultado[primera] != '').sum()
        print(f"📊 Merge exitoso: {con_data}/{len(df_resultado)} ({con_data/len(df_resultado)*100:.1f}%)")
        print(f"📋 Columnas agregadas: {nuevas_cols}")
    
    print(f"✅ LISTO: {ruta_salida}")
    return ruta_salida

# Ejecutar
if __name__ == "__main__":
    csv_validado = r"C:\Users\jjbustos\OneDrive - Grupo Jerónimo Martins\Documents\dash_ausentismos\salidas\validation_report_45.csv"
    excel_tiendas = r"C:\Users\jjbustos\OneDrive - Grupo Jerónimo Martins\Documents\dash_ausentismos\datos_base\0002 Dash Stores.xlsx"
    salida_final = r"C:\Users\jjbustos\OneDrive - Grupo Jerónimo Martins\Documents\dash_ausentismos\salidas\validation_report_45_con_tiendas.csv"
    
    agregar_tiendas_directo(csv_validado, excel_tiendas, salida_final)