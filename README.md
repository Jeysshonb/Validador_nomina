# 📊 Dash Ausentismos Nómina

**Creado por Jeysshon** | Grupo Jerónimo Martins

Sistema completo de validación y procesamiento de datos de ausentismos con interfaz web intuitiva. Procesa datos en 2 pasos simples con descargas disponibles en cada nivel.

## 🚀 Características Principales

- ✅ **Validación automática** de datos de ausentismos
- 🏪 **Integración con datos de tiendas** por centro de coste
- 📊 **Estadísticas en tiempo real** y análisis de completitud
- 💾 **Descargables en cada paso** del proceso
- 🎨 **Interfaz moderna** con diseño profesional
- 📈 **Métricas detalladas** de validación y procesamiento

## 📁 Estructura del Proyecto

```
dash-ausentismos-nomina/
├── app.py                           # 🌐 Aplicación Streamlit principal
├── part1_validation_reporte_45.py   # 🔍 Motor de validación de datos
├── part2_dash_store_total.py        # 🏪 Integración con datos de tiendas
├── requirements.txt                 # 📋 Dependencias del proyecto
├── README.md                        # 📖 Documentación
├── temp/                           # 📁 Archivos temporales (auto-creada)
└── salidas/                        # 📁 Archivos de salida (auto-creada)
```

## 🛠️ Instalación

### Opción 1: Instalación Local

```bash
# 1. Clonar el repositorio
git clone https://github.com/tu-usuario/dash-ausentismos-nomina.git
cd dash-ausentismos-nomina

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. Ejecutar la aplicación
streamlit run app.py
```

### Opción 2: Despliegue en Streamlit Cloud

1. 🍴 Haz fork de este repositorio
2. 🌐 Ve a [share.streamlit.io](https://share.streamlit.io)
3. 🔗 Conecta tu cuenta de GitHub
4. 📂 Selecciona tu repositorio
5. 🚀 ¡Despliega automáticamente!

## 📊 Proceso de Validación

### 🔍 Paso 1: Validación de Ausentismos

**Archivos requeridos:**
- 📂 **Base de Diagnósticos** (Excel): Archivo base con diagnósticos de ausentismos
- 📊 **Reporte 45** (Excel): Reporte principal de ausentismos

**Proceso:**
1. Combina datos de ambos archivos
2. Actualiza campos "Modificado el" y "Modificado por"
3. Normaliza formatos numéricos y nombres de columnas
4. Genera archivo CSV validado

**Salida:**
- 💾 **datos_validados_[timestamp].csv** - Datos combinados y validados

### 🏪 Paso 2: Integración con Tiendas

**Archivos requeridos:**
- 📊 **Archivo de Tiendas** (Excel): Datos de tiendas con centro de coste

**Proceso:**
1. Cruza datos por centro de coste
2. Agrega información de tiendas (nombre, código)
3. Limpia y reordena columnas
4. Genera reporte final completo

**Salida:**
- 💾 **reporte_final_con_tiendas_[timestamp].csv** - Reporte completo

## 📈 Características del Sistema

### 🎯 Funcionalidades Principales

- **Validación inteligente**: Preserva la integridad de datos originales
- **Normalización automática**: Convierte columnas a snake_case sin acentos
- **Limpieza de datos**: Elimina formatos inconsistentes en números
- **Merge inteligente**: Cruza datos por múltiples campos clave
- **Estadísticas en tiempo real**: Métricas de completitud y calidad

### 📊 Métricas Disponibles

- **Total de registros** procesados
- **Porcentaje de actualización** de datos
- **Completitud por columna** (nombre_tienda, value_tienda, etc.)
- **Estadísticas de coincidencias** entre archivos
- **Análisis de calidad** de datos

### 💾 Opciones de Descarga

- **Nivel 1**: Datos validados (post-validación)
- **Nivel 2**: Datos completos con tiendas (resultado final)
- **Centro de descargas**: Acceso a todos los archivos generados
- **Formatos**: CSV con encoding UTF-8-sig (compatible con Excel)

## 🔧 Requisitos Técnicos

### Dependencias

```txt
streamlit>=1.28.0
pandas>=2.0.0
numpy>=1.24.0
openpyxl>=3.1.0
```

### Archivos de Entrada

| Archivo | Formato | Descripción |
|---------|---------|-------------|
| Base Diagnósticos | .xlsx/.xls | Contiene diagnósticos base de ausentismos |
| Reporte 45 | .xlsx/.xls | Reporte principal con datos de ausentismos |
| Datos Tiendas | .xlsx/.xls | Información de tiendas por centro de coste |

### Columnas Clave

**Para validación:**
- Número de personal
- Número ID
- Clase absent./pres.
- Inicio de validez
- Fin de validez

**Para tiendas:**
- Centro de coste (CECO)
- myCECO (campo de cruce)

## 🎨 Interfaz de Usuario

### Diseño Moderno
- **Header personalizado** con gradiente corporativo
- **Tarjetas de pasos** con diseño intuitivo
- **Métricas visuales** con iconos y colores
- **Secciones de descarga** destacadas
- **Sidebar informativo** con estadísticas

### Experiencia de Usuario
- **Validación en tiempo real** de archivos
- **Indicadores de progreso** durante procesamiento
- **Mensajes de éxito/error** claros
- **Vista previa de datos** en cada paso
- **Limpieza de sesión** con un clic

## 🚀 Casos de Uso

### Para Recursos Humanos
- Validación mensual de reportes de ausentismos
- Integración de datos de múltiples fuentes
- Generación de reportes ejecutivos

### Para Análisis de Datos
- Limpieza automática de datasets
- Normalización de formatos inconsistentes
- Preparación de datos para análisis avanzado

### Para Operaciones
- Procesamiento masivo de archivos Excel
- Automatización de tareas repetitivas
- Control de calidad de datos

## 🤝 Contribución

¿Quieres contribuir al proyecto?

1. 🍴 Fork el repositorio
2. 🌿 Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. 💾 Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. 📤 Push a la rama (`git push origin feature/AmazingFeature`)
5. 🔄 Abre un Pull Request

## 📞 Soporte

Para soporte técnico o consultas:

- **Desarrollador**: Jeysshon
- **Empresa**: Grupo Jerónimo Martins
- **Departamento**: Sistemas/RRHH

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo `LICENSE` para más detalles.

## 🏆 Reconocimientos

- **Grupo Jerónimo Martins** por proporcionar los requisitos y casos de uso
- **Streamlit** por la excelente plataforma de desarrollo
- **Pandas** por las poderosas herramientas de manipulación de datos

---

<div align="center">

**📊 Dash Ausentismos Nómina** | Desarrollado con ❤️ por **Jeysshon** para **Grupo Jerónimo Martins**

*Sistema de procesamiento y validación de datos de ausentismos | Versión 2.0*

</div>
