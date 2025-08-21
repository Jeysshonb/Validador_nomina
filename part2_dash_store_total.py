#tiendas_modificado
import pandas as pd

def agregar_tiendas_modificado(ruta_csv, ruta_excel, ruta_salida):
    """Agrega tiendas SIN JODER los datos originales - VERSIÓN MODIFICADA"""
    print("🔥 MERGE DIRECTO - SIN JODER (MODIFICADO)")
    
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
    
    # COLUMNAS MODIFICADAS - SOLO LAS QUE NECESITAMOS
    columnas_utiles = ['myCECO']
    ceco_col = 'myCECO'
    
    # SOLO agregar Tienda y Alias (NO region, zona, etc.)
    cols_disponibles = {
        'Tienda': 'value_tienda',
        'Alias': 'nombre_tienda'          # Solo estas dos columnas
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
    
    # 🎯 NUEVA LÓGICA: Mover descripcion1 a nombre_tienda y eliminar descripcion1
    print(f"\n🔧 MOVIENDO descripcion1 → nombre_tienda Y ELIMINANDO descripcion1:")
    
    if 'nombre_tienda' in df_resultado.columns and 'descripcion1' in df_resultado.columns:
        # Contar datos en descripcion1
        datos_desc = (df_resultado['descripcion1'] != '').sum()
        print(f"   📊 Registros con descripcion1: {datos_desc:,}")
        
        # Contar nombre_tienda vacíos
        nombre_vacios_antes = (df_resultado['nombre_tienda'] == '').sum()
        print(f"   📊 nombre_tienda vacíos ANTES: {nombre_vacios_antes:,}")
        
        # MOVER: Solo llenar nombre_tienda vacío con descripcion1
        mask_nombre_vacio = (df_resultado['nombre_tienda'] == '') | (df_resultado['nombre_tienda'].isna())
        mask_desc_lleno = (df_resultado['descripcion1'] != '') & (df_resultado['descripcion1'].notna())
        
        # Aplicar solo donde nombre_tienda está vacío Y descripcion1 tiene datos
        mask_mover = mask_nombre_vacio & mask_desc_lleno
        
        if mask_mover.any():
            df_resultado.loc[mask_mover, 'nombre_tienda'] = df_resultado.loc[mask_mover, 'descripcion1']
            movidos = mask_mover.sum()
            print(f"   ✅ Registros movidos: {movidos:,}")
            
            # Mostrar ejemplos de lo que se movió
            ejemplos = df_resultado[mask_mover][['centro_de_coste', 'nombre_tienda']].head(3)
            print(f"   🔍 Ejemplos de datos movidos:")
            for i, (_, row) in enumerate(ejemplos.iterrows()):
                print(f"      {i+1}. Centro: {row['centro_de_coste']} → nombre_tienda: '{row['nombre_tienda']}'")
        
        # ELIMINAR la columna descripcion1
        df_resultado = df_resultado.drop('descripcion1', axis=1)
        print(f"   🗑️ Columna 'descripcion1' ELIMINADA")
        
        # Verificar resultado final
        nombre_vacios_despues = (df_resultado['nombre_tienda'] == '').sum()
        print(f"   📊 nombre_tienda vacíos DESPUÉS: {nombre_vacios_despues:,}")
        
    else:
        print(f"   ⚠️ No se encontraron las columnas necesarias")
        if 'nombre_tienda' not in df_resultado.columns:
            print(f"      ❌ Falta: nombre_tienda")
        if 'descripcion1' not in df_resultado.columns:
            print(f"      ❌ Falta: descripcion1")
    
    # Llenar otros vacíos
    df_resultado = df_resultado.fillna('')
    
    # 🎯 REORDENAR COLUMNAS SEGÚN EL ORDEN ESPECIFICADO
    print(f"\n📋 REORDENANDO COLUMNAS...")
    
    orden_deseado = [
        'numero_de_personal', 'nombre_emplcand', 'descripcion', 'numero_id', 
        'clase_absentpres', 'txtclpresab', 'clase_absentpres1', 'txtclpresab1', 
        'descripcenfermedad', 'descripcenfermedad1', 'inicio_de_validez', 'fin_de_validez', 
        'modificado_el', 'modificado_por', 'division_de_personal', 'texto_division_pers', 
        'dias_presencabs', 'dias_naturales', 'final_salario_enfer', 'area_de_personal', 
        'texto_subdivpers', 'centro_de_coste', 'nombre_tienda', 'sexo', 
        'denominacion_funcion', 'id_entidad_de_seguridad_social', 'subtipo', 
        'area_de_nomina', 'estado_empleado', 'value_tienda'
    ]
    
    # Verificar qué columnas existen
    columnas_existentes = []
    columnas_faltantes = []
    
    for col in orden_deseado:
        if col in df_resultado.columns:
            columnas_existentes.append(col)
        else:
            columnas_faltantes.append(col)
    
    # Agregar columnas adicionales que no están en el orden (por si acaso)
    columnas_adicionales = [col for col in df_resultado.columns if col not in orden_deseado]
    
    # Reordenar
    columnas_finales = columnas_existentes + columnas_adicionales
    df_resultado = df_resultado[columnas_finales]
    
    print(f"   ✅ Columnas ordenadas: {len(columnas_existentes)}")
    if columnas_faltantes:
        print(f"   ⚠️ Columnas faltantes: {len(columnas_faltantes)} → {columnas_faltantes[:5]}...")
    if columnas_adicionales:
        print(f"   📋 Columnas adicionales al final: {columnas_adicionales}")
    
    print(f"   🎯 Orden final verificado: nombre_tienda en posición {columnas_finales.index('nombre_tienda') + 1}")
    print(f"   🎯 Orden final verificado: value_tienda en posición {columnas_finales.index('value_tienda') + 1}")
    
    # VERIFICAR QUE NO SE JODAN LOS DATOS ORIGINALES
    print(f"\n🔍 VERIFICACIÓN POST-MERGE:")
    cols_verificar = ['numero_de_personal', 'numero_id', 'centro_de_coste']
    for col in cols_verificar:
        if col in df_resultado.columns:
            print(f"   {col} original: {df_csv[col].head(3).tolist()}")
            print(f"   {col} resultado: {df_resultado[col].head(3).tolist()}")
            iguales = df_csv[col].head(3).tolist() == df_resultado[col].head(3).tolist()
            print(f"   ¿Iguales? {iguales}")
    
    # Guardar
    print(f"\n💾 GUARDANDO: {ruta_salida}")
    df_resultado.to_csv(ruta_salida, index=False, encoding='utf-8-sig')
    
    # Stats finales
    nuevas_cols = [col for col in df_resultado.columns if col not in df_csv.columns]
    print(f"\n📊 ESTADÍSTICAS FINALES:")
    print(f"   📁 Registros totales: {len(df_resultado):,}")
    
    if nuevas_cols:
        print(f"   📋 Columnas agregadas: {nuevas_cols}")
        
        # Estadísticas de value_tienda
        if 'value_tienda' in nuevas_cols:
            con_value = (df_resultado['value_tienda'] != '').sum()
            print(f"   🏪 Con value_tienda: {con_value:,}/{len(df_resultado):,} ({con_value/len(df_resultado)*100:.1f}%)")
        
        # Estadísticas de nombre_tienda
        if 'nombre_tienda' in nuevas_cols:
            con_nombre = (df_resultado['nombre_tienda'] != '').sum()
            print(f"   🏷️ Con nombre_tienda: {con_nombre:,}/{len(df_resultado):,} ({con_nombre/len(df_resultado)*100:.1f}%)")
    
    # Verificar que descripcion1 fue eliminada
    if 'descripcion1' in df_resultado.columns:
        print(f"   ⚠️ ADVERTENCIA: descripcion1 AÚN existe (no se eliminó)")
    else:
        print(f"   ✅ descripcion1 eliminada correctamente")
    
    print(f"✅ COMPLETADO: {ruta_salida}")
    return ruta_salida

# Ejecutar
if __name__ == "__main__":
    csv_validado = r"C:\Users\jjbustos\OneDrive - Grupo Jerónimo Martins\Documents\dash_ausentismos\salidas\validation_report_45.csv"
    excel_tiendas = r"C:\Users\jjbustos\OneDrive - Grupo Jerónimo Martins\Documents\dash_ausentismos\datos_base\0002 Dash Stores.xlsx"
    salida_final = r"C:\Users\jjbustos\OneDrive - Grupo Jerónimo Martins\Documents\dash_ausentismos\salidas\validation_report_45_con_tiendas.csv"
    
    agregar_tiendas_modificado(csv_validado, excel_tiendas, salida_final)
