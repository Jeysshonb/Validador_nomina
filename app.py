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
    from part1_validation_reporte_45 import validar_ausentismos_original as validar_ausentismos
    from part2_dash_store_total import agregar_tiendas_modificado as agregar_tiendas_directo
except ImportError as e:
    st.error(f"Error importando módulos: {e}")
    st.stop()

# Configuración de la página
st.set_page_config(
    page_title="Dash Ausentismos Nómina",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personalizado para mejorar el diseño
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #1f4e79 0%, #2e75b6 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        text-align: center;
    }
    .step-container {
        background: #f8f9fa;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 5px solid #2e75b6;
        margin-bottom: 2rem;
    }
    .success-box {
        background: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
        padding: 1rem;
        border-radius: 5px;
        margin: 1rem 0;
    }
    .download-section {
        background: #e3f2fd;
        padding: 1rem;
        border-radius: 8px;
        border: 2px dashed #2196f3;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Header principal
st.markdown("""
<div class="main-header">
    <h1>📊 Dash Ausentismos Nómina</h1>
    <p><strong>Creado por Jeysshon</strong> | Grupo Jerónimo Martins</p>
    <p>Sistema de validación y procesamiento de datos de ausentismos</p>
</div>
""", unsafe_allow_html=True)

# Crear carpetas temporales
os.makedirs("temp", exist_ok=True)
os.makedirs("salidas", exist_ok=True)

def crear_descargable(df, nombre_archivo, descripcion):
    """Función para crear botón de descarga con estadísticas"""
    st.markdown(f"""
    <div class="download-section">
        <h4>💾 {descripcion}</h4>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("📊 Registros", f"{len(df):,}")
    with col2:
        st.metric("📋 Columnas", len(df.columns))
    with col3:
        # Calcular tamaño aproximado del archivo
        tamaño_mb = len(df.to_csv(index=False).encode('utf-8')) / (1024 * 1024)
        st.metric("📁 Tamaño", f"{tamaño_mb:.2f} MB")
    
    # Vista previa
    with st.expander("👀 Vista previa de datos"):
        st.dataframe(df.head(10), use_container_width=True)
    
    # Botón de descarga
    csv_data = df.to_csv(index=False, encoding='utf-8-sig')
    st.download_button(
        label=f"📥 Descargar {nombre_archivo}",
        data=csv_data,
        file_name=nombre_archivo,
        mime="text/csv",
        type="primary",
        use_container_width=True
    )
    return csv_data

# PASO 1: VALIDACIÓN
st.markdown('<div class="step-container">', unsafe_allow_html=True)
st.header("🔍 Paso 1: Validación de Ausentismos")

col1, col2 = st.columns(2)

with col1:
    st.subheader("📂 Base de Diagnósticos")
    archivo_base = st.file_uploader(
        "Selecciona el archivo base (Excel)",
        type=['xlsx', 'xls'],
        key="base",
        help="Archivo que contiene la base de diagnósticos de ausentismos"
    )

with col2:
    st.subheader("📊 Reporte 45")
    archivo_reporte = st.file_uploader(
        "Selecciona el archivo reporte (Excel)", 
        type=['xlsx', 'xls'],
        key="reporte",
        help="Archivo del reporte 45 con datos de ausentismos"
    )

if archivo_base and archivo_reporte:
    st.info("✅ Ambos archivos cargados. Listos para validación.")
    
    if st.button("🚀 Ejecutar Validación", type="primary", use_container_width=True):
        with st.spinner("🔄 Procesando validación..."):
            try:
                # Guardar archivos temporalmente
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                ruta_base = f"temp/base_{timestamp}.xlsx"
                ruta_reporte = f"temp/reporte_{timestamp}.xlsx"
                
                with open(ruta_base, "wb") as f:
                    f.write(archivo_base.getvalue())
                with open(ruta_reporte, "wb") as f:
                    f.write(archivo_reporte.getvalue())
                
                # Ejecutar validación
                ruta_validado = validar_ausentismos(ruta_base, ruta_reporte)
                
                if ruta_validado:
                    st.markdown('<div class="success-box">✅ Validación completada exitosamente!</div>', unsafe_allow_html=True)
                    
                    # Leer el resultado
                    df_validado = pd.read_csv(ruta_validado, encoding='utf-8-sig')
                    
                    # Crear descargable para Paso 1
                    nombre_archivo_paso1 = f"datos_validados_{timestamp}.csv"
                    crear_descargable(
                        df_validado, 
                        nombre_archivo_paso1,
                        "Datos Validados - Paso 1"
                    )
                    
                    # Estadísticas adicionales
                    st.subheader("📈 Estadísticas de Validación")
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        st.metric("📊 Total Registros", f"{len(df_validado):,}")
                    with col2:
                        st.metric("📋 Total Columnas", len(df_validado.columns))
                    with col3:
                        if 'fuente_datos' in df_validado.columns:
                            reporte_count = (df_validado['fuente_datos'] == 'reporte').sum()
                            st.metric("📈 Del Reporte", f"{reporte_count:,}")
                        else:
                            st.metric("📈 Datos", "100%")
                    with col4:
                        if 'modificado_el' in df_validado.columns:
                            modificados = df_validado['modificado_el'].notna().sum()
                            st.metric("🔄 Actualizados", f"{modificados:,}")
                    
                    # Guardar en session_state
                    st.session_state['ruta_validado'] = ruta_validado
                    st.session_state['df_validado'] = df_validado
                    
                # Limpiar archivos temporales
                for archivo in [ruta_base, ruta_reporte]:
                    if os.path.exists(archivo):
                        os.remove(archivo)
                        
            except Exception as e:
                st.error(f"❌ Error en validación: {str(e)}")
                st.exception(e)

st.markdown('</div>', unsafe_allow_html=True)

# PASO 2: AGREGAR TIENDAS
st.markdown('<div class="step-container">', unsafe_allow_html=True)
st.header("🏪 Paso 2: Agregar Información de Tiendas")

if 'ruta_validado' not in st.session_state:
    st.warning("⚠️ Primero completa el Paso 1: Validación")
else:
    st.success("✅ Datos validados disponibles para procesar")
    
    st.subheader("📊 Archivo de Tiendas")
    archivo_tiendas = st.file_uploader(
        "Selecciona el archivo de tiendas (Excel)",
        type=['xlsx', 'xls'],
        key="tiendas",
        help="Archivo que contiene información de tiendas y centros de coste"
    )
    
    if archivo_tiendas:
        st.info("✅ Archivo de tiendas cargado.")
        
        if st.button("🔗 Agregar Tiendas", type="primary", use_container_width=True):
            with st.spinner("🔄 Agregando información de tiendas..."):
                try:
                    # Guardar archivo de tiendas temporalmente
                    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                    ruta_tiendas = f"temp/tiendas_{timestamp}.xlsx"
                    
                    with open(ruta_tiendas, "wb") as f:
                        f.write(archivo_tiendas.getvalue())
                    
                    # Ejecutar agregado de tiendas
                    ruta_final = f"salidas/validation_report_45_con_tiendas_{timestamp}.csv"
                    
                    resultado = agregar_tiendas_directo(
                        st.session_state['ruta_validado'],
                        ruta_tiendas,
                        ruta_final
                    )
                    
                    if resultado and os.path.exists(resultado):
                        st.markdown('<div class="success-box">✅ Información de tiendas agregada exitosamente!</div>', unsafe_allow_html=True)
                        
                        # Leer resultado final
                        df_final = pd.read_csv(resultado, encoding='utf-8-sig')
                        
                        # Crear descargable para Paso 2 (Resultado Final)
                        nombre_archivo_final = f"reporte_final_con_tiendas_{timestamp}.csv"
                        crear_descargable(
                            df_final,
                            nombre_archivo_final,
                            "Reporte Final con Tiendas - Paso 2"
                        )
                        
                        # Estadísticas detalladas
                        st.subheader("📈 Estadísticas del Resultado Final")
                        
                        col1, col2, col3, col4 = st.columns(4)
                        with col1:
                            st.metric("📊 Registros Finales", f"{len(df_final):,}")
                        with col2:
                            st.metric("📋 Columnas Finales", len(df_final.columns))
                        with col3:
                            if 'nombre_tienda' in df_final.columns:
                                con_tienda = (df_final['nombre_tienda'] != '').sum()
                                porcentaje = (con_tienda / len(df_final) * 100) if len(df_final) > 0 else 0
                                st.metric("🏪 Con Tienda", f"{con_tienda:,} ({porcentaje:.1f}%)")
                        with col4:
                            if 'value_tienda' in df_final.columns:
                                con_value = (df_final['value_tienda'] != '').sum()
                                st.metric("🏷️ Con Código", f"{con_value:,}")
                        
                        # Análisis de completitud
                        st.subheader("📋 Análisis de Completitud de Datos")
                        
                        columnas_importantes = ['nombre_tienda', 'value_tienda', 'centro_de_coste', 'numero_de_personal']
                        completitud_data = []
                        
                        for col in columnas_importantes:
                            if col in df_final.columns:
                                total = len(df_final)
                                completos = (df_final[col] != '').sum()
                                porcentaje = (completos / total * 100) if total > 0 else 0
                                completitud_data.append({
                                    'Columna': col,
                                    'Completos': completos,
                                    'Total': total,
                                    'Porcentaje': f"{porcentaje:.1f}%"
                                })
                        
                        if completitud_data:
                            df_completitud = pd.DataFrame(completitud_data)
                            st.dataframe(df_completitud, use_container_width=True)
                        
                        # Guardar en session state
                        st.session_state['df_final'] = df_final
                        st.session_state['ruta_final'] = resultado
                        
                        st.success(f"🎉 ¡Proceso completado exitosamente!")
                        
                    # Limpiar archivo temporal
                    if os.path.exists(ruta_tiendas):
                        os.remove(ruta_tiendas)
                        
                except Exception as e:
                    st.error(f"❌ Error agregando tiendas: {str(e)}")
                    st.exception(e)

st.markdown('</div>', unsafe_allow_html=True)

# SECCIÓN DE DESCARGA HISTÓRICA
if 'df_validado' in st.session_state or 'df_final' in st.session_state:
    st.markdown("---")
    st.header("📁 Centro de Descargas")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if 'df_validado' in st.session_state:
            st.subheader("📊 Datos Validados (Paso 1)")
            df_validado = st.session_state['df_validado']
            timestamp_desc = datetime.now().strftime('%Y%m%d_%H%M%S')
            crear_descargable(
                df_validado,
                f"datos_validados_{timestamp_desc}.csv",
                "Resultado del Paso 1"
            )
    
    with col2:
        if 'df_final' in st.session_state:
            st.subheader("🏪 Datos con Tiendas (Paso 2)")
            df_final = st.session_state['df_final']
            timestamp_desc = datetime.now().strftime('%Y%m%d_%H%M%S')
            crear_descargable(
                df_final,
                f"reporte_final_{timestamp_desc}.csv",
                "Resultado Final Completo"
            )

# SIDEBAR CON INFORMACIÓN
with st.sidebar:
    st.markdown("""
    <div style="background: #f0f8ff; padding: 1rem; border-radius: 8px; margin-bottom: 1rem;">
        <h3 style="color: #1f4e79; margin-top: 0;">📋 Información del Sistema</h3>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    ### 🔄 Proceso:
    1. **Validación**: Combina base de diagnósticos con reporte 45
    2. **Tiendas**: Agrega información de tiendas por centro de coste
    
    ### 📁 Archivos necesarios:
    - 📂 Base diagnósticos (.xlsx)
    - 📊 Reporte 45 (.xlsx)  
    - 🏪 Datos tiendas (.xlsx)
    
    ### 📊 Resultado:
    - 💾 CSV con datos validados (Paso 1)
    - 💾 CSV con datos + tiendas (Paso 2)
    
    ### 👤 Información:
    - **Desarrollador**: Jeysshon
    - **Empresa**: Grupo Jerónimo Martins
    - **Versión**: 2.0
    """)
    
    st.markdown("---")
    
    # Estadísticas de sesión
    if 'df_validado' in st.session_state or 'df_final' in st.session_state:
        st.subheader("📈 Estadísticas de Sesión")
        
        if 'df_validado' in st.session_state:
            st.metric("Paso 1 - Registros", f"{len(st.session_state['df_validado']):,}")
        
        if 'df_final' in st.session_state:
            st.metric("Paso 2 - Registros", f"{len(st.session_state['df_final']):,}")
            
            # Calcular mejora en completitud
            if 'df_validado' in st.session_state:
                mejora = len(st.session_state['df_final']) - len(st.session_state['df_validado'])
                st.metric("Diferencia", f"{mejora:,}")
    
    st.markdown("---")
    
    # Botón de limpieza
    if st.button("🗑️ Limpiar Sesión", use_container_width=True):
        # Limpiar session state
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()
    
    # Información técnica
    with st.expander("🔧 Información Técnica"):
        st.markdown("""
        **Tecnologías utilizadas:**
        - Streamlit 
        - Pandas
        - OpenPyXL
        - NumPy
        
        **Funciones principales:**
        - Validación de datos
        - Normalización de columnas
        - Merge de datos por centro de coste
        - Limpieza y formateo
        """)

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; font-size: 0.9em; padding: 1rem;">
    <p>📊 <strong>Dash Ausentismos Nómina</strong> | Desarrollado por <strong>Jeysshon</strong> para Grupo Jerónimo Martins</p>
    <p>Sistema de procesamiento y validación de datos de ausentismos | Versión 2.0</p>
</div>
""", unsafe_allow_html=True)
