"""
Script para ejecutar la aplicación localmente sin Railway
Usa SQLite para desarrollo local
"""
from flask import Flask, render_template, request, jsonify
import sqlite3
import os
from datetime import datetime
import json

app = Flask(__name__)

def get_db_connection():
    """Conexión a SQLite local"""
    conn = sqlite3.connect('survey_local.db')
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Inicializar base de datos SQLite local"""
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        print("📝 Creando base de datos para detección de violencia intrafamiliar...")
        
        # Crear tablas
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

        # Verificar si ya hay datos
        cur.execute("SELECT COUNT(*) FROM questions")
        count = cur.fetchone()[0]
        
        if count == 0:
            print("📊 Insertando preguntas sobre violencia intrafamiliar...")
            
            # Insertar preguntas reales
            questions = [
                "¿Cómo describirías el ambiente en tu hogar?",
                "¿Te han hecho sentir miedo, humillado/a o culpable dentro de tu familia recientemente?",
                "¿Te han hecho sentir miedo con miradas, gestos o silencios prolongados?",
                "¿A quién acudirías si te sintieras en peligro dentro de tu hogar?",
                "¿Alguna vez alguien en tu familia te ha golpeado, empujado o agredido físicamente?",
                "¿Has presenciado actos de violencia hacia ti u otros miembros de tu familia?"
            ]
            
            for question in questions:
                cur.execute("INSERT INTO questions (texto) VALUES (?)", (question,))
            
            # Insertar opciones con puntajes
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
                cur.execute("INSERT INTO options (pregunta_id, texto, puntaje) VALUES (?, ?, ?)", 
                          (question_id, texto, puntaje))
        
        conn.commit()
        print("✅ Base de datos de violencia intrafamiliar lista!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
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
    cur = conn.cursor()
    
    # Obtener preguntas
    cur.execute("SELECT id, texto as pregunta FROM questions ORDER BY id")
    questions_data = cur.fetchall()
    
    questions = []
    for q in questions_data:
        # Obtener opciones para cada pregunta
        cur.execute("SELECT id, texto FROM options WHERE pregunta_id = ? ORDER BY id", (q['id'],))
        opciones = cur.fetchall()
        questions.append({
            'id': q['id'],
            'pregunta': q['pregunta'],
            'opciones': [{'id': o['id'], 'texto': o['texto']} for o in opciones]
        })
    
    cur.close()
    conn.close()
    
    return render_template('survey.html', questions=questions)

@app.route('/dashboard')
def dashboard():
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        # Total de ENCUESTAS (no respuestas individuales)
        # Contar usuarios únicos que completaron la encuesta
        cur.execute("""
            SELECT COUNT(DISTINCT CASE WHEN user_id IS NOT NULL THEN user_id END) as named_surveys,
                   COUNT(DISTINCT CASE WHEN user_id IS NULL THEN timestamp END) as anonymous_surveys
            FROM (
                SELECT user_id, timestamp, COUNT(*) as respuestas
                FROM responses 
                GROUP BY user_id, timestamp
                HAVING respuestas = 6
            )
        """)
        result = cur.fetchone()
        total_named = result['named_surveys'] if result else 0
        total_anonymous = result['anonymous_surveys'] if result else 0
        total_surveys = total_named + total_anonymous
        
        # Estadísticas por género CON PORCENTAJES
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
        
        # Porcentaje anónimas
        anonymous_percentage = (total_anonymous / total_surveys * 100) if total_surveys > 0 else 0
        
        # Estadísticas de CLASIFICACIÓN (leve, moderado, grave)
        cur.execute("""
            SELECT 
                CASE 
                    WHEN puntaje_total BETWEEN 0 AND 5 THEN 'Leve'
                    WHEN puntaje_total BETWEEN 6 AND 11 THEN 'Moderado'
                    WHEN puntaje_total BETWEEN 12 AND 18 THEN 'Grave'
                    ELSE 'Sin clasificar'
                END as clasificacion,
                COUNT(*) as count
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
        
        # Estadísticas por pregunta
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
        
        # Organizar por pregunta
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
                'puntaje': stat['puntaje'],
                'count': stat['count']
            })
            questions_data[q_id]['total_responses'] += stat['count']
        
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
            cur.execute("SELECT puntaje FROM options WHERE id = ?", (int(option_id),))
            result = cur.fetchone()
            if result:
                puntaje_total += result['puntaje']
        
        # Determinar clasificación
        if puntaje_total <= 5:
            clasificacion = 'Leve'
        elif puntaje_total <= 11:
            clasificacion = 'Moderado'
        else:
            clasificacion = 'Grave'
        
        # Si no es anónima, crear usuario
        if not data.get('is_anonymous'):
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
        
        # Insertar respuestas con puntajes
        for question_id, option_id in data['responses'].items():
            # Obtener puntaje de la opción
            cur.execute("SELECT puntaje FROM options WHERE id = ?", (int(option_id),))
            result = cur.fetchone()
            puntaje_respuesta = result['puntaje'] if result else 0
            
            cur.execute("""
                INSERT INTO responses (user_id, pregunta_id, respuesta, puntaje)
                VALUES (?, ?, ?, ?)
            """, (user_id, int(question_id), int(option_id), puntaje_respuesta))
        
        conn.commit()
        print(f"✅ Encuesta guardada - Usuario: {user_id}, Puntaje: {puntaje_total}, Clasificación: {clasificacion}")
        return jsonify({
            'success': True, 
            'puntaje': puntaje_total, 
            'clasificacion': clasificacion
        })
        
    except Exception as e:
        conn.rollback()
        print(f"❌ Error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        cur.close()
        conn.close()

if __name__ == '__main__':
    print("🚀 Iniciando aplicación de encuestas (modo local)...")
    print("📍 Usando SQLite para desarrollo local")
    init_db()
    app.run(debug=True, host='127.0.0.1', port=5000)

# Para Vercel
app.config['ENV'] = 'production'
if __name__ != '__main__':
    # Inicializar DB cuando se importa (para Vercel)
    init_db()
