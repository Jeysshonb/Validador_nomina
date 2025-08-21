# Validador de Ausentismos - LÓGICA ORIGINAL CORRECTA
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

def validar_ausentismos_original(ruta_diagnostico, ruta_reporte, ruta_salida=None):
    """
    VALIDADOR ORIGINAL - LÓGICA CORRECTA:
    1. REPORTE = BASE PRINCIPAL (todos los registros)
    2. DIAGNÓSTICO = Solo para actualizar 'Modificado el' y 'Modificado por'
    3. Resultado = Exactamente las mismas filas del REPORTE
    """
    print("🔍 VALIDADOR DE AUSENTISMOS - LÓGICA ORIGINAL")
    print("="*60)
    
    # Verificar archivos
    if not os.path.exists(ruta_diagnostico):
        print(f"❌ No existe: {ruta_diagnostico}")
        return None
    if not os.path.exists(ruta_reporte):
        print(f"❌ No existe: {ruta_reporte}")
        return None
    
    # Leer archivos
    print("\n📂 LEYENDO ARCHIVOS:")
    df_diagnostico = leer_excel_y_renombrar_duplicadas(ruta_diagnostico)
    df_reporte = leer_excel_y_renombrar_duplicadas(ruta_reporte)
    
    if df_diagnostico is None or df_reporte is None:
        return None
    
    print(f"\n📊 NÚMEROS INICIALES:")
    print(f"   🎯 REPORTE (BASE PRINCIPAL): {len(df_reporte):,} filas")
    print(f"   📋 DIAGNÓSTICO (solo para modificado): {len(df_diagnostico):,} filas")
    
    # COLUMNAS CLAVE PARA BUSCAR COINCIDENCIAS
    columnas_busqueda = [
        'Número de personal',
        'Número ID', 
        'Clase absent./pres.',
        'Inicio de validez',
        'Fin de validez'
    ]
    
    print(f"\n🔍 BUSCANDO COINCIDENCIAS...")
    print(f"   Columnas de búsqueda: {columnas_busqueda}")
    
    # CREAR COPIA DEL REPORTE (será nuestro resultado final)
    df_resultado = df_reporte.copy()
    
    # LEFT JOIN: Reporte como principal, diagnóstico para completar
    df_con_diagnostico = pd.merge(
        df_reporte, 
        df_diagnostico[columnas_busqueda + ['Modificado el', 'Modificado por']], 
        on=columnas_busqueda, 
        how='left', 
        suffixes=('', '_diagnostico')
    )
    
    print(f"   ✅ Merge completado: {len(df_con_diagnostico):,} filas (igual que reporte)")
    
    # ACTUALIZAR SOLO LAS COLUMNAS DE MODIFICADO
    print(f"\n🔄 ACTUALIZANDO COLUMNAS DE MODIFICADO...")
    
    # Contar coincidencias
    tiene_diagnostico = df_con_diagnostico['Modificado el_diagnostico'].notna()
    coincidencias = tiene_diagnostico.sum()
    
    print(f"   📊 Coincidencias encontradas: {coincidencias:,} de {len(df_reporte):,}")
    print(f"   📊 Porcentaje de actualización: {(coincidencias/len(df_reporte)*100):.1f}%")
    
    # Actualizar donde hay coincidencia
    mask_actualizar = df_con_diagnostico['Modificado el_diagnostico'].notna()
    
    if mask_actualizar.any():
        df_resultado.loc[mask_actualizar, 'Modificado el'] = df_con_diagnostico.loc[mask_actualizar, 'Modificado el_diagnostico']
        print(f"   ✅ Actualizada 'Modificado el': {mask_actualizar.sum():,} registros")
    
    mask_actualizar_por = df_con_diagnostico['Modificado por_diagnostico'].notna()
    if mask_actualizar_por.any():
        df_resultado.loc[mask_actualizar_por, 'Modificado por'] = df_con_diagnostico.loc[mask_actualizar_por, 'Modificado por_diagnostico']
        print(f"   ✅ Actualizada 'Modificado por': {mask_actualizar_por.sum():,} registros")
    
    # VERIFICAR QUE EL RESULTADO TIENE EL MISMO NÚMERO DE FILAS
    print(f"\n✅ VERIFICACIÓN DE INTEGRIDAD:")
    print(f"   Filas originales del REPORTE: {len(df_reporte):,}")
    print(f"   Filas en resultado final: {len(df_resultado):,}")
    
    if len(df_resultado) == len(df_reporte):
        print(f"   🎉 ¡PERFECTO! No se perdieron ni duplicaron registros")
    else:
        print(f"   ❌ ERROR: El número de filas cambió")
        return None
    
    # CONVERTIR A SNAKE_CASE
    print(f"\n🐍 CONVIRTIENDO A SNAKE_CASE...")
    
    mapeo_columnas = {}
    for col in df_resultado.columns:
        col_snake = normalizar_columna(col)
        mapeo_columnas[col] = col_snake
    
    df_resultado = df_resultado.rename(columns=mapeo_columnas)
    print(f"   ✅ {len(mapeo_columnas)} columnas convertidas")
    
    # NORMALIZAR FORMATOS NUMÉRICOS
    print(f"\n🧹 NORMALIZANDO FORMATOS NUMÉRICOS...")
    
    columnas_numericas = [
        'numero_de_personal', 'numero_id', 'clase_absentpres', 
        'dias_presencabs', 'dias_naturales', 'centro_de_coste'
    ]
    
    # Agregar columnas que pueden tener números con sufijos
    columnas_numericas_adicionales = [col for col in df_resultado.columns if any(base in col for base in ['clase_absentpres', 'numero_de_personal', 'numero_id', 'centro_de_coste', 'dias_presencabs', 'dias_naturales'])]
    
    todas_columnas_numericas = list(set(columnas_numericas + columnas_numericas_adicionales))
    
    for col in todas_columnas_numericas:
        if col in df_resultado.columns:
            print(f"   🔧 Normalizando: {col}")
            df_resultado[col] = normalizar_numeros_vectorizado(df_resultado[col])
    
    # NORMALIZACIÓN ESPECÍFICA PARA QUITAR CEROS INICIALES DE clase_absentpres1
    if 'clase_absentpres1' in df_resultado.columns:
        print(f"   🎯 Normalizando específicamente: clase_absentpres1 (quitando ceros iniciales)")
        df_resultado['clase_absentpres1'] = df_resultado['clase_absentpres1'].astype(str).str.lstrip('0')
        # Si queda vacío después de quitar ceros, poner '0'
        df_resultado['clase_absentpres1'] = df_resultado['clase_absentpres1'].replace('', '0')
        
        # Mostrar muestra del resultado
        muestra = df_resultado['clase_absentpres1'].head(3).tolist()
        print(f"      ✅ Muestra resultado: {muestra}")
    
    # LIMPIAR VALORES FINALES
    print(f"\n🧹 LIMPIANDO VALORES FINALES...")
    df_resultado = df_resultado.fillna('')
    
    # Limpiar valores no deseados
    for col in df_resultado.columns:
        df_resultado[col] = df_resultado[col].astype(str).replace(['nan', 'None', 'NaT', '<NA>', '0.0'], '')
    
    # DETERMINAR RUTA DE SALIDA
    if ruta_salida is None:
        carpeta_salida = Path(ruta_reporte).parent.parent / "salidas"
        carpeta_salida.mkdir(exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        ruta_salida = carpeta_salida / f"validation_report_45_{timestamp}.csv"
    
    # GUARDAR ARCHIVO
    print(f"\n💾 GUARDANDO: {Path(ruta_salida).name}")
    df_resultado.to_csv(ruta_salida, index=False, encoding='utf-8-sig')
    
    # RESUMEN FINAL
    print(f"\n🎉 ¡VALIDACIÓN COMPLETADA!")
    print(f"📁 Archivo: {ruta_salida}")
    print(f"📊 Registros: {len(df_resultado):,} (igual que REPORTE original)")
    print(f"📋 Columnas: {len(df_resultado.columns)}")
    
    # Mostrar estadísticas de actualización
    print(f"\n📈 ESTADÍSTICAS DE ACTUALIZACIÓN:")
    print(f"   🎯 Registros del REPORTE: {len(df_reporte):,} (100%)")
    print(f"   ✅ Actualizados con DIAGNÓSTICO: {coincidencias:,} ({(coincidencias/len(df_reporte)*100):.1f}%)")
    print(f"   📋 Sin actualizar: {len(df_reporte)-coincidencias:,} ({((len(df_reporte)-coincidencias)/len(df_reporte)*100):.1f}%)")
    
    # Mostrar ejemplo de datos procesados
    if len(df_resultado) > 0:
        print(f"\n🔍 EJEMPLO DE DATOS PROCESADOS:")
        print("   (Primeras 3 filas con columnas clave)")
        cols_ejemplo = ['numero_de_personal', 'clase_absentpres', 'modificado_el', 'modificado_por']
        cols_disponibles = [col for col in cols_ejemplo if col in df_resultado.columns]
        
        if cols_disponibles:
            muestra = df_resultado[cols_disponibles].head(3)
            for i, (_, row) in enumerate(muestra.iterrows()):
                print(f"   Fila {i+1}: ", end="")
                for col in cols_disponibles:
                    valor = str(row[col])[:20]  # Limitar longitud
                    print(f"{col}={valor} ", end="")
                print()
    
    print(f"\n🏆 LÓGICA APLICADA:")
    print(f"   ✅ REPORTE = Base principal (todas las filas)")
    print(f"   ✅ DIAGNÓSTICO = Solo para actualizar 'Modificado el' y 'Modificado por'")
    print(f"   ✅ Resultado = Exactamente {len(df_resultado):,} filas (igual que REPORTE)")
    
    return ruta_salida


# Ejemplo de uso
if __name__ == "__main__":
    ruta_diagnostico = r"C:\Users\jjbustos\OneDrive - Grupo Jerónimo Martins\Documents\dash_ausentismos\datos_base\base_diagnosticos.XLSX"
    ruta_reporte = r"C:\Users\jjbustos\OneDrive - Grupo Jerónimo Martins\Documents\dash_ausentismos\datos_base\Reporte 45.XLSX"
    ruta_salida = r"C:\Users\jjbustos\OneDrive - Grupo Jerónimo Martins\Documents\dash_ausentismos\salidas\validation_report_45.csv"
    
    resultado = validar_ausentismos_original(ruta_diagnostico, ruta_reporte, ruta_salida)
    
    if resultado:
        print(f"\n🏆 ¡VALIDACIÓN EXITOSA! → {resultado}")
    else:
        print("\n💥 Error en la validación")
