import streamlit as st
import pandas as pd
import sys
import os
from datetime import datetime
import io

# Agregar el directorio actual al path para importar los módulos
sys.path.append(os.path.dirname(__file__))

# Importar las funciones de validación - EXACTAS DEL GITHUB
try:
    from part1_validation_reporte_45 import validar_ausentismos_original
    from part2_dash_store_total import agregar_tiendas_modificado
    print("✅ Módulos importados correctamente del GitHub")
except ImportError as e:
    st.error(f"❌ Error importando módulos: {e}")
    st.error("Asegúrate de que los archivos part1_validation_reporte_45.py y part2_dash_store_total.py estén en la misma carpeta")
    st.stop()
except Exception as e:
    st.error(f"❌ Error inesperado: {e}")
    st.stop()

# Configuración de la página
st.set_page_config(
    page_title="Dash Ausentismos Nómina",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personalizado - ADAPTABLE CLARO/OSCURO
st.markdown("""
<style>
    /* Variables para modo claro y oscuro */
    :root {
        --bg-primary: #ffffff;
        --bg-secondary: #f8f9fa;
        --text-primary: #000000;
        --text-secondary: #6c757d;
        --border-color: #dee2e6;
        --success-bg: #d4edda;
        --success-text: #155724;
        --success-border: #c3e6cb;
        --warning-bg: #fff3cd;
        --warning-text: #856404;
        --warning-border: #ffeaa7;
        --error-bg: #f8d7da;
        --error-text: #721c24;
        --error-border: #f5c6cb;
    }
    
    /* Modo oscuro */
    @media (prefers-color-scheme: dark) {
        :root {
            --bg-primary: #0e1117;
            --bg-secondary: #262730;
            --text-primary: #ffffff;
            --text-secondary: #a0a0a0;
            --border-color: #30363d;
            --success-bg: #0d4429;
            --success-text: #4caf50;
            --success-border: #2ea043;
            --warning-bg: #332b00;
            --warning-text: #ffeb3b;
            --warning-border: #ffd700;
            --error-bg: #4a1c1c;
            --error-text: #ff6b6b;
            --error-border: #dc3545;
        }
    }
    
    /* Detectar tema de Streamlit */
    [data-theme="dark"], .stApp[data-theme="dark"] {
        --bg-primary: #0e1117;
        --bg-secondary: #262730;
        --text-primary: #ffffff;
        --text-secondary: #a0a0a0;
        --border-color: #30363d;
        --success-bg: #0d4429;
        --success-text: #4caf50;
        --success-border: #2ea043;
        --warning-bg: #332b00;
        --warning-text: #ffeb3b;
        --warning-border: #ffd700;
        --error-bg: #4a1c1c;
        --error-text: #ff6b6b;
        --error-border: #dc3545;
    }

    .main-header {
        background: linear-gradient(90deg, #1f4e79 0%, #2e75b6 100%);
        color: white !important;
        padding: 1.5rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        text-align: center;
    }
    
    .step-container {
        background: var(--bg-primary) !important;
        color: var(--text-primary) !important;
        padding: 1.5rem;
        border-radius: 10px;
        border: 1px solid var(--border-color);
        margin-bottom: 1.5rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    .status-success {
        background: var(--success-bg) !important;
        color: var(--success-text) !important;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
        text-align: center;
        border: 1px solid var(--success-border);
    }
    
    .status-warning {
        background: var(--warning-bg) !important;
        color: var(--warning-text) !important;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
        text-align: center;
        border: 1px solid var(--warning-border);
    }
    
    .status-error {
        background: var(--error-bg) !important;
        color: var(--error-text) !important;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
        text-align: center;
        border: 1px solid var(--error-border);
    }
    
    .upload-zone {
        background: var(--bg-secondary) !important;
        color: var(--text-secondary) !important;
        border: 2px dashed var(--border-color);
        border-radius: 8px;
        padding: 1.5rem;
        text-align: center;
        margin: 1rem 0;
    }
    
    .upload-zone:hover {
        border-color: #2196f3 !important;
        background: rgba(33, 150, 243, 0.1) !important;
    }
    
    .metrics-container {
        background: var(--bg-secondary) !important;
        color: var(--text-primary) !important;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
        border: 1px solid var(--border-color);
    }
    
    /* Fix para texto en contenedores */
    .step-container h1, .step-container h2, .step-container h3, .step-container h4, .step-container h5, .step-container h6 {
        color: var(--text-primary) !important;
    }
    
    .step-container p, .step-container span, .step-container div {
        color: var(--text-primary) !important;
    }
    
    /* Fix específico para modo oscuro de Streamlit */
    .stApp[theme-base="dark"] .step-container {
        background: #262730 !important;
        color: #ffffff !important;
        border: 1px solid #30363d !important;
    }
    
    .stApp[theme-base="dark"] .upload-zone {
        background: #1a1a1a !important;
        color: #ffffff !important;
        border: 2px dashed #444 !important;
    }
</style>

<script>
// Detectar tema automáticamente
function detectTheme() {
    const streamlitDoc = window.parent.document;
    const isDark = streamlitDoc.querySelector('[data-theme="dark"]') || 
                   streamlitDoc.body.classList.contains('dark') ||
                   window.matchMedia('(prefers-color-scheme: dark)').matches;
    
    if (isDark) {
        document.documentElement.setAttribute('data-theme', 'dark');
    } else {
        document.documentElement.setAttribute('data-theme', 'light');
    }
}

// Ejecutar al cargar y cuando cambie el tema
detectTheme();
new MutationObserver(detectTheme).observe(window.parent.document.body, {
    attributes: true,
    subtree: true
});
</script>
""", unsafe_allow_html=True)

# Header principal
st.markdown("""
<div class="main-header">
    <h1>📊 Dash Ausentismos Nómina</h1>
    <p><strong>Creado por Jeysshon</strong> | Grupo Jerónimo Martins</p>
</div>
""", unsafe_allow_html=True)

# Crear carpetas temporales
os.makedirs("temp", exist_ok=True)
os.makedirs("salidas", exist_ok=True)

# PASO 1: VALIDACIÓN
st.markdown('<div class="step-container">', unsafe_allow_html=True)
st.header("🔍 Paso 1: Validación de Ausentismos")

col1, col2 = st.columns(2)

with col1:
    st.markdown("### 📂 Base de Diagnósticos")
    archivo_base = st.file_uploader(
        "Sube archivo Excel (.xlsx)",
        type=['xlsx', 'xls'],
        key="base"
    )
    if archivo_base:
        st.success("✅ Archivo cargado")

with col2:
    st.markdown("### 📊 Reporte 45")
    archivo_reporte = st.file_uploader(
        "Sube archivo Excel (.xlsx)", 
        type=['xlsx', 'xls'],
        key="reporte"
    )
    if archivo_reporte:
        st.success("✅ Archivo cargado")

# Procesar validación
if archivo_base and archivo_reporte:
    st.markdown('<div class="status-success"><h3>🎯 Archivos listos - Procesar validación</h3></div>', unsafe_allow_html=True)
    
    if st.button("🚀 VALIDAR DATOS", type="primary", use_container_width=True):
        # Crear contenedor para logs
        log_container = st.empty()
        progress_bar = st.progress(0)
        
        try:
            # Log inicial
            log_container.info("🔄 Iniciando validación de datos...")
            progress_bar.progress(10)
            
            # Guardar archivos temporalmente
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            ruta_base = f"temp/base_{timestamp}.xlsx"
            ruta_reporte = f"temp/reporte_{timestamp}.xlsx"
            
            log_container.info("💾 Guardando archivos temporalmente...")
            progress_bar.progress(20)
            
            with open(ruta_base, "wb") as f:
                f.write(archivo_base.getvalue())
            with open(ruta_reporte, "wb") as f:
                f.write(archivo_reporte.getvalue())
            
            log_container.info("✅ Archivos guardados, iniciando procesamiento...")
            progress_bar.progress(30)
            
            # Ejecutar validación con logs
            log_container.info("🔍 Ejecutando validar_ausentismos_original...")
            log_container.info("📊 Leyendo base de diagnósticos...")
            progress_bar.progress(50)
            
            ruta_validado = validar_ausentismos_original(ruta_base, ruta_reporte)
            
            log_container.info("📈 Combinando datos del reporte...")
            progress_bar.progress(70)
            
            if ruta_validado:
                log_container.info("📋 Normalizando columnas y formatos...")
                progress_bar.progress(85)
                
                # Leer resultado
                df_validado = pd.read_csv(ruta_validado, encoding='utf-8-sig')
                
                log_container.success(f"✅ Validación completada: {len(df_validado):,} registros procesados")
                progress_bar.progress(100)
                
                st.success(f"🎉 Proceso terminado - {len(df_validado):,} registros validados")
                
                # DESCARGA AUTOMÁTICA DEL PASO 1
                csv_data = df_validado.to_csv(index=False, encoding='utf-8-sig')
                nombre_descarga = f"datos_validados_{timestamp}.csv"
                
                st.download_button(
                    label="📥 DESCARGAR DATOS VALIDADOS",
                    data=csv_data,
                    file_name=nombre_descarga,
                    mime="text/csv",
                    type="primary",
                    use_container_width=True
                )
                
                # Guardar en session_state SOLO PARA REFERENCIA (no necesario para Paso 2)
                st.session_state['ultimo_timestamp'] = timestamp
                
            else:
                log_container.error("❌ Error: No se pudo completar la validación")
                progress_bar.progress(0)
            
            # Limpiar archivos temporales
            log_container.info("🧹 Limpiando archivos temporales...")
            for archivo in [ruta_base, ruta_reporte]:
                if os.path.exists(archivo):
                    os.remove(archivo)
            
            log_container.success("🎯 Proceso completado - Archivos temporales eliminados")
                    
        except Exception as e:
            log_container.error(f"💥 Error durante el procesamiento: {str(e)}")
            progress_bar.progress(0)
            st.error(f"❌ Error: {str(e)}")
            st.exception(e)

elif archivo_base or archivo_reporte:
    st.markdown('<div class="status-warning"><h4>⚠️ Sube ambos archivos para continuar</h4></div>', unsafe_allow_html=True)
else:
    st.markdown('<div class="upload-zone"><h3>📁 Sube los 2 archivos Excel</h3><p>Base de diagnósticos + Reporte 45</p></div>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# PASO 2: AGREGAR TIENDAS - COMPLETAMENTE INDEPENDIENTE
st.markdown('<div class="step-container">', unsafe_allow_html=True)
st.header("🏪 Paso 2: Agregar Tiendas")

# LIMPIAR CUALQUIER MIERDA DEL SESSION STATE
if st.button("🧹 LIMPIAR TODO", type="secondary"):
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.success("✅ Session limpiado - Ahora sube tus archivos")
    st.rerun()

st.markdown("""
<div style="background: #d1ecf1; padding: 1rem; border-radius: 8px; margin-bottom: 1rem; border-left: 4px solid #17a2b8;">
    <h4 style="margin-top: 0; color: #0c5460;">💡 Proceso independiente</h4>
    <p style="margin-bottom: 0;">Sube tu CSV del Paso 1 + Excel de tiendas. No usa nada guardado en memoria.</p>
</div>
""", unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    st.markdown("### 📊 CSV Validado (Paso 1)")
    archivo_validado = st.file_uploader(
        "Sube el CSV que descargaste del Paso 1",
        type=['csv'],
        key="validado_csv_independiente",
        help="El archivo CSV que descargaste del Paso 1"
    )
    if archivo_validado:
        st.success("✅ CSV validado cargado")
        # Mostrar info del archivo
        try:
            import io
            df_preview = pd.read_csv(io.BytesIO(archivo_validado.getvalue()), nrows=0)
            st.info(f"📋 Columnas detectadas: {len(df_preview.columns)}")
        except:
            st.warning("⚠️ No se pudo leer el preview del CSV")

with col2:
    st.markdown("### 🏪 Excel de Tiendas")
    archivo_tiendas = st.file_uploader(
        "Sube el Excel con datos de tiendas",
        type=['xlsx', 'xls'],
        key="tiendas_independiente",
        help="Archivo Excel con información de tiendas y centros de coste"
    )
    if archivo_tiendas:
        st.success("✅ Excel de tiendas cargado")
        # Mostrar info del archivo
        try:
            df_tiendas_preview = pd.read_excel(io.BytesIO(archivo_tiendas.getvalue()), nrows=0)
            st.info(f"📋 Columnas detectadas: {len(df_tiendas_preview.columns)}")
        except:
            st.warning("⚠️ No se pudo leer el preview del Excel")

# Procesar tiendas - COMPLETAMENTE INDEPENDIENTE
if archivo_validado and archivo_tiendas:
    st.markdown('<div class="status-success"><h3>🎯 AMBOS ARCHIVOS LISTOS - Procesar independientemente</h3></div>', unsafe_allow_html=True)
    
    if st.button("🔗 PROCESAR TIENDAS (INDEPENDIENTE)", type="primary", use_container_width=True):
        # Crear contenedor para logs
        log_container = st.empty()
        progress_bar = st.progress(0)
        
        try:
            log_container.info("🏪 Iniciando proceso INDEPENDIENTE de tiendas...")
            progress_bar.progress(10)
            
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            
            # Guardar CSV validado temporalmente
            log_container.info("💾 Guardando CSV validado (sin tocar session_state)...")
            progress_bar.progress(20)
            
            ruta_validado_temp = f"temp/csv_validado_{timestamp}.csv"
            with open(ruta_validado_temp, "wb") as f:
                f.write(archivo_validado.getvalue())
            
            log_container.info(f"✅ CSV guardado en: {ruta_validado_temp}")
            
            # Guardar Excel de tiendas temporalmente  
            log_container.info("📊 Guardando Excel de tiendas...")
            progress_bar.progress(30)
            
            ruta_tiendas_temp = f"temp/excel_tiendas_{timestamp}.xlsx"
            with open(ruta_tiendas_temp, "wb") as f:
                f.write(archivo_tiendas.getvalue())
            
            log_container.info(f"✅ Excel guardado en: {ruta_tiendas_temp}")
            
            # Verificar que los archivos existen
            log_container.info("🔍 Verificando archivos guardados...")
            progress_bar.progress(40)
            
            if not os.path.exists(ruta_validado_temp):
                raise Exception(f"No se pudo guardar el CSV en {ruta_validado_temp}")
            if not os.path.exists(ruta_tiendas_temp):
                raise Exception(f"No se pudo guardar el Excel en {ruta_tiendas_temp}")
            
            log_container.info("✅ Archivos verificados, ejecutando función de tiendas...")
            progress_bar.progress(50)
            
            # Ejecutar agregado de tiendas - FUNCIÓN ORIGINAL DEL GITHUB
            ruta_final = f"salidas/reporte_tiendas_{timestamp}.csv"
            
            log_container.info("🔗 Ejecutando agregar_tiendas_modificado (GitHub)...")
            progress_bar.progress(60)
            
            resultado = agregar_tiendas_modificado(
                ruta_validado_temp,
                ruta_tiendas_temp, 
                ruta_final
            )
            
            progress_bar.progress(80)
            
            if resultado and os.path.exists(resultado):
                log_container.info("📊 Leyendo resultado final...")
                
                # Leer resultado final
                df_final = pd.read_csv(resultado, encoding='utf-8-sig')
                
                # 🔥 FORZAR LIMPIEZA DE value_tienda AQUÍ EN LA APP
                if 'value_tienda' in df_final.columns:
                    log_container.info("🔧 FORZANDO limpieza de value_tienda en la app...")
                    
                    # Función para quitar SOLO el último 0
                    def quitar_ultimo_cero_forzado(valor):
                        valor_str = str(valor)
                        if valor_str.endswith('0') and len(valor_str) > 1:
                            return valor_str[:-1]  # Quitar solo el último carácter
                        return valor_str
                    
                    # ANTES de limpiar
                    antes = df_final['value_tienda'].head(5).tolist()
                    log_container.info(f"🔍 ANTES de limpiar: {antes}")
                    
                    # LIMPIAR FORZADO
                    df_final['value_tienda'] = df_final['value_tienda'].apply(quitar_ultimo_cero_forzado)
                    
                    # DESPUÉS de limpiar
                    despues = df_final['value_tienda'].head(5).tolist()
                    log_container.info(f"✅ DESPUÉS de limpiar: {despues}")
                
                log_container.success(f"✅ PROCESO GITHUB + LIMPIEZA FORZADA: {len(df_final):,} registros")
                progress_bar.progress(95)
                
                st.success(f"🎉 ¡ÉXITO CON CÓDIGO GITHUB! - {len(df_final):,} registros procesados")
                
                # VERIFICAR LA COLUMNA value_tienda
                if 'value_tienda' in df_final.columns:
                    sample_values = df_final['value_tienda'].head(10).tolist()
                    st.info(f"🔍 Muestra value_tienda: {sample_values}")
                
                # GUARDAR EL ARCHIVO CORREGIDO
                csv_final = df_final.to_csv(index=False, encoding='utf-8-sig')
                
                # También guardar archivo corregido en disco
                ruta_corregida = f"salidas/reporte_tiendas_corregido_{timestamp}.csv"
                df_final.to_csv(ruta_corregida, index=False, encoding='utf-8-sig')
                log_container.info(f"💾 Archivo corregido guardado: {ruta_corregida}")
                
                st.download_button(
                    label="📥 DESCARGAR REPORTE CORREGIDO",
                    data=csv_final,
                    file_name=f"reporte_tiendas_corregido_{timestamp}.csv",
                    mime="text/csv",
                    type="primary",
                    use_container_width=True
                )
                
                # Métricas
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("📊 Registros", f"{len(df_final):,}")
                with col2:
                    if 'nombre_tienda' in df_final.columns:
                        con_tienda = (df_final['nombre_tienda'] != '').sum()
                        st.metric("🏪 Con Tienda", f"{con_tienda:,}")
                with col3:
                    st.metric("📋 Columnas", len(df_final.columns))
                
                progress_bar.progress(100)
                log_container.success("🎯 ¡TODO LISTO! Archivo descargable generado")
                st.balloons()
                
            else:
                log_container.error("❌ ERROR: No se generó el archivo final")
                st.error("No se pudo generar el resultado")
            
            # Limpiar archivos temporales
            log_container.info("🧹 Limpiando archivos temporales...")
            for archivo in [ruta_validado_temp, ruta_tiendas_temp]:
                if os.path.exists(archivo):
                    os.remove(archivo)
                    log_container.info(f"🗑️ Eliminado: {archivo}")
            
            log_container.success("✨ Limpieza completada")
                    
        except Exception as e:
            log_container.error(f"💥 ERROR: {str(e)}")
            progress_bar.progress(0)
            st.error(f"❌ Error: {str(e)}")
            
            # Mostrar detalles del error
            st.markdown("### 🔍 Detalles del error:")
            st.exception(e)

elif archivo_validado and not archivo_tiendas:
    st.markdown('<div class="status-warning"><h4>⚠️ Falta el Excel de tiendas</h4></div>', unsafe_allow_html=True)
elif not archivo_validado and archivo_tiendas:
    st.markdown('<div class="status-warning"><h4>⚠️ Falta el CSV validado</h4></div>', unsafe_allow_html=True)
else:
    st.markdown('<div class="upload-zone"><h3>📁 Sube los 2 archivos INDEPENDIENTES</h3><p>CSV del Paso 1 + Excel de tiendas</p></div>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# SIDEBAR SIMPLIFICADO
with st.sidebar:
    st.markdown("### 📋 Proceso")
    st.markdown("""
    **1. Validación**
    - Sube base + reporte
    - Descarga datos validados
    
    **2. Tiendas**  
    - Sube archivo tiendas
    - Descarga reporte final
    """)
    
    st.markdown("---")
    st.markdown("### 👤 Info")
    st.markdown("""
    **Desarrollador:** Jeysshon  
    **Empresa:** Grupo Jerónimo Martins  
    **Versión:** 2.1
    """)
    
    if st.button("🗑️ Limpiar", use_container_width=True):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; padding: 1rem;">
    <p><strong>Dash Ausentismos Nómina</strong> | Jeysshon - Grupo Jerónimo Martins</p>
</div>
""", unsafe_allow_html=True)
