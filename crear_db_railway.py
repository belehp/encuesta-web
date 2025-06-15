import psycopg2
import os
from dotenv import load_dotenv
load_dotenv()
# URL completa, o usa variable de entorno en producción
DATABASE_URL = os.getenv('DATABASE_URL')

def crear_db_postgres():
    conn = None
    cur = None
    try:
        print("🔗 Conectando a la base de datos PostgreSQL...")
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()

        print("🗑️ Eliminando tablas anteriores (si existen)...")
        cur.execute("DROP TABLE IF EXISTS responses, users, options, questions CASCADE;")

        print("🛠️ Creando nuevas tablas...")
        cur.execute('''
            CREATE TABLE questions (
                id SERIAL PRIMARY KEY,
                texto TEXT NOT NULL
            )
        ''')

        cur.execute('''
            CREATE TABLE options (
                id SERIAL PRIMARY KEY,
                pregunta_id INTEGER REFERENCES questions (id) ON DELETE CASCADE,
                texto TEXT NOT NULL,
                puntaje INTEGER NOT NULL DEFAULT 0
            )
        ''')

        cur.execute('''
            CREATE TABLE users (
                id SERIAL PRIMARY KEY,
                nombre TEXT NOT NULL,
                email TEXT NOT NULL,
                edad INTEGER NOT NULL,
                sexo TEXT NOT NULL,
                puntaje_total INTEGER DEFAULT 0,
                clasificacion TEXT DEFAULT 'leve',
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        cur.execute('''
            CREATE TABLE responses (
                id SERIAL PRIMARY KEY,
                user_id INTEGER REFERENCES users (id) ON DELETE CASCADE,
                pregunta_id INTEGER REFERENCES questions (id),
                respuesta INTEGER REFERENCES options (id),
                puntaje INTEGER DEFAULT 0,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        print("📊 Insertando preguntas...")
        questions = [
            "¿Cómo describirías el ambiente en tu hogar?",
            "¿Te han hecho sentir miedo, humillado/a o culpable dentro de tu familia recientemente?",
            "¿Te han hecho sentir miedo con miradas, gestos o silencios prolongados?",
            "¿A quién acudirías si te sintieras en peligro dentro de tu hogar?",
            "¿Alguna vez alguien en tu familia te ha golpeado, empujado o agredido físicamente?",
            "¿Has presenciado actos de violencia hacia ti u otros miembros de tu familia?"
        ]

        for q in questions:
            cur.execute("INSERT INTO questions (texto) VALUES (%s)", (q,))

        print("🧩 Insertando opciones...")
        options = [
            # (pregunta_id, texto, puntaje)
            (1, "Tranquilo y de respeto mutuo", 0),
            (1, "A veces tenso, con discusiones esporádicas", 1),
            (1, "Frecuentemente hay gritos, insultos o agresiones", 2),
            (1, "Me siento incómodo/a o inseguro/a en casa", 3),

            (2, "No, nunca", 0),
            (2, "A veces, pero no sé si es normal", 1),
            (2, "Sí, con frecuencia", 2),
            (2, "Sí, siempre", 3),

            (3, "No, nunca", 0),
            (3, "A veces", 1),
            (3, "Sí, frecuentemente", 2),
            (3, "Sí, constantemente", 3),

            (4, "A un amigo/familiar de confianza", 0),
            (4, "A un profesional de salud, asistente social o Carabineros", 1),
            (4, "No sabría qué hacer", 2),
            (4, "No tengo a quién acudir", 3),

            (5, "No, nunca", 0),
            (5, "Una vez, en una situación puntual", 1),
            (5, "Varias veces", 2),
            (5, "Sí, actualmente ocurre", 3),

            (6, "No", 0),
            (6, "Sí, una vez", 1),
            (6, "Varias veces", 2),
            (6, "Sí, recientemente", 3),
        ]

        for pregunta_id, texto, puntaje in options:
            cur.execute("INSERT INTO options (pregunta_id, texto, puntaje) VALUES (%s, %s, %s)", 
                        (pregunta_id, texto, puntaje))

        conn.commit()
        print("✅ ¡Base de datos PostgreSQL inicializada correctamente!")

    except Exception as e:
        print(f"❌ Error: {e}")
        if conn:
            conn.rollback()
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()

if __name__ == '__main__':
    crear_db_postgres()