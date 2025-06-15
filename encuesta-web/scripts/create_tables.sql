-- Crear base de datos y tablas para la aplicación de encuestas

-- Tabla de preguntas
CREATE TABLE IF NOT EXISTS questions (
    id SERIAL PRIMARY KEY,
    texto TEXT NOT NULL
);

-- Tabla de opciones para cada pregunta
CREATE TABLE IF NOT EXISTS options (
    id SERIAL PRIMARY KEY,
    pregunta_id INTEGER REFERENCES questions(id) ON DELETE CASCADE,
    texto TEXT NOT NULL
);

-- Tabla de usuarios (para encuestas no anónimas)
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL,
    edad INTEGER NOT NULL,
    sexo VARCHAR(50) NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabla de respuestas
CREATE TABLE IF NOT EXISTS responses (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE NULL, -- NULL para respuestas anónimas
    pregunta_id INTEGER REFERENCES questions(id) ON DELETE CASCADE,
    respuesta INTEGER REFERENCES options(id) ON DELETE CASCADE,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Índices para mejorar el rendimiento
CREATE INDEX IF NOT EXISTS idx_responses_user_id ON responses(user_id);
CREATE INDEX IF NOT EXISTS idx_responses_pregunta_id ON responses(pregunta_id);
CREATE INDEX IF NOT EXISTS idx_options_pregunta_id ON options(pregunta_id);

-- Insertar datos de ejemplo
INSERT INTO questions (id, texto) VALUES 
(1, '¿Cuál es tu lenguaje de programación favorito?'),
(2, '¿Qué framework web prefieres?'),
(3, '¿Cuántas horas al día programas?')
ON CONFLICT (id) DO NOTHING;

INSERT INTO options (id, pregunta_id, texto) VALUES 
-- Pregunta 1
(1, 1, 'Python'),
(2, 1, 'JavaScript'),
(3, 1, 'Java'),
(4, 1, 'C++'),
-- Pregunta 2
(5, 2, 'Flask'),
(6, 2, 'Django'),
(7, 2, 'FastAPI'),
(8, 2, 'Express.js'),
-- Pregunta 3
(9, 3, '1-2 horas'),
(10, 3, '3-4 horas'),
(11, 3, '5-6 horas'),
(12, 3, 'Más de 6 horas')
ON CONFLICT (id) DO NOTHING;

COMMIT;
