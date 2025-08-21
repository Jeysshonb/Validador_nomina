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
        with st.spinner("Procesando..."):
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
                    # Leer resultado
                    df_validado = pd.read_csv(ruta_validado, encoding='utf-8-sig')
                    
                    st.success(f"✅ Validación completada - {len(df_validado):,} registros")
                    
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
                    
                    # Guardar para paso 2 (SIN mostrar estadísticas detalladas)
                    st.session_state['ruta_validado'] = ruta_validado
                    st.session_state['timestamp'] = timestamp
                    
                # Limpiar archivos temporales
                for archivo in [ruta_base, ruta_reporte]:
                    if os.path.exists(archivo):
                        os.remove(archivo)
                        
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")

elif archivo_base or archivo_reporte:
    st.markdown('<div class="status-warning"><h4>⚠️ Sube ambos archivos para continuar</h4></div>', unsafe_allow_html=True)
else:
    st.markdown('<div class="upload-zone"><h3>📁 Sube los 2 archivos Excel</h3><p>Base de diagnósticos + Reporte 45</p></div>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# PASO 2: AGREGAR TIENDAS
st.markdown('<div class="step-container">', unsafe_allow_html=True)
st.header("🏪 Paso 2: Agregar Tiendas")

if 'ruta_validado' not in st.session_state:
    st.markdown('<div class="status-error"><h3>🚫 Completa primero el Paso 1</h3></div>', unsafe_allow_html=True)
else:
    st.markdown('<div class="status-success"><h4>✅ Datos validados listos</h4></div>', unsafe_allow_html=True)
    
    archivo_tiendas = st.file_uploader(
        "📊 Sube archivo Excel de tiendas",
        type=['xlsx', 'xls'],
        key="tiendas"
    )
    
    if archivo_tiendas:
        st.success("✅ Archivo de tiendas cargado")
        
        if st.button("🔗 AGREGAR TIENDAS", type="primary", use_container_width=True):
            with st.spinner("Procesando tiendas..."):
                try:
                    # Usar timestamp del paso 1
                    timestamp = st.session_state.get('timestamp', datetime.now().strftime('%Y%m%d_%H%M%S'))
                    ruta_tiendas = f"temp/tiendas_{timestamp}.xlsx"
                    
                    with open(ruta_tiendas, "wb") as f:
                        f.write(archivo_tiendas.getvalue())
                    
                    # Ejecutar agregado de tiendas
                    ruta_final = f"salidas/reporte_final_{timestamp}.csv"
                    
                    resultado = agregar_tiendas_directo(
                        st.session_state['ruta_validado'],
                        ruta_tiendas,
                        ruta_final
                    )
                    
                    if resultado and os.path.exists(resultado):
                        # Leer resultado final
                        df_final = pd.read_csv(resultado, encoding='utf-8-sig')
                        
                        st.success(f"✅ Tiendas agregadas - {len(df_final):,} registros")
                        
                        # DESCARGA AUTOMÁTICA DEL RESULTADO FINAL
                        csv_final = df_final.to_csv(index=False, encoding='utf-8-sig')
                        
                        st.download_button(
                            label="📥 DESCARGAR REPORTE FINAL",
                            data=csv_final,
                            file_name=f"reporte_final_con_tiendas_{timestamp}.csv",
                            mime="text/csv",
                            type="primary",
                            use_container_width=True
                        )
                        
                        # Mostrar solo métricas básicas
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("📊 Registros", f"{len(df_final):,}")
                        with col2:
                            if 'nombre_tienda' in df_final.columns:
                                con_tienda = (df_final['nombre_tienda'] != '').sum()
                                st.metric("🏪 Con Tienda", f"{con_tienda:,}")
                        with col3:
                            st.metric("📋 Columnas", len(df_final.columns))
                        
                        st.balloons()
                        
                    # Limpiar archivo temporal
                    if os.path.exists(ruta_tiendas):
                        os.remove(ruta_tiendas)
                        
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
    else:
        st.markdown('<div class="upload-zone"><h3>🏪 Sube archivo de tiendas</h3></div>', unsafe_allow_html=True)

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
