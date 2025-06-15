# 🏥 Sistema de Detección de Violencia Intrafamiliar

Una aplicación web desarrollada con **Python Flask** para detectar y prevenir la violencia intrafamiliar en el sistema público de salud (SAR, CESFAM, urgencias).

---

## 🚀 Características

- ✅ Evaluación de **6 preguntas clave** sobre violencia intrafamiliar.
- ✅ **Sistema de puntajes** (0-18) con clasificación automática:
  - 🟢 Leve: 0-5 puntos
  - 🟡 Moderado: 6-11 puntos
  - 🔴 Grave: 12-18 puntos
- ✅ Opción de **encuesta anónima**
- ✅ **Dashboard interactivo** con estadísticas en tiempo real
- ✅ Compatible con **SQLite (local)** y **PostgreSQL (Railway)**
- ✅ Diseño **responsive** (móviles + desktop)

---

## 📋 Requisitos

- Python 3.8 o superior
- pip (gestor de paquetes Python)

---

## 🛠️ Instalación y Ejecución

### 1. Clonar el proyecto

```bash
git clone https://github.com/belehp/encuesta-web.git
cd encuesta-web
```

### 2. Crear y activar entorno virtual

```bash
# Crear
python -m venv venv

# Activar (Windows)
venv\Scripts\activate

# Activar (macOS / Linux)
source venv/bin/activate
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 4. Crear archivo `.env` en la raíz del proyecto

Crea un archivo llamado `.env` con este contenido (reemplaza con tus datos reales de Railway):

```
DATABASE_URL=postgresql://usuario:contraseña@host:puerto/nombre_db
```

### 5. Ejecutar la aplicación

#### Opción A: Automático (Windows)

```bash
ejecutar.bat
```

#### Opción B: Manual

```bash
# Inicializar la base de datos
python crear_db_nueva.py

# Ejecutar aplicación
python run_local.py
```

### 6. Abrir en el navegador

```text
http://127.0.0.1:5000
```

---

## 📁 Estructura del Proyecto

```text
encuesta-web/
├── run_local.py           # Aplicación principal Flask
├── crear_db_nueva.py      # Script para crear la base de datos
├── requirements.txt       # Dependencias Python
├── ejecutar.bat           # Script de ejecución (Windows)
├── .env                   # Variables de entorno (no se sube)
├── templates/             # Archivos HTML
│   ├── base.html
│   ├── index.html
│   ├── survey.html
│   ├── dashboard.html
│   └── mision.html
├── static/                # Archivos estáticos
│   ├── style.css
│   └── script.js
└── survey_local.db        # Base de datos local (si usas SQLite)
```

---

## 🔐 Ignorar archivo `.env` (importante)

Agrega esto a tu archivo `.gitignore` para evitar subir el `.env`:

```
.env
```

---

## 🧠 Base de Datos

### Tablas:

- `questions`: preguntas de la encuesta
- `options`: opciones de respuesta
- `users`: datos personales (solo si no es anónima)
- `responses`: respuestas a la encuesta

---

## 🧪 Clasificación automática

```python
if puntaje_total <= 5:
    clasificacion = 'Leve'
elif puntaje_total <= 11:
    clasificacion = 'Moderado'
else:
    clasificacion = 'Grave'
```

---

## 📊 Dashboard

- Gráfico de género (azul, rosa, gris, verde)
- Gráfico de clasificación de riesgo (verde, amarillo, rojo)
- Totales y porcentajes por pregunta

---

## 🛠 Personalización

### Cambiar preguntas:

Edita `crear_db_nueva.py` y vuelve a ejecutar:

```bash
python crear_db_nueva.py
```

### Modificar estilos:

Edita `static/style.css`.

---

## 🚀 Deploy

Puedes hacer deploy con:

- **Railway** → base de datos PostgreSQL
- **Vercel / Render / Heroku** → backend Flask

---

## 📞 Soporte

Esta aplicación está diseñada para apoyar a profesionales de la salud en Chile ante casos de violencia intrafamiliar en urgencias, CESFAM o SAR.

---

## 🎉 ¡Listo para usar!

1. Evaluá el riesgo  
2. Clasificá el nivel de gravedad  
3. Visualizá estadísticas claras  
4. Protegé a tus pacientes

---