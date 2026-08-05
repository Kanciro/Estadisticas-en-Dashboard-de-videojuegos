import time
import datetime
import psutil
import requests
from typing import Dict, Optional, Set

# Configuración Base
CHECK_INTERVAL_SECONDS = 5  # Frecuencia de escaneo
API_URL = "http://localhost:8000/api/v1/sessions"  # Endpoint del backend FastAPI

# Lista de ejecutables objetivo (nombres en minúsculas para comparaciones uniformes)
TARGET_GAMES = {
    "2xko.exe": "2XKO",
    "streetfighter6.exe": "Street Fighter 6",
    "wow.exe": "World of Warcraft",
    "valorant-win64-shipping.exe": "Valorant",
    "opera.exe": "Opera GX",  # Ejemplo de navegador para pruebas
    "notepad.exe": "Notepad"  # Ejemplo de aplicación no relacionada con juegos
}


class ActiveSession:
    """Clase para representar y gestionar el estado de una sesión de juego activa."""
    def __init__(self, process_name: str, game_title: str):
        self.process_name = process_name
        self.game_title = game_title
        # UTC internamente para enviar al Backend/Supabase de forma estándar
        self.start_time = datetime.datetime.now(datetime.timezone.utc)
        self.end_time: Optional[datetime.datetime] = None

    def close(self):
        """Finaliza la sesión y calcula la duración en segundos."""
        self.end_time = datetime.datetime.now(datetime.timezone.utc)

    @property
    def start_time_local(self) -> datetime.datetime:
        """Devuelve la hora de inicio convertida a la zona horaria del sistema (ej. Colombia UTC-5)."""
        return self.start_time.astimezone()

    @property
    def end_time_local(self) -> Optional[datetime.datetime]:
        """Devuelve la hora de cierre convertida a la zona horaria local."""
        return self.end_time.astimezone() if self.end_time else None

    @property
    def duration_seconds(self) -> int:
        if not self.end_time:
            return 0
        return int((self.end_time - self.start_time).total_seconds())

    def to_payload(self) -> dict:
        """Formatea los datos para enviarlos al backend FastAPI (estándar UTC ISO-8601)."""
        return {
            "process_name": self.process_name,
            "game_title": self.game_title,
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "duration_seconds": self.duration_seconds
        }


class ProcessMonitor:
    """Clase encargada de escanear los procesos del SO usando psutil."""
    def __init__(self, target_games: Dict[str, str]):
        self.target_games = target_games  # Map: {"process.exe": "Game Title"}
        self.active_sessions: Dict[str, ActiveSession] = {}

    def get_running_process_names(self) -> Set[str]:
        """Escanea todos los procesos del SO de forma optimizada."""
        running = set()
        for proc in psutil.process_iter(['name']):
            try:
                name = proc.info['name']
                if name:
                    running.add(name.lower())
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                continue
        return running

    def send_telemetry(self, payload: dict):
        """Envía el payload de la sesión finalizada al Backend FastAPI por HTTP POST."""
        try:
            response = requests.post(API_URL, json=payload, timeout=5)
            if response.status_code == 201:
                print("✅ [HTTP 201] Sesión guardada exitosamente en el Backend/Supabase.")
            else:
                print(f"⚠️ [HTTP {response.status_code}] Error del backend: {response.text}")
        except Exception as e:
            print(f"❌ No se pudo conectar con el Backend ({API_URL}): {e}")

    def scan(self):
        """Escanea y compara el estado actual con las sesiones activas."""
        running_processes = self.get_running_process_names()

        # 1. Detectar Nuevos Juegos Iniciados
        for proc_exe, game_title in self.target_games.items():
            if proc_exe in running_processes and proc_exe not in self.active_sessions:
                session = ActiveSession(proc_exe, game_title)
                self.active_sessions[proc_exe] = session
                print(f"🎮 [INICIO DE SESIÓN DETECTADO] {game_title} ({proc_exe}) a las {session.start_time_local.strftime('%H:%M:%S')}")

        # 2. Detectar Juegos Cerrados
        closed_processes = []
        for proc_exe, session in self.active_sessions.items():
            if proc_exe not in running_processes:
                session.close()
                closed_processes.append(proc_exe)
                end_str = session.end_time_local.strftime('%H:%M:%S') if session.end_time_local else ""
                print(f"🛑 [FIN DE SESIÓN DETECTADO] {session.game_title} a las {end_str}")
                print(f"⏱️ Duración Total: {session.duration_seconds} segundos")
                print(f"📡 Payload de Telemetría: {session.to_payload()}")
                
                # Enviar telemetría al Backend FastAPI
                self.send_telemetry(session.to_payload())
                print()

        # Limpiar sesiones cerradas de la memoria del agente
        for proc_exe in closed_processes:
            del self.active_sessions[proc_exe]


def main():
    print("🚀 [Agente Local] Monitor de Juegos iniciado...")
    print(f"🎯 Monitoreando los siguientes ejecutables: {list(TARGET_GAMES.keys())}\n")
    
    monitor = ProcessMonitor(TARGET_GAMES)

    try:
        while True:
            monitor.scan()
            time.sleep(CHECK_INTERVAL_SECONDS)
    except KeyboardInterrupt:
        print("\n🛑 [Agente Local] Monitor detenido por el usuario.")


if __name__ == "__main__":
    main()