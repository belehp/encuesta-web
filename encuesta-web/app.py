from flask import Flask, render_template, request, jsonify, redirect, url_for
import psycopg2
from psycopg2.extras import RealDictCursor
import os
from datetime import datetime
import json
from urllib.parse import urlparse

app = Flask(__name__)

# Configuración de la base de datos para Railway
DATABASE_URL = os.environ.get('DATABASE_URL')

# Si no hay DATABASE_URL (desarrollo local), usar SQLite como fallback
if not DATABASE_URL:
    DATABASE_URL = 'sqlite:///survey.db'
    USE_SQLITE = True
else:
    USE_SQLITE = False

def get_db_connection():
    if USE_SQLITE:
        import sqlite3
        conn = sqlite3.connect('survey.db')
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
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            cur.execute('''
                CREATE TABLE IF NOT EXISTS responses (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    pregunta_id INTEGER,
                    respuesta INTEGER,
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
                    texto TEXT NOT NULL
                )
            ''')
            
            cur.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id SERIAL PRIMARY KEY,
                    nombre VARCHAR(255) NOT NULL,
                    email VARCHAR(255) NOT NULL,
                    edad INTEGER NOT NULL,
                    sexo VARCHAR(50) NOT NULL,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            cur.execute('''
                CREATE TABLE IF NOT EXISTS responses (
                    id SERIAL PRIMARY KEY,
                    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
                    pregunta_id INTEGER REFERENCES questions(id) ON DELETE CASCADE,
                    respuesta INTEGER REFERENCES options(id) ON DELETE CASCADE,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')

        # Insertar preguntas de ejemplo si no existen
        cur.execute("SELECT COUNT(*) FROM questions")
        count = cur.fetchone()[0] if USE_SQLITE else cur.fetchone()[0]
        
        if count == 0:
            questions = [
                "¿Cuál es tu lenguaje de programación favorito?",
                "¿Qué framework web prefieres?",
                "¿Cuántas horas al día programas?"
            ]
            
            for i, question in enumerate(questions, 1):
                if USE_SQLITE:
                    cur.execute("INSERT INTO questions (texto) VALUES (?)", (question,))
                else:
                    cur.execute("INSERT INTO questions (id, texto) VALUES (%s, %s)", (i, question))
            
            # Insertar opciones para cada pregunta
            options = [
                # Pregunta 1
                (1, "Python"),
                (1, "JavaScript"),
                (1, "Java"),
                (1, "C++"),
                # Pregunta 2
                (2, "Flask"),
                (2, "Django"),
                (2, "FastAPI"),
                (2, "Express.js"),
                # Pregunta 3
                (3, "1-2 horas"),
                (3, "3-4 horas"),
                (3, "5-6 horas"),
                (3, "Más de 6 horas")
            ]
            
            for question_id, texto in options:
                if USE_SQLITE:
                    cur.execute("INSERT INTO options (pregunta_id, texto) VALUES (?, ?)", 
                              (question_id, texto))
                else:
                    cur.execute("INSERT INTO options (pregunta_id, texto) VALUES (%s, %s)", 
                              (question_id, texto))
        
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

@app.route('/survey')
def survey():
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor) if not USE_SQLITE else conn.cursor()
    
    # Obtener preguntas y opciones
    if USE_SQLITE:
        cur.execute("""
            SELECT q.id, q.texto as pregunta, 
                   GROUP_CONCAT(JSON_OBJECT('id', o.id, 'texto', o.texto), ',') as opciones
            FROM questions q
            LEFT JOIN options o ON q.id = o.pregunta_id
            GROUP BY q.id, q.texto
            ORDER BY q.id
        """)
        
        questions = []
        for row in cur.fetchall():
            opciones = []
            if row[2]:
                for opt_str in row[2].split(','):
                    opt_dict = json.loads(opt_str)
                    opciones.append(opt_dict)
            questions.append({
                'id': row[0],
                'pregunta': row[1],
                'opciones': opciones
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
    
    # Total de encuestas
    if USE_SQLITE:
        cur.execute("SELECT COUNT(DISTINCT user_id) as total FROM responses WHERE user_id IS NOT NULL")
        total_named = cur.fetchone()[0] if cur.fetchone() else 0
        
        cur.execute("SELECT COUNT(*) as total FROM responses WHERE user_id IS NULL")
        total_anonymous = cur.fetchone()[0] if cur.fetchone() else 0
    else:
        cur.execute("SELECT COUNT(DISTINCT user_id) as total FROM responses WHERE user_id IS NOT NULL")
        total_named = cur.fetchone()['total']
        
        cur.execute("SELECT COUNT(*) as total FROM responses WHERE user_id IS NULL")
        total_anonymous = cur.fetchone()['total']
    
    total_surveys = total_named + total_anonymous
    
    # Porcentaje por sexo (solo usuarios no anónimos)
    if USE_SQLITE:
        cur.execute("""
            SELECT sexo, COUNT(*) as count 
            FROM users 
            GROUP BY sexo
        """)
        gender_stats = []
        for row in cur.fetchall():
            gender_stats.append({'sexo': row[0], 'count': row[1]})
    else:
        cur.execute("""
            SELECT sexo, COUNT(*) as count 
            FROM users 
            GROUP BY sexo
        """)
        gender_stats = cur.fetchall()
    
    # Porcentaje de encuestas anónimas
    anonymous_percentage = (total_anonymous / total_surveys * 100) if total_surveys > 0 else 0
    
    # Estadísticas por pregunta
    if USE_SQLITE:
        cur.execute("""
            SELECT q.id, q.texto as pregunta,
                   o.id as option_id, o.texto as opcion,
                   COUNT(r.id) as count
            FROM questions q
            LEFT JOIN options o ON q.id = o.pregunta_id
            LEFT JOIN responses r ON o.id = r.respuesta
            GROUP BY q.id, q.texto, o.id, o.texto
            ORDER BY q.id, o.id
        """)
        
        question_stats = []
        for row in cur.fetchall():
            question_stats.append({
                'id': row[0],
                'pregunta': row[1],
                'option_id': row[2],
                'opcion': row[3],
                'count': row[4]
            })
    else:
        cur.execute("""
            SELECT q.id, q.texto as pregunta,
                   o.id as option_id, o.texto as opcion,
                   COUNT(r.id) as count
            FROM questions q
            LEFT JOIN options o ON q.id = o.pregunta_id
            LEFT JOIN responses r ON o.id = r.respuesta
            GROUP BY q.id, q.texto, o.id, o.texto
            ORDER BY q.id, o.id
        """)
        
        question_stats = cur.fetchall()
    
    # Organizar estadísticas por pregunta
    questions_data = {}
    for stat in question_stats:
        q_id = stat['id']
        if q_id not in questions_data:
            questions_data[q_id] = {
                'pregunta': stat['pregunta'],
                'opciones': [],
                'total_responses': 0
            }
        
        questions_data[q_id]['opciones'].append({
            'opcion': stat['opcion'],
            'count': stat['count']
        })
        questions_data[q_id]['total_responses'] += stat['count']
    
    # Calcular porcentajes
    for q_data in questions_data.values():
        total = q_data['total_responses']
        for opcion in q_data['opciones']:
            opcion['percentage'] = (opcion['count'] / total * 100) if total > 0 else 0
    
    cur.close()
    conn.close()
    
    return render_template('dashboard.html', 
                         total_surveys=total_surveys,
                         gender_stats=gender_stats,
                         anonymous_percentage=anonymous_percentage,
                         questions_data=questions_data)

@app.route('/api/submit-survey', methods=['POST'])
def submit_survey():
    data = request.json
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        user_id = None
        
        # Si no es anónima, crear usuario
        if not data.get('is_anonymous'):
            if USE_SQLITE:
                cur.execute("""
                    INSERT INTO users (nombre, email, edad, sexo, timestamp)
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    data['nombre'],
                    data['email'],
                    data['edad'],
                    data['sexo'],
                    datetime.now()
                ))
                user_id = cur.lastrowid
            else:
                cur.execute("""
                    INSERT INTO users (nombre, email, edad, sexo, timestamp)
                    VALUES (%s, %s, %s, %s, %s)
                    RETURNING id
                """, (
                    data['nombre'],
                    data['email'],
                    data['edad'],
                    data['sexo'],
                    datetime.now()
                ))
                user_id = cur.fetchone()[0]
        
        # Insertar respuestas
        for question_id, option_id in data['responses'].items():
            if USE_SQLITE:
                cur.execute("""
                    INSERT INTO responses (user_id, pregunta_id, respuesta)
                    VALUES (?, ?, ?)
                """, (user_id, int(question_id), int(option_id)))
            else:
                cur.execute("""
                    INSERT INTO responses (user_id, pregunta_id, respuesta)
                    VALUES (%s, %s, %s)
                """, (user_id, int(question_id), int(option_id)))
        
        conn.commit()
        return jsonify({'success': True})
        
    except Exception as e:
        conn.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        cur.close()
        conn.close()

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
