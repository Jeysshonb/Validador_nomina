# Validador de Ausentismos - part_1
import pandas as pd
import numpy as np
import os
from pathlib import Path
import warnings
from datetime import datetime
import unicodedata
import re
warnings.filterwarnings('ignore')

def normalizar_columna(nombre):
    """Convierte a snake_case sin acentos"""
    nombre_sin_acentos = unicodedata.normalize('NFD', str(nombre))
    nombre_sin_acentos = ''.join(char for char in nombre_sin_acentos if unicodedata.category(char) != 'Mn')
    nombre_lower = nombre_sin_acentos.lower()
    nombre_snake = re.sub(r'[^\w\s]', '', nombre_lower)
    nombre_snake = re.sub(r'\s+', '_', nombre_snake)
    nombre_snake = re.sub(r'_+', '_', nombre_snake).strip('_')
    return nombre_snake

def normalizar_numeros_vectorizado(serie):
    """Normaliza una serie completa de números de una vez"""
    if isinstance(serie, pd.DataFrame):
        serie = serie.iloc[:, 0]
    
    nombre_col = getattr(serie, 'name', 'columna_sin_nombre')
    print(f"      🔧 Normalizando serie: {nombre_col}")
    
    # Convertir todo a string primero
    serie_str = serie.astype(str)
    
    # Reemplazar comas por puntos
    serie_str = serie_str.str.replace(',', '.')
    
    # Convertir a numérico donde sea posible
    serie_num = pd.to_numeric(serie_str, errors='coerce')
    
    # Para valores que se convirtieron exitosamente a número
    mask_numerico = serie_num.notna()
    
    # Crear resultado como string
    resultado = serie_str.copy()
    
    # Para valores numéricos, convertir enteros sin decimales
    valores_enteros = (serie_num % 1 == 0) & mask_numerico
    resultado.loc[valores_enteros] = serie_num.loc[valores_enteros].astype(int).astype(str)
    
    # Para valores con decimales, mantener pero sin ceros innecesarios
    valores_decimales = (serie_num % 1 != 0) & mask_numerico
    if valores_decimales.any():
        resultado.loc[valores_decimales] = serie_num.loc[valores_decimales].astype(str)
    
    # Limpiar valores nulos
    resultado = resultado.replace(['nan', 'None', 'NaT', '<NA>', ''], '')
    
    return resultado

def leer_excel_y_renombrar_duplicadas(ruta):
    """Lee Excel y renombra columnas duplicadas automáticamente"""
    print(f"📖 Leyendo: {Path(ruta).name}")
    try:
        df = pd.read_excel(ruta)
        
        # Renombrar columnas duplicadas
        columnas_nuevas = []
        contador = {}
        
        for col in df.columns:
            if col in contador:
                contador[col] += 1
                nuevo_nombre = f"{col}_{contador[col]}"
                columnas_nuevas.append(nuevo_nombre)
                print(f"   🔄 Columna duplicada: '{col}' → '{nuevo_nombre}'")
            else:
                contador[col] = 0
                columnas_nuevas.append(col)
        
        df.columns = columnas_nuevas
        print(f"   ✅ {df.shape[0]:,} filas, {df.shape[1]} columnas")
        return df
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def convertir_fecha_modificacion(df):
    """Convierte 'Modificado el' a datetime usando el mismo método que funciona"""
    if 'Modificado el' not in df.columns:
        print("   ⚠️ No hay columna 'Modificado el'")
        df['fecha_dt'] = pd.NaT
        return df
    
    print("   📅 Convirtiendo fechas...")
    
    # Convertir a datetime con formato día primero
    df['fecha_dt'] = pd.to_datetime(df['Modificado el'], errors='coerce', dayfirst=True)
    
    # Si hay números seriales de Excel, convertirlos también
    mask_numerico = pd.to_numeric(df['Modificado el'], errors='coerce').notna()
    if mask_numerico.any():
        numeros = pd.to_numeric(df['Modificado el'], errors='coerce')
        df.loc[mask_numerico, 'fecha_dt'] = pd.to_datetime(numeros, origin='1899-12-30', unit='D', errors='coerce')
    
    fechas_validas = df['fecha_dt'].notna().sum()
    print(f"      ✅ {fechas_validas:,} fechas válidas convertidas")
    
    return df

def validar_ausentismos(ruta_base, ruta_reporte, ruta_salida=None):
    """
    VALIDADOR de ausentismos: 
    - Compara registros por columnas clave
    - Toma el de fecha más reciente
    - Mantiene toda la información
    - Convierte a snake_case
    """
    print("🔍 VALIDADOR DE AUSENTISMOS")
    print("="*50)
    
    # Verificar archivos
    if not os.path.exists(ruta_base):
        print(f"❌ No existe: {ruta_base}")
        return None
    if not os.path.exists(ruta_reporte):
        print(f"❌ No existe: {ruta_reporte}")
        return None
    
    # Leer archivos
    print("\n📂 LEYENDO ARCHIVOS:")
    df_base = leer_excel_y_renombrar_duplicadas(ruta_base)
    df_reporte = leer_excel_y_renombrar_duplicadas(ruta_reporte)
    
    if df_base is None or df_reporte is None:
        return None
    
    # Convertir fechas
    print("\n📅 PROCESANDO FECHAS:")
    df_base = convertir_fecha_modificacion(df_base)
    df_reporte = convertir_fecha_modificacion(df_reporte)
    
    # Agregar sufijos para identificar origen
    df_base = df_base.add_suffix('_base')
    df_reporte = df_reporte.add_suffix('_reporte')
    
    # COLUMNAS CLAVE PARA VERIFICACIÓN (identificar si es el mismo registro)
    columnas_verificacion = [
        'Número de personal',
        'Número ID', 
        'Clase absent./pres.',
        'Inicio de validez',
        'Fin de validez'
    ]
    
    # Renombrar columnas de verificación para que coincidan
    for col in columnas_verificacion:
        if f"{col}_base" in df_base.columns:
            df_base[col] = df_base[f"{col}_base"]
        if f"{col}_reporte" in df_reporte.columns:
            df_reporte[col] = df_reporte[f"{col}_reporte"]
    
    print(f"\n🔍 VERIFICANDO REGISTROS...")
    print(f"   Columnas de verificación: {columnas_verificacion}")
    
    # OUTER JOIN para mantener todos los registros
    df_verificado = pd.merge(df_base, df_reporte, on=columnas_verificacion, how='outer', suffixes=('_base', '_reporte'))
    
    print(f"   ✅ Verificación completada: {len(df_verificado):,} registros")
    
    # SELECCIONAR EL REGISTRO MÁS RECIENTE
    print("\n⏰ SELECCIONANDO REGISTROS MÁS RECIENTES...")
    
    def seleccionar_mas_reciente(row):
        fecha_base = row.get('fecha_dt_base')
        fecha_reporte = row.get('fecha_dt_reporte')
        
        # Si ambas fechas son válidas, tomar la más reciente
        if pd.notna(fecha_base) and pd.notna(fecha_reporte):
            if fecha_reporte >= fecha_base:
                return 'reporte'
            else:
                return 'base'
        # Si solo una es válida, usar esa
        elif pd.notna(fecha_reporte):
            return 'reporte'
        elif pd.notna(fecha_base):
            return 'base'
        # Si ninguna es válida, priorizar reporte (más actual)
        else:
            return 'reporte'
    
    # Aplicar selección
    df_verificado['fuente_seleccionada'] = df_verificado.apply(seleccionar_mas_reciente, axis=1)
    
    # OBTENER EL ORDEN REAL DE LAS COLUMNAS DEL REPORTE (que tiene la estructura completa)
    print(f"   🔍 Detectando estructura real de columnas...")
    
    # Quitar sufijo _reporte para obtener nombres originales
    columnas_reales_reporte = [col.replace('_reporte', '') for col in df_reporte.columns if col.endswith('_reporte') and col != 'fecha_dt_reporte']
    
    print(f"   📋 Columnas detectadas en reporte: {len(columnas_reales_reporte)}")
    print(f"   📋 Primeras 10 columnas: {columnas_reales_reporte[:10]}")
    
    # USAR EL ORDEN REAL DE LAS COLUMNAS COMO ESTÁN EN EL EXCEL
    orden_columnas_reales = columnas_reales_reporte
    
    print(f"   📋 Total columnas en orden real: {len(orden_columnas_reales)}")
    
    # CREAR DATAFRAME FINAL COMBINANDO LA INFORMACIÓN EN EL ORDEN REAL
    print("   🔧 Combinando información en orden real de las columnas...")
    
    df_final = pd.DataFrame()
    
    # Para cada columna EN EL ORDEN REAL, tomar el valor del archivo seleccionado
    for col in orden_columnas_reales:
        col_base = f"{col}_base"
        col_reporte = f"{col}_reporte"
        
        if col_base in df_verificado.columns and col_reporte in df_verificado.columns:
            # Combinar basado en fuente seleccionada
            df_final[col] = df_verificado.apply(
                lambda row: row[col_reporte] if row['fuente_seleccionada'] == 'reporte' else row[col_base], 
                axis=1
            )
            print(f"      ✅ Procesada: {col}")
        elif col_base in df_verificado.columns:
            df_final[col] = df_verificado[col_base]
            print(f"      📋 Solo en base: {col}")
        elif col_reporte in df_verificado.columns:
            df_final[col] = df_verificado[col_reporte]
            print(f"      📋 Solo en reporte: {col}")
        else:
            # Si la columna no existe, crear vacía pero mantener el orden
            df_final[col] = ''
            print(f"      ⚠️ No encontrada: {col}")
    
    # Agregar información de validación
    df_final['fuente_datos'] = df_verificado['fuente_seleccionada']
    
    # CONVERTIR NOMBRES DE COLUMNAS A SNAKE_CASE MANTENIENDO EL ORDEN REAL
    print("\n🐍 CONVIRTIENDO A SNAKE_CASE EN ORDEN REAL...")
    
    # Crear orden en snake_case manteniendo la secuencia real
    orden_snake_case = [normalizar_columna(col) for col in orden_columnas_reales]
    orden_snake_case.append('fuente_datos')  # Agregar al final
    
    # Crear mapeo de columnas
    mapeo_columnas = {}
    for col in df_final.columns:
        if col != 'fuente_datos':
            col_snake = normalizar_columna(col)
            mapeo_columnas[col] = col_snake
    
    # Aplicar conversión
    df_final = df_final.rename(columns=mapeo_columnas)
    
    # REORDENAR COLUMNAS SEGÚN EL ORDEN SNAKE_CASE REAL
    columnas_disponibles = [col for col in orden_snake_case if col in df_final.columns]
    df_final = df_final[columnas_disponibles]
    
    print(f"   ✅ {len(mapeo_columnas)} columnas convertidas y ordenadas según estructura real")
    
    # NORMALIZAR FORMATOS NUMÉRICOS
    print("\n🧹 NORMALIZANDO FORMATOS NUMÉRICOS...")
    
    columnas_numericas = [
        'numero_de_personal', 'numero_id', 'clase_absentpres', 
        'dias_presencabs', 'dias_naturales', 'centro_de_coste'
    ]
    
    # Agregar columnas que pueden tener números con sufijos
    columnas_numericas_adicionales = [col for col in df_final.columns if any(base in col for base in ['clase_absentpres', 'numero_de_personal', 'numero_id', 'centro_de_coste', 'dias_presencabs', 'dias_naturales'])]
    
    todas_columnas_numericas = list(set(columnas_numericas + columnas_numericas_adicionales))
    
    for col in todas_columnas_numericas:
        if col in df_final.columns:
            print(f"   🔧 Normalizando: {col}")
            df_final[col] = normalizar_numeros_vectorizado(df_final[col])
    
    # NORMALIZACIÓN ESPECÍFICA PARA QUITAR CEROS INICIALES DE clase_absentpres1
    if 'clase_absentpres1' in df_final.columns:
        print(f"   🎯 Normalizando específicamente: clase_absentpres1 (quitando ceros iniciales)")
        df_final['clase_absentpres1'] = df_final['clase_absentpres1'].astype(str).str.lstrip('0')
        # Si queda vacío después de quitar ceros, poner '0'
        df_final['clase_absentpres1'] = df_final['clase_absentpres1'].replace('', '0')
        
        # Mostrar muestra del resultado
        muestra = df_final['clase_absentpres1'].head(3).tolist()
        print(f"      ✅ Muestra resultado: {muestra}")
    
    # LIMPIAR VALORES FINALES
    print("\n🧹 Limpiando valores finales...")
    df_final = df_final.fillna('')
    
    # Limpiar valores no deseados
    for col in df_final.columns:
        if col != 'fuente_datos':
            df_final[col] = df_final[col].astype(str).replace(['nan', 'None', 'NaT', '<NA>', '0.0'], '')
    
    # DETERMINAR RUTA DE SALIDA
    if ruta_salida is None:
        carpeta_salida = Path(ruta_base).parent.parent / "salidas"
        carpeta_salida.mkdir(exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        ruta_salida = carpeta_salida / f"validation_report_45_{timestamp}.csv"
    
    # GUARDAR ARCHIVO
    print(f"\n💾 GUARDANDO: {Path(ruta_salida).name}")
    df_final.to_csv(ruta_salida, index=False, encoding='utf-8-sig')
    
    # RESUMEN FINAL
    print(f"\n🎉 ¡VALIDACIÓN COMPLETADA!")
    print(f"📁 Archivo: {ruta_salida}")
    print(f"📊 Registros: {len(df_final):,}")
    print(f"📋 Columnas: {len(df_final.columns)}")
    
    # Mostrar orden final de columnas
    print(f"\n📋 ORDEN FINAL DE COLUMNAS (snake_case):")
    for i, col in enumerate(df_final.columns):
        print(f"   {i+1:2d}. {col}")
    
    print(f"\n📋 CORRESPONDENCIA COLUMNAS REALES → SNAKE_CASE:")
    for i, (orig, snake) in enumerate(zip(orden_columnas_reales, orden_snake_case[:-1])):
        print(f"   {i+1:2d}. '{orig}' → '{snake}'")
        if i >= 15:  # Mostrar solo las primeras 15
            print(f"   ... y {len(orden_columnas_reales)-16} más")
            break
    
    # Estadísticas de fuentes
    if 'fuente_datos' in df_final.columns:
        print(f"\n📈 FUENTES DE DATOS SELECCIONADAS:")
        fuentes = df_final['fuente_datos'].value_counts()
        for fuente, cantidad in fuentes.items():
            porcentaje = (cantidad / len(df_final)) * 100
            print(f"   • {fuente}: {cantidad:,} registros ({porcentaje:.1f}%)")
    
    # Mostrar ejemplo de datos procesados
    if len(df_final) > 0:
        print(f"\n🔍 EJEMPLO DE DATOS PROCESADOS:")
        print("   (Primeras 3 filas con columnas clave)")
        cols_ejemplo = ['numero_de_personal', 'clase_absentpres', 'modificado_el', 'modificado_por', 'fuente_datos']
        cols_disponibles = [col for col in cols_ejemplo if col in df_final.columns]
        
        if cols_disponibles:
            muestra = df_final[cols_disponibles].head(3)
            for i, (_, row) in enumerate(muestra.iterrows()):
                print(f"   Fila {i+1}: ", end="")
                for col in cols_disponibles:
                    valor = str(row[col])[:20]  # Limitar longitud
                    print(f"{col}={valor} ", end="")
                print()
    
    return ruta_salida


# Ejemplo de uso
if __name__ == "__main__":
    ruta_base = r"C:\Users\jjbustos\OneDrive - Grupo Jerónimo Martins\Documents\dash_ausentismos\datos_base\base_diagnosticos.XLSX"
    ruta_reporte = r"C:\Users\jjbustos\OneDrive - Grupo Jerónimo Martins\Documents\dash_ausentismos\datos_base\Reporte 45.XLSX"
    ruta_salida = r"C:\Users\jjbustos\OneDrive - Grupo Jerónimo Martins\Documents\dash_ausentismos\salidas\validation_report_45.csv"
    
    resultado = validar_ausentismos(ruta_base, ruta_reporte, ruta_salida)
    
    if resultado:
        print(f"\n🏆 ¡VALIDACIÓN EXITOSA! → {resultado}")
    else:
        print("\n💥 Error en la validación")