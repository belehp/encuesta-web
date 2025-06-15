# 🚀 Guía para Deploy en GitHub y Vercel

## 📋 Paso 1: Subir a GitHub

### 1.1 Crear repositorio en GitHub
1. Ve a https://github.com
2. Haz clic en "New repository"
3. Nombre: `encuesta-violencia-intrafamiliar`
4. Descripción: `Sistema de detección de violencia intrafamiliar para centros de salud`
5. Marca como "Public" o "Private"
6. NO marques "Initialize with README" (ya tienes uno)
7. Haz clic en "Create repository"

### 1.2 Preparar archivos localmente
\`\`\`bash
# En tu carpeta del proyecto, inicializar git
git init

# Agregar todos los archivos
git add .

# Hacer primer commit
git commit -m "Initial commit: Sistema de detección de violencia intrafamiliar"

# Conectar con tu repositorio de GitHub (reemplaza con tu URL)
git remote add origin https://github.com/TU_USUARIO/encuesta-violencia-intrafamiliar.git

# Subir archivos
git push -u origin main
\`\`\`

### 1.3 Si no tienes Git instalado
1. Descarga Git desde: https://git-scm.com/download/win
2. Instala con configuración por defecto
3. Reinicia tu terminal/cmd
4. Ejecuta los comandos de arriba

## 📋 Paso 2: Configurar para Vercel

### 2.1 Crear archivo de configuración para Vercel
Crea \`vercel.json\` en la raíz del proyecto:

\`\`\`json
{
  "version": 2,
  "builds": [
    {
      "src": "run_local.py",
      "use": "@vercel/python"
    }
  ],
  "routes": [
    {
      "src": "/(.*)",
      "dest": "run_local.py"
    }
  ],
  "env": {
    "PYTHONPATH": "."
  }
}
\`\`\`

### 2.2 Modificar run_local.py para producción
Agrega al final de \`run_local.py\`:

\`\`\`python
# Para Vercel
app.config['ENV'] = 'production'
if __name__ != '__main__':
    # Inicializar DB cuando se importa (para Vercel)
    init_db()
\`\`\`

## 📋 Paso 3: Deploy en Vercel

### 3.1 Crear cuenta en Vercel
1. Ve a https://vercel.com
2. Regístrate con tu cuenta de GitHub
3. Autoriza el acceso a tus repositorios

### 3.2 Importar proyecto
1. En Vercel dashboard, haz clic en "New Project"
2. Busca tu repositorio \`encuesta-violencia-intrafamiliar\`
3. Haz clic en "Import"
4. Configuración:
   - Framework Preset: "Other"
   - Root Directory: "./" (por defecto)
   - Build Command: (dejar vacío)
   - Output Directory: (dejar vacío)
5. Haz clic en "Deploy"

### 3.3 Configurar variables de entorno (si usas Railway)
Si quieres usar PostgreSQL en lugar de SQLite:
1. En tu proyecto de Vercel → Settings → Environment Variables
2. Agregar: \`DATABASE_URL\` = tu URL de Railway
3. Redeploy el proyecto

## 📋 Paso 4: Actualizar código

### 4.1 Para futuras actualizaciones
\`\`\`bash
# Hacer cambios en tu código local
# Luego:
git add .
git commit -m "Descripción de los cambios"
git push

# Vercel se actualizará automáticamente
\`\`\`

## 📋 Paso 5: Comandos útiles de Git

### 5.1 Comandos básicos
\`\`\`bash
# Ver estado de archivos
git status

# Ver historial de commits
git log --oneline

# Crear nueva rama
git checkout -b nueva-funcionalidad

# Cambiar de rama
git checkout main

# Ver diferencias
git diff
\`\`\`

### 5.2 Si tienes errores
\`\`\`bash
# Si hay conflictos, resetear a último commit
git reset --hard HEAD

# Si quieres deshacer último commit (mantener cambios)
git reset --soft HEAD~1

# Si quieres deshacer último commit (eliminar cambios)
git reset --hard HEAD~1
\`\`\`

## 🎯 Resultado Final

Después de seguir estos pasos tendrás:

✅ **Código en GitHub**: Respaldo y control de versiones  
✅ **App en Vercel**: Accesible desde cualquier lugar  
✅ **URL pública**: Para compartir con tu equipo  
✅ **Deploy automático**: Cada cambio se actualiza solo  

## 📱 URLs de ejemplo

- **GitHub**: https://github.com/tu-usuario/encuesta-violencia-intrafamiliar
- **Vercel**: https://encuesta-violencia-intrafamiliar.vercel.app

## 🔧 Troubleshooting

### Error en Vercel: "Module not found"
- Verifica que \`requirements.txt\` esté en la raíz
- Asegúrate que todos los imports sean correctos

### Error: "Database locked"
- En producción, considera usar PostgreSQL (Railway)
- SQLite puede tener problemas con múltiples usuarios

### Error de Git: "Permission denied"
- Configura tu usuario de Git:
\`\`\`bash
git config --global user.name "Tu Nombre"
git config --global user.email "tu@email.com"
\`\`\`

¡Listo! Tu aplicación estará disponible en internet 🌐
\`\`\`
