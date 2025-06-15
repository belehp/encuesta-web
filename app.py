from flask import Flask, render_template, request, jsonify, redirect, url_for
import psycopg2
from psycopg2.extras import RealDictCursor
import os
from datetime import datetime
import json
from urllib.parse import urlparse
from flask_cors import CORS

app = Flask(__name__)

CORS(app)

# Configuración de la base de datos para Railway
DATABASE_URL = os.environ.get('DATABASE_URL')

# Si no hay DATABASE_URL (desarrollo local), usar SQLite como fallback
if not DATABASE_URL:
    DATABASE_URL = 'sqlite:///survey_local.db'
    USE_SQLITE = True
else:
    USE_SQLITE = False

def get_db_connection():
    if USE_SQLITE:
        import sqlite3
        conn = sqlite3.connect('survey_local.db')
        conn.row_factory = sqlite3.Row
        return conn
    else:
        conn = psycopg2.connect(DATABASE_URL)
        return conn

def init_db():
    """Inicializar la base de datos con datos de ejemplo"""
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        # Crear tablas si no existen (compatible con SQLite y PostgreSQL)
        if USE_SQLITE:
            # Crear tablas para SQLite
            cur.execute('''
                CREATE TABLE IF NOT EXISTS questions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    texto TEXT NOT NULL
                )
            ''')
            
            cur.execute('''
                CREATE TABLE IF NOT EXISTS options (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    pregunta_id INTEGER,
                    texto TEXT NOT NULL,
                    puntaje INTEGER NOT NULL DEFAULT 0,
                    FOREIGN KEY (pregunta_id) REFERENCES questions (id)
                )
            ''')
            
            cur.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nombre TEXT NOT NULL,
                    email TEXT NOT NULL,
                    edad INTEGER NOT NULL,
                    sexo TEXT NOT NULL,
                    puntaje_total INTEGER DEFAULT 0,
                    clasificacion TEXT DEFAULT 'leve',
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            cur.execute('''
                CREATE TABLE IF NOT EXISTS responses (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    pregunta_id INTEGER,
                    respuesta INTEGER,
                    puntaje INTEGER DEFAULT 0,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id),
                    FOREIGN KEY (pregunta_id) REFERENCES questions (id),
                    FOREIGN KEY (respuesta) REFERENCES options (id)
                )
            ''')
        else:
            # Crear tablas para PostgreSQL
            cur.execute('''
                CREATE TABLE IF NOT EXISTS questions (
                    id SERIAL PRIMARY KEY,
                    texto TEXT NOT NULL
                )
            ''')
            
            cur.execute('''
                CREATE TABLE IF NOT EXISTS options (
                    id SERIAL PRIMARY KEY,
                    pregunta_id INTEGER REFERENCES questions(id) ON DELETE CASCADE,
                    texto TEXT NOT NULL,
                    puntaje INTEGER NOT NULL DEFAULT 0
                )
            ''')
            
            cur.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id SERIAL PRIMARY KEY,
                    nombre VARCHAR(255) NOT NULL,
                    email VARCHAR(255) NOT NULL,
                    edad INTEGER NOT NULL,
                    sexo VARCHAR(50) NOT NULL,
                    puntaje_total INTEGER DEFAULT 0,
                    clasificacion VARCHAR(50) DEFAULT 'leve',
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            cur.execute('''
                CREATE TABLE IF NOT EXISTS responses (
                    id SERIAL PRIMARY KEY,
                    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
                    pregunta_id INTEGER REFERENCES questions(id) ON DELETE CASCADE,
                    respuesta INTEGER REFERENCES options(id) ON DELETE CASCADE,
                    puntaje INTEGER DEFAULT 0,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')

        # Insertar preguntas de ejemplo si no existen
        cur.execute("SELECT COUNT(*) FROM questions")
        count = cur.fetchone()[0] if USE_SQLITE else cur.fetchone()[0]
        
        if count == 0:
            questions = [
                "¿Cómo describirías el ambiente en tu hogar?",
                "¿Te han hecho sentir miedo, humillado/a o culpable dentro de tu familia recientemente?",
                "¿Te han hecho sentir miedo con miradas, gestos o silencios prolongados?",
                "¿A quién acudirías si te sintieras en peligro dentro de tu hogar?",
                "¿Alguna vez alguien en tu familia te ha golpeado, empujado o agredido físicamente?",
                "¿Has presenciado actos de violencia hacia ti u otros miembros de tu familia?"
            ]
            
            for i, question in enumerate(questions, 1):
                if USE_SQLITE:
                    cur.execute("INSERT INTO questions (texto) VALUES (?)", (question,))
                else:
                    cur.execute("INSERT INTO questions (id, texto) VALUES (%s, %s)", (i, question))
            
            # Insertar opciones para cada pregunta con puntajes
            options = [
                # Pregunta 1 - Ambiente en el hogar
                (1, "Tranquilo y de respeto mutuo", 0),
                (1, "A veces tenso, con discusiones esporádicas", 1),
                (1, "Frecuentemente hay gritos, insultos o agresiones", 2),
                (1, "Me siento incómodo/a o inseguro/a en casa", 3),
                
                # Pregunta 2 - Miedo, humillación, culpa
                (2, "No, nunca", 0),
                (2, "A veces, pero no sé si es normal", 1),
                (2, "Sí, con frecuencia", 2),
                (2, "Sí, siempre", 3),
                
                # Pregunta 3 - Miedo con gestos
                (3, "No, nunca", 0),
                (3, "A veces", 1),
                (3, "Sí, frecuentemente", 2),
                (3, "Sí, constantemente", 3),
                
                # Pregunta 4 - A quién acudir
                (4, "A un amigo/familiar de confianza", 0),
                (4, "A un profesional de salud, asistente social o Carabineros", 1),
                (4, "No sabría qué hacer", 2),
                (4, "No tengo a quién acudir", 3),
                
                # Pregunta 5 - Agresión física
                (5, "No, nunca", 0),
                (5, "Una vez, en una situación puntual", 1),
                (5, "Varias veces", 2),
                (5, "Sí, actualmente ocurre", 3),
                
                # Pregunta 6 - Presenciar violencia
                (6, "No", 0),
                (6, "Sí, una vez", 1),
                (6, "Varias veces", 2),
                (6, "Sí, recientemente", 3)
            ]
            
            for question_id, texto, puntaje in options:
                if USE_SQLITE:
                    cur.execute("INSERT INTO options (pregunta_id, texto, puntaje) VALUES (?, ?, ?)", 
                              (question_id, texto, puntaje))
                else:
                    cur.execute("INSERT INTO options (pregunta_id, texto, puntaje) VALUES (%s, %s, %s)", 
                              (question_id, texto, puntaje))
        
        conn.commit()
    except Exception as e:
        print(f"Error inicializando DB: {e}")
        conn.rollback()
    finally:
        cur.close()
        conn.close()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/mision')
def mision():
    return render_template('mision.html')

@app.route('/survey')
def survey():
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor) if not USE_SQLITE else conn.cursor()
    
    # Obtener preguntas y opciones
    if USE_SQLITE:
        cur.execute("SELECT id, texto as pregunta FROM questions ORDER BY id")
        questions_data = cur.fetchall()
        
        questions = []
        for q in questions_data:
            cur.execute("SELECT id, texto FROM options WHERE pregunta_id = ? ORDER BY id", (q['id'],))
            opciones = cur.fetchall()
            questions.append({
                'id': q['id'],
                'pregunta': q['pregunta'],
                'opciones': [{'id': o['id'], 'texto': o['texto']} for o in opciones]
            })
    else:
        cur.execute("""
            SELECT q.id, q.texto as pregunta, 
                   array_agg(json_build_object('id', o.id, 'texto', o.texto) ORDER BY o.id) as opciones
            FROM questions q
            LEFT JOIN options o ON q.id = o.pregunta_id
            GROUP BY q.id, q.texto
            ORDER BY q.id
        """)
        questions = cur.fetchall()
    
    cur.close()
    conn.close()
    
    return render_template('survey.html', questions=questions)

@app.route('/dashboard')
def dashboard():
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor) if not USE_SQLITE else conn.cursor()
    
    try:
        # Total de ENCUESTAS COMPLETADAS (ahora todas están en users)
        cur.execute("SELECT COUNT(*) as total FROM users")
        result = cur.fetchone()
        total_surveys = result[0] if USE_SQLITE else result['total']
        
        # Estadísticas por género CON PORCENTAJES (incluye anónimos como "Prefiero no decirlo")
        if USE_SQLITE:
            cur.execute("SELECT sexo, COUNT(*) as count FROM users GROUP BY sexo")
            gender_data = cur.fetchall()
        else:
            cur.execute("SELECT sexo, COUNT(*) as count FROM users GROUP BY sexo")
            gender_data = cur.fetchall()
        
        # Calcular porcentajes de género
        total_users = sum(row['count'] for row in gender_data)
        gender_stats = []
        for row in gender_data:
            percentage = (row['count'] / total_users * 100) if total_users > 0 else 0
            gender_stats.append({
                'sexo': row['sexo'],
                'count': row['count'],
                'percentage': round(percentage, 1)
            })
        
        # Contar encuestas anónimas para el porcentaje
        if USE_SQLITE:
            cur.execute("SELECT COUNT(*) as count FROM users WHERE nombre = 'Anónimo'")
            result = cur.fetchone()
            total_anonymous = result['count'] if result else 0
        else:
            cur.execute("SELECT COUNT(*) as count FROM users WHERE nombre = 'Anónimo'")
            result = cur.fetchone()
            total_anonymous = result['count'] if result else 0
        
        # Porcentaje de encuestas anónimas
        anonymous_percentage = (total_anonymous / total_surveys * 100) if total_surveys > 0 else 0
        
        # Estadísticas de CLASIFICACIÓN (incluye anónimos)
        if USE_SQLITE:
            cur.execute("""
                SELECT clasificacion, COUNT(*) as count
                FROM users 
                GROUP BY clasificacion
            """)
            classification_data = cur.fetchall()
        else:
            cur.execute("""
                SELECT clasificacion, COUNT(*) as count
                FROM users 
                GROUP BY clasificacion
            """)
            classification_data = cur.fetchall()
        
        # Calcular porcentajes de clasificación
        total_classified = sum(row['count'] for row in classification_data)
        classification_stats = []
        for row in classification_data:
            percentage = (row['count'] / total_classified * 100) if total_classified > 0 else 0
            classification_stats.append({
                'clasificacion': row['clasificacion'],
                'count': row['count'],
                'percentage': round(percentage, 1)
            })
        
        # Estadísticas por pregunta (sin cambios)
        if USE_SQLITE:
            cur.execute("""
                SELECT q.id, q.texto as pregunta,
                       o.id as option_id, o.texto as opcion, o.puntaje,
                       COUNT(r.id) as count
                FROM questions q
                LEFT JOIN options o ON q.id = o.pregunta_id
                LEFT JOIN responses r ON o.id = r.respuesta
                GROUP BY q.id, q.texto, o.id, o.texto, o.puntaje
                ORDER BY q.id, o.id
            """)
            question_stats = cur.fetchall()
        else:
            cur.execute("""
                SELECT q.id, q.texto as pregunta,
                       o.id as option_id, o.texto as opcion, o.puntaje,
                       COUNT(r.id) as count
                FROM questions q
                LEFT JOIN options o ON q.id = o.pregunta_id
                LEFT JOIN responses r ON o.id = r.respuesta
                GROUP BY q.id, q.texto, o.id, o.texto, o.puntaje
                ORDER BY q.id, o.id
            """)
            question_stats = cur.fetchall()
        
        # Organizar estadísticas por pregunta
        questions_data = {}
        for stat in question_stats:
            q_id = stat['id'] if not USE_SQLITE else stat[0]
            pregunta = stat['pregunta'] if not USE_SQLITE else stat[1]
            opcion = stat['opcion'] if not USE_SQLITE else stat[3]
            count = stat['count'] if not USE_SQLITE else stat[4]
            
            if q_id not in questions_data:
                questions_data[q_id] = {
                    'pregunta': pregunta,
                    'opciones': [],
                    'total_responses': 0
                }
            
            questions_data[q_id]['opciones'].append({
                'opcion': opcion,
                'puntaje': stat['puntaje'] if not USE_SQLITE else stat[4],
                'count': count
            })
            questions_data[q_id]['total_responses'] += count
        
        # Calcular porcentajes
        for q_data in questions_data.values():
            total = q_data['total_responses']
            for opcion in q_data['opciones']:
                opcion['percentage'] = (opcion['count'] / total * 100) if total > 0 else 0
        
    except Exception as e:
        print(f"Error en dashboard: {e}")
        total_surveys = 0
        gender_stats = []
        anonymous_percentage = 0
        classification_stats = []
        questions_data = {}
    
    finally:
        cur.close()
        conn.close()
    
    return render_template('dashboard.html', 
                         total_surveys=total_surveys,
                         gender_stats=gender_stats,
                         anonymous_percentage=anonymous_percentage,
                         classification_stats=classification_stats,
                         questions_data=questions_data)

@app.route('/api/submit-survey', methods=['POST'])
def submit_survey():
    data = request.json
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        user_id = None
        puntaje_total = 0
        
        # Calcular puntaje total primero
        for question_id, option_id in data['responses'].items():
            if USE_SQLITE:
                cur.execute("SELECT puntaje FROM options WHERE id = ?", (int(option_id),))
            else:
                cur.execute("SELECT puntaje FROM options WHERE id = %s", (int(option_id),))
            result = cur.fetchone()
            if result:
                puntaje_total += result[0] if USE_SQLITE else result['puntaje']
        
        # Determinar clasificación
        if puntaje_total <= 5:
            clasificacion = 'Leve'
        elif puntaje_total <= 11:
            clasificacion = 'Moderado'
        else:
            clasificacion = 'Grave'
        
        # CREAR USUARIO SIEMPRE (anónimo o no)
        if data.get('is_anonymous'):
            # Para encuestas anónimas, usar datos genéricos
            if USE_SQLITE:
                cur.execute("""
                    INSERT INTO users (nombre, email, edad, sexo, puntaje_total, clasificacion, timestamp)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    "Anónimo",
                    "anonimo@encuesta.com",
                    0,  # Edad genérica
                    "Prefiero no decirlo",  # Género para anónimos
                    puntaje_total,
                    clasificacion,
                    datetime.now()
                ))
                user_id = cur.lastrowid
            else:
                cur.execute("""
                    INSERT INTO users (nombre, email, edad, sexo, puntaje_total, clasificacion, timestamp)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    RETURNING id
                """, (
                    "Anónimo",
                    "anonimo@encuesta.com",
                    0,  # Edad genérica
                    "Prefiero no decirlo",  # Género para anónimos
                    puntaje_total,
                    clasificacion,
                    datetime.now()
                ))
                user_id = cur.fetchone()[0]
        else:
            # Para encuestas con datos personales
            if USE_SQLITE:
                cur.execute("""
                    INSERT INTO users (nombre, email, edad, sexo, puntaje_total, clasificacion, timestamp)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    data['nombre'],
                    data['email'],
                    data['edad'],
                    data['sexo'],
                    puntaje_total,
                    clasificacion,
                    datetime.now()
                ))
                user_id = cur.lastrowid
            else:
                cur.execute("""
                    INSERT INTO users (nombre, email, edad, sexo, puntaje_total, clasificacion, timestamp)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    RETURNING id
                """, (
                    data['nombre'],
                    data['email'],
                    data['edad'],
                    data['sexo'],
                    puntaje_total,
                    clasificacion,
                    datetime.now()
                ))
                user_id = cur.fetchone()[0]
        
        # Insertar respuestas con puntajes
        for question_id, option_id in data['responses'].items():
            # Obtener puntaje de la opción
            if USE_SQLITE:
                cur.execute("SELECT puntaje FROM options WHERE id = ?", (int(option_id),))
            else:
                cur.execute("SELECT puntaje FROM options WHERE id = %s", (int(option_id),))
            result = cur.fetchone()
            puntaje_respuesta = result[0] if USE_SQLITE and result else (result['puntaje'] if result else 0)
            
            if USE_SQLITE:
                cur.execute("""
                    INSERT INTO responses (user_id, pregunta_id, respuesta, puntaje)
                    VALUES (?, ?, ?, ?)
                """, (user_id, int(question_id), int(option_id), puntaje_respuesta))
            else:
                cur.execute("""
                    INSERT INTO responses (user_id, pregunta_id, respuesta, puntaje)
                    VALUES (%s, %s, %s, %s)
                """, (user_id, int(question_id), int(option_id), puntaje_respuesta))
        
        conn.commit()
        return jsonify({
            'success': True, 
            'puntaje': puntaje_total, 
            'clasificacion': clasificacion
        })
        
    except Exception as e:
        conn.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        cur.close()
        conn.close()

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    init_db()
    app.run(host='0.0.0.0', port=port)

if __name__ != "__main__":
    init_db()
