import streamlit as st
import pandas as pd
import sys
import os
from datetime import datetime
import io

# Agregar el directorio actual al path para importar los módulos
sys.path.append(os.path.dirname(__file__))

# Importar las funciones de validación
try:
    from part1_validation_reporte_45 import validar_ausentismos
    from part2_dash_store_total import agregar_tiendas_directo
except ImportError as e:
    st.error(f"Error importando módulos: {e}")
    st.stop()

# Configuración de la página
st.set_page_config(
    page_title="Validador de Ausentismos",
    page_icon="📊",
    layout="wide"
)

st.title("🏢 Validador de Ausentismos")
st.markdown("Procesa y valida datos de ausentismos en 2 pasos simples")
st.markdown("---")

# Crear carpetas temporales
os.makedirs("temp", exist_ok=True)
os.makedirs("salidas", exist_ok=True)

# PASO 1: VALIDACIÓN
st.header("🔍 Paso 1: Validación de Ausentismos")

col1, col2 = st.columns(2)

with col1:
    st.subheader("📂 Base de Diagnósticos")
    archivo_base = st.file_uploader(
        "Archivo base (Excel)",
        type=['xlsx', 'xls'],
        key="base"
    )

with col2:
    st.subheader("📊 Reporte 45")
    archivo_reporte = st.file_uploader(
        "Archivo reporte (Excel)", 
        type=['xlsx', 'xls'],
        key="reporte"
    )

validacion_completa = False

if archivo_base and archivo_reporte:
    if st.button("🚀 Ejecutar Validación", type="primary"):
        with st.spinner("Procesando validación..."):
            try:
                # Guardar archivos temporalmente
                ruta_base = f"temp/base_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
                ruta_reporte = f"temp/reporte_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
                
                with open(ruta_base, "wb") as f:
                    f.write(archivo_base.getvalue())
                with open(ruta_reporte, "wb") as f:
                    f.write(archivo_reporte.getvalue())
                
                # Ejecutar validación usando la función original
                ruta_validado = validar_ausentismos(ruta_base, ruta_reporte)
                
                if ruta_validado:
                    st.success("✅ Validación completada exitosamente!")
                    
                    # Leer el resultado para mostrar estadísticas
                    df_validado = pd.read_csv(ruta_validado, encoding='utf-8-sig')
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("📊 Total Registros", f"{len(df_validado):,}")
                    with col2:
                        st.metric("📋 Total Columnas", len(df_validado.columns))
                    with col3:
                        if 'fuente_datos' in df_validado.columns:
                            reporte_count = (df_validado['fuente_datos'] == 'reporte').sum()
                            st.metric("📈 Del Reporte", f"{reporte_count:,}")
                    
                    # Guardar ruta en session_state
                    st.session_state['ruta_validado'] = ruta_validado
                    validacion_completa = True
                    
                    # Vista previa
                    st.subheader("👀 Vista Previa")
                    st.dataframe(df_validado.head(10), use_container_width=True)
                    
                # Limpiar archivos temporales
                if os.path.exists(ruta_base):
                    os.remove(ruta_base)
                if os.path.exists(ruta_reporte):
                    os.remove(ruta_reporte)
                    
            except Exception as e:
                st.error(f"❌ Error en validación: {str(e)}")

st.markdown("---")

# PASO 2: AGREGAR TIENDAS  
st.header("🏪 Paso 2: Agregar Información de Tiendas")

if 'ruta_validado' not in st.session_state:
    st.warning("⚠️ Primero completa el Paso 1: Validación")
else:
    st.success("✅ Datos validados listos para procesar")
    
    st.subheader("📊 Archivo de Tiendas")
    archivo_tiendas = st.file_uploader(
        "Archivo de tiendas (Excel)",
        type=['xlsx', 'xls'],
        key="tiendas"
    )
    
    if archivo_tiendas:
        if st.button("🔗 Agregar Tiendas", type="primary"):
            with st.spinner("Agregando información de tiendas..."):
                try:
                    # Guardar archivo de tiendas temporalmente
                    ruta_tiendas = f"temp/tiendas_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
                    
                    with open(ruta_tiendas, "wb") as f:
                        f.write(archivo_tiendas.getvalue())
                    
                    # Ejecutar agregado de tiendas usando la función original
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    ruta_final = f"salidas/validation_report_45_con_tiendas_{timestamp}.csv"
                    
                    resultado = agregar_tiendas_directo(
                        st.session_state['ruta_validado'],
                        ruta_tiendas,
                        ruta_final
                    )
                    
                    if resultado and os.path.exists(resultado):
                        st.success("✅ Información de tiendas agregada exitosamente!")
                        
                        # Leer resultado final para estadísticas
                        df_final = pd.read_csv(resultado, encoding='utf-8-sig')
                        
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("📊 Registros Finales", f"{len(df_final):,}")
                        with col2:
                            st.metric("📋 Columnas Finales", len(df_final.columns))
                        with col3:
                            if 'nombre_tienda' in df_final.columns:
                                con_tienda = (df_final['nombre_tienda'] != '').sum()
                                st.metric("🏪 Con Tienda", f"{con_tienda:,}")
                        
                        # Vista previa final
                        st.subheader("👀 Resultado Final")
                        st.dataframe(df_final.head(10), use_container_width=True)
                        
                        # Botón de descarga
                        st.subheader("💾 Descargar Resultado")
                        
                        with open(resultado, 'r', encoding='utf-8-sig') as f:
                            csv_data = f.read()
                        
                        st.download_button(
                            label="📥 Descargar CSV Final",
                            data=csv_data,
                            file_name=os.path.basename(resultado),
                            mime="text/csv",
                            type="primary"
                        )
                        
                        st.success(f"🎉 ¡Proceso completado! Archivo guardado como: {os.path.basename(resultado)}")
                        
                    # Limpiar archivo temporal
                    if os.path.exists(ruta_tiendas):
                        os.remove(ruta_tiendas)
                        
                except Exception as e:
                    st.error(f"❌ Error agregando tiendas: {str(e)}")

# Información adicional
with st.sidebar:
    st.header("📋 Información")
    st.markdown("""
    ### Proceso:
    1. **Validación**: Combina base y reporte
    2. **Tiendas**: Agrega info de tiendas
    
    ### Archivos necesarios:
    - Base diagnósticos (.xlsx)
    - Reporte 45 (.xlsx)
    - Datos tiendas (.xlsx)
    
    ### Resultado:
    - CSV con datos validados y tiendas
    """)
    
    if st.button("🗑️ Limpiar Datos"):
        # Limpiar session state
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()
