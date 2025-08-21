# 🏢 Validador de Ausentismos

Aplicación Streamlit para validar y procesar datos de ausentismos en 2 pasos simples.

## 📁 Archivos del Proyecto

```
validador-ausentismos/
├── app.py                           # Aplicación Streamlit principal
├── part1_validation_reporte_45.py   # Script de validación 
├── part2_dash_store_total.py        # Script de tiendas
├── requirements.txt                 # Dependencias
└── README.md                       # Esta documentación
```

## 🚀 Instalación y Uso

### 1. Clonar repositorio
```bash
git clone https://github.com/tu-usuario/validador-ausentismos.git
cd validador-ausentismos
```

### 2. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 3. Ejecutar aplicación
```bash
streamlit run app.py
```

## 📊 Proceso

### Paso 1: Validación
- Sube **Base de diagnósticos** (Excel)
- Sube **Reporte 45** (Excel) 
- Ejecuta validación → Combina y normaliza datos

### Paso 2: Tiendas
- Sube **Archivo de tiendas** (Excel)
- Agrega información de tiendas por centro de coste
- Descarga resultado final (CSV)

## 🌐 Desplegar en Streamlit Cloud

1. Haz fork de este repo
2. Ve a [share.streamlit.io](https://share.streamlit.io)
3. Conecta con GitHub
4. Selecciona tu repo
5. ¡Despliega!

## 📄 Licencia

MIT License
