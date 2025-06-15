# 🚂 Configuración con Railway

## 1. Crear cuenta en Railway
1. Ve a https://railway.app
2. Regístrate con GitHub (es gratis)
3. Verifica tu cuenta

## 2. Crear base de datos PostgreSQL
1. En el dashboard de Railway, haz clic en "New Project"
2. Selecciona "Provision PostgreSQL"
3. Espera a que se cree (toma 1-2 minutos)
4. Haz clic en tu base de datos PostgreSQL

## 3. Obtener la URL de conexión
1. En tu proyecto de Railway, ve a la pestaña "Variables"
2. Copia el valor de `DATABASE_URL`
3. Se ve algo así: `postgresql://postgres:password@containers-us-west-xxx.railway.app:5432/railway`

## 4. Configurar localmente
Crea un archivo `.env` en tu proyecto:
\`\`\`
DATABASE_URL=postgresql://postgres:tu_password@containers-us-west-xxx.railway.app:5432/railway
\`\`\`

## 5. Ejecutar la aplicación
\`\`\`bash
python app.py
\`\`\`

¡La aplicación se conectará automáticamente a Railway y creará las tablas!

## 6. Deploy en Railway (opcional)
1. En Railway, crea un nuevo servicio
2. Conecta tu repositorio de GitHub
3. Railway detectará automáticamente que es una app Python
4. Se desplegará automáticamente

## 7. Deploy en Vercel
\`\`\`bash
# Instalar Vercel CLI
npm i -g vercel

# Deploy
vercel

# Agregar variable de entorno
vercel env add DATABASE_URL
# Pega aquí tu DATABASE_URL de Railway
\`\`\`

## Ventajas de Railway:
✅ No necesitas instalar PostgreSQL localmente
✅ Base de datos en la nube gratis
✅ Fácil de configurar
✅ Compatible con Vercel y otros servicios
✅ Backups automáticos
✅ Interfaz web para ver los datos
