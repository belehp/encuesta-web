# 🏥 Sistema de Detección de Violencia Intrafamiliar

Una aplicación web desarrollada con Python Flask para detectar y prevenir la violencia intrafamiliar en el sistema público de salud (SAR, CESFAM, urgencias).

## 🚀 Características

- **Evaluación de 6 preguntas** específicas sobre violencia intrafamiliar
- **Sistema de puntajes** (0-18 puntos) con clasificación automática:
  - 🟢 **Leve**: 0-5 puntos
  - 🟡 **Moderado**: 6-11 puntos  
  - 🔴 **Grave**: 12-18 puntos
- **Encuestas anónimas**: Opción para responder sin proporcionar datos personales
- **Dashboard interactivo**: Gráficos circulares y estadísticas detalladas
- **Diseño responsive**: Compatible con dispositivos móviles y desktop
- **Base de datos SQLite**: Para desarrollo local (fácil de usar)

## 📋 Requisitos

- Python 3.8 o superior
- pip (gestor de paquetes de Python)

## 🛠️ Instalación y Ejecución

### 1. Clonar o descargar el proyecto
\`\`\`bash
# Si tienes git:
git clone [URL_DEL_REPOSITORIO]
cd encuesta-web

# O descargar y extraer el ZIP
\`\`\`

### 2. Crear entorno virtual
\`\`\`bash
# Crear entorno virtual
python -m venv venv

# Activar entorno virtual
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate
\`\`\`

### 3. Instalar dependencias
\`\`\`bash
pip install -r requirements.txt
\`\`\`

### 4. Ejecutar la aplicación

#### Opción A: Usando el script automático (Windows)
\`\`\`cmd
ejecutar.bat
\`\`\`

#### Opción B: Manual
\`\`\`bash
# Crear base de datos nueva
python crear_db_nueva.py

# Ejecutar aplicación
python run_local.py
\`\`\`

### 5. Abrir en el navegador
Visita: http://127.0.0.1:5000

## 📁 Estructura del Proyecto

\`\`\`
encuesta-web/
├── run_local.py           # Aplicación principal Flask
├── crear_db_nueva.py      # Script para crear base de datos
├── requirements.txt       # Dependencias Python
├── ejecutar_nuevo.bat     # Script automático (Windows)
├── README.md             # Este archivo
├── templates/            # Templates HTML
│   ├── base.html         # Template base
│   ├── index.html        # Página principal
│   ├── survey.html       # Formulario de encuesta
│   └── dashboard.html    # Dashboard con gráficos
├── static/               # Archivos estáticos
│   ├── style.css         # Estilos CSS
│   └── script.js         # JavaScript
└── survey_local.db       # Base de datos SQLite (se crea automáticamente)
\`\`\`

## 🗄️ Base de Datos

### Tablas:
- **questions**: 6 preguntas sobre violencia intrafamiliar
- **options**: 4 opciones por pregunta con puntajes (0-3)
- **users**: Datos de usuarios (solo encuestas no anónimas)
- **responses**: Respuestas con puntajes calculados

### Datos incluidos:
- Preguntas específicas para detectar violencia intrafamiliar
- Sistema de puntajes para clasificación de riesgo
- Se crean automáticamente al ejecutar la aplicación

## 🎯 Uso de la Aplicación

### 1. Página Principal (/)
- Información sobre la herramienta
- Botón "Hacer Encuesta"
- Botón "Ver Dashboard"

### 2. Encuesta (/survey)
- Switch para encuesta anónima
- Formulario de datos personales (si no es anónima)
- 6 preguntas con 4 opciones cada una
- Clasificación automática al finalizar

### 3. Dashboard (/dashboard)
- Total de encuestas completadas
- Gráfico circular de distribución por género
- Gráfico circular de clasificación de riesgo
- Estadísticas detalladas por pregunta

## 🎨 Características del Dashboard

- **Gráficos circulares** con colores específicos:
  - Género: Hombre (azul), Mujer (rosa), Otro (gris), Prefiero no decirlo (verde)
  - Riesgo: Leve (verde), Moderado (amarillo), Grave (rojo)
- **Porcentajes** mostrados dentro de cada sector
- **Leyendas** con colores y estadísticas
- **Responsive** para móviles y desktop

## 🔧 Personalización

### Cambiar preguntas:
Modifica el archivo \`crear_db_nueva.py\` y ejecuta:
\`\`\`bash
python crear_db_nueva.py
\`\`\`

### Modificar estilos:
Edita \`static/style.css\` para cambiar la apariencia.

### Ajustar clasificación:
Modifica los rangos de puntaje en \`run_local.py\`:
\`\`\`python
if puntaje_total <= 5:
    clasificacion = 'Leve'
elif puntaje_total <= 11:
    clasificacion = 'Moderado'
else:
    clasificacion = 'Grave'
\`\`\`

## 🐛 Solución de Problemas

### Error "pip no se reconoce":
\`\`\`bash
# Usar la ruta completa:
.\venv\Scripts\pip.exe install -r requirements.txt
\`\`\`

### Error "python no se reconoce":
\`\`\`bash
# Usar la ruta completa:
.\venv\Scripts\python.exe run_local.py
\`\`\`

### Base de datos corrupta:
\`\`\`bash
# Eliminar y recrear:
del survey_local.db
python crear_db_nueva.py
\`\`\`

## 🌐 Deploy en Producción

Para subir a un servidor web, puedes usar:
- **Railway**: Para base de datos PostgreSQL
- **Vercel**: Para hosting de la aplicación
- **Heroku**: Para aplicaciones Python

## 📞 Soporte

Esta herramienta está diseñada para profesionales de la salud en el sistema público chileno (SAR, CESFAM, urgencias) para detectar situaciones de violencia intrafamiliar y orientar la intervención adecuada.

## 🎉 ¡Listo para usar!

Con este sistema podrás:
1. Evaluar riesgo de violencia intrafamiliar
2. Clasificar automáticamente los casos
3. Visualizar estadísticas con gráficos
4. Mantener confidencialidad de los datos

¡La aplicación está lista para ser utilizada en entornos de salud! 🏥
\`\`\`
