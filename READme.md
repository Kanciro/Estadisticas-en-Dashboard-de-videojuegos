

Markdown
# 🎮 Gaming Analytics Tracker

Un sistema de telemetría y análisis de rendimiento en tiempo real para videojuegos. Registra de forma autónoma el tiempo de uso de ejecutables mediante un agente de escritorio ligero en Windows, ingiere los datos en una API REST construida con FastAPI, persiste la información en Supabase y visualiza las métricas en un Dashboard moderno e interactivo desarrollado en Next.js.

---

## 🛠️ Arquitectura e Tecnologías

* **Backend:** FastAPI (Python 3.10+), Pydantic, Supabase Client.
* **Frontend:** Next.js (React 19, TypeScript, Tailwind CSS, Lucide Icons).
* **Agente de Telemetría:** Python Script (Monitoreo de procesos en Windows vía `psutil` y peticiones HTTP asíncronas).
* **Base de Datos:** Supabase (PostgreSQL con Políticas RLS).

---

## 🚀 Características Clave

* **Monitoreo Automático:** Detección en segundo plano de ejecutables en tiempo real sin interferir con el rendimiento del sistema.
* **Métricas Consolidadas:** Cálculo dinámico de horas jugadas, número de sesiones y desgloses por juego.
* **Sección de Rendimiento Competitivo:** Estructura lista para el registro de partidas (Win/Loss), tasa de victorias (*Win Rate*) y trazabilidad de personajes/rangos.
* **Resiliencia & Manejo de Errores:** Conversión automática de fracciones de tiempo para pruebas de corta duración y alertas visuales en caso de desconexión del backend.

---

## ⚙️ Instalación y Configuración Local

### 1. Backend (FastAPI)
```bash
cd backend
python -m venv venv
# En Windows:
venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
2. Frontend (Next.js)
Bash
cd frontend
npm install
npm run dev
3. Agente de Escritorio (Windows)
Bash
cd agent
python agent.py
🗄️ Variables de Entorno
Asegúrate de configurar los archivos .env correspondientes en el Backend y Frontend:

backend/.env

Fragmento de código
SUPABASE_URL=tu_supabase_url
SUPABASE_KEY=tu_supabase_anon_key
DEV_USER_ID=a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11
frontend/.env.local

Fragmento de código
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
📌 Estado del Proyecto & Próximos Pasos
[x] Ingesta automática de sesiones desde el agente.

[x] Cálculo dinámico de estadísticas de uso.

[x] Dashboard UI responsivo en Next.js.

[ ] Integración del formulario para registro de partidas competitivas.

[ ] Filtro de ignorados (ignore-list) en el agente para omitir software que no sea de juego.


---

### 2. Guardar Cambios y Crear Punto de Control en Git

Ejecuta los siguientes comandos en tu terminal desde la raíz del proyecto para confirmar el punto de control (*commit tag*):

```bash
# 1. Verificar los archivos modificados
git status

# 2. Agregar todos los cambios al stage (incluyendo el README)
git add .

# 3. Crear el commit del punto de control
git commit -m "feat: integración completa de telemetría (Agente -> FastAPI -> Supabase -> Next.js)"

# 4. Crear una etiqueta (tag) para marcar este hito estable
git tag -a v1.0.0-beta -m "Punto de control: MVP de la pipeline de telemetría y dashboard funcionando"

# 5. Subir los cambios y las etiquetas a GitHub
git push origin main
git push origin --tags
