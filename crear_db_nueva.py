"""
Script para crear una base de datos completamente nueva
con las preguntas actualizadas
"""
import sqlite3
import os

def crear_db_nueva():
    # Eliminar base de datos existente si existe
    if os.path.exists('survey_local.db'):
        os.remove('survey_local.db')
        print("🗑️ Base de datos anterior eliminada")
    
    conn = sqlite3.connect('survey_local.db')
    cur = conn.cursor()
    
    try:
        print("📝 Creando nueva base de datos para detección de violencia intrafamiliar...")
        
        # Crear tablas con la columna puntaje
        cur.execute('''
            CREATE TABLE questions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                texto TEXT NOT NULL
            )
        ''')
        
        cur.execute('''
            CREATE TABLE options (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pregunta_id INTEGER,
                texto TEXT NOT NULL,
                puntaje INTEGER NOT NULL DEFAULT 0,
                FOREIGN KEY (pregunta_id) REFERENCES questions (id)
            )
        ''')
        
        cur.execute('''
            CREATE TABLE users (
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
            CREATE TABLE responses (
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

        print("📊 Insertando preguntas actualizadas sobre violencia intrafamiliar...")
        
        # Insertar preguntas EXACTAS que me pasaste
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
        
        # Insertar opciones EXACTAS con puntajes
        options = [
            # Pregunta 1 - ¿Cómo describirías el ambiente en tu hogar?
            (1, "Tranquilo y de respeto mutuo", 0),
            (1, "A veces tenso, con discusiones esporádicas", 1),
            (1, "Frecuentemente hay gritos, insultos o agresiones", 2),
            (1, "Me siento incómodo/a o inseguro/a en casa", 3),
            
            # Pregunta 2 - ¿Te han hecho sentir miedo, humillado/a o culpable dentro de tu familia recientemente?
            (2, "No, nunca", 0),
            (2, "A veces, pero no sé si es normal", 1),
            (2, "Sí, con frecuencia", 2),
            (2, "Sí, siempre", 3),
            
            # Pregunta 3 - ¿Te han hecho sentir miedo con miradas, gestos o silencios prolongados?
            (3, "No, nunca", 0),
            (3, "A veces", 1),
            (3, "Sí, frecuentemente", 2),
            (3, "Sí, constantemente", 3),
            
            # Pregunta 4 - ¿A quién acudirías si te sintieras en peligro dentro de tu hogar?
            (4, "A un amigo/familiar de confianza", 0),
            (4, "A un profesional de salud, asistente social o Carabineros", 1),
            (4, "No sabría qué hacer", 2),
            (4, "No tengo a quién acudir", 3),
            
            # Pregunta 5 - ¿Alguna vez alguien en tu familia te ha golpeado, empujado o agredido físicamente?
            (5, "No, nunca", 0),
            (5, "Una vez, en una situación puntual", 1),
            (5, "Varias veces", 2),
            (5, "Sí, actualmente ocurre", 3),
            
            # Pregunta 6 - ¿Has presenciado actos de violencia hacia ti u otros miembros de tu familia?
            (6, "No", 0),
            (6, "Sí, una vez", 1),
            (6, "Varias veces", 2),
            (6, "Sí, recientemente", 3)
        ]
        
        for question_id, texto, puntaje in options:
            cur.execute("INSERT INTO options (pregunta_id, texto, puntaje) VALUES (?, ?, ?)", 
                      (question_id, texto, puntaje))
        
        conn.commit()
        print("✅ Nueva base de datos creada con las preguntas correctas!")
        print("📋 Preguntas insertadas:")
        for i, q in enumerate(questions, 1):
            print(f"   {i}. {q}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        conn.rollback()
    finally:
        cur.close()
        conn.close()

if __name__ == '__main__':
    crear_db_nueva()
