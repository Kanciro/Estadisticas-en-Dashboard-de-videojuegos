import os
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware

# Importación de todos los esquemas requeridos
from app.schemas import (
    SessionCreate,
    MatchCreate,
    StatsSummaryResponse,
    GameSummary,
)
from app.database import supabase

app = FastAPI(title="Gaming Tracker API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DEV_USER_ID = os.getenv("DEV_USER_ID", "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11")


@app.get("/")
def root():
    return {"message": "Gaming Tracker API Online 🚀"}


@app.post("/api/v1/sessions", status_code=status.HTTP_201_CREATED)
def record_session(session_data: SessionCreate):
    try:
        # 1. Buscar o registrar el juego en la tabla 'games'
        game_query = (
            supabase.table("games")
            .select("id")
            .eq("process_name", session_data.process_name.lower())
            .execute()
        )

        if game_query.data:
            game_id = game_query.data[0]["id"]
        else:
            new_game = (
                supabase.table("games")
                .insert(
                    {
                        "title": session_data.game_title,
                        "process_name": session_data.process_name.lower(),
                    }
                )
                .execute()
            )
            game_id = new_game.data[0]["id"]

        # 2. Registrar la sesión en 'game_sessions'
        session_payload = {
            "user_id": DEV_USER_ID,
            "game_id": game_id,
            "start_time": session_data.start_time.isoformat(),
            "end_time": session_data.end_time.isoformat(),
            "duration_seconds": session_data.duration_seconds,
            "is_active": False,
        }

        res = supabase.table("game_sessions").insert(session_payload).execute()
        return {"status": "success", "session": res.data[0]}

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error guardando sesión en Supabase: {str(e)}",
        )


@app.post("/api/v1/matches", status_code=status.HTTP_201_CREATED)
def record_match(match_data: MatchCreate):
    """Registra una partida (Win/Loss) para análisis de rendimiento y Win Rate."""
    try:
        match_payload = {
            "user_id": DEV_USER_ID,
            "game_id": str(match_data.game_id),
            "result": match_data.result.upper(),
            "character_played": match_data.character_played,
            "rank_at_time": match_data.rank_at_time,
            "notes": match_data.notes,
        }

        res = supabase.table("matches").insert(match_payload).execute()
        return {"status": "success", "match": res.data[0]}

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al registrar partida en Supabase: {str(e)}",
        )


@app.get("/api/v1/stats/summary", response_model=StatsSummaryResponse)
def get_stats_summary():
    """Consulta consolidada para alimentar el Dashboard principal."""
    try:
        # 1. Obtener todas las sesiones del usuario
        sessions_res = (
            supabase.table("game_sessions")
            .select("duration_seconds, game_id")
            .eq("user_id", DEV_USER_ID)
            .execute()
        )
        sessions = sessions_res.data or []

        total_seconds = sum(s.get("duration_seconds") or 0 for s in sessions)
        total_sessions = len(sessions)

        # Cálculo de horas totales con precisión mínima para pruebas cortas
        total_hours = round(total_seconds / 3600, 2)
        if total_seconds > 0 and total_hours == 0:
            total_hours = 0.01

        # 2. Mapear IDs de juegos a sus títulos
        games_res = supabase.table("games").select("id, title").execute()
        games_dict = {g["id"]: g["title"] for g in (games_res.data or [])}

        # Agrupar tiempo por juego
        games_map = {}
        for s in sessions:
            gid = s.get("game_id")
            game_title = games_dict.get(gid, "Desconocido")
            if game_title not in games_map:
                games_map[game_title] = {"seconds": 0, "count": 0}
            games_map[game_title]["seconds"] += s.get("duration_seconds") or 0
            games_map[game_title]["count"] += 1

        top_games = []
        for title, data in sorted(
            games_map.items(), key=lambda item: item[1]["seconds"], reverse=True
        ):
            game_hours = round(data["seconds"] / 3600, 2)
            if data["seconds"] > 0 and game_hours == 0:
                game_hours = 0.01

            top_games.append(
                GameSummary(
                    game_title=title,
                    total_hours=game_hours,
                    total_sessions=data["count"],
                )
            )

        # 3. Obtener partidas competitivas (Win/Loss)
        total_matches = 0
        total_wins = 0
        total_losses = 0
        win_rate = 0.0

        try:
            matches_res = (
                supabase.table("matches")
                .select("result")
                .eq("user_id", DEV_USER_ID)
                .execute()
            )
            matches = matches_res.data or []
            total_matches = len(matches)
            total_wins = sum(1 for m in matches if m.get("result") == "WIN")
            total_losses = sum(1 for m in matches if m.get("result") == "LOSS")
            win_rate = (
                round((total_wins / total_matches) * 100, 1)
                if total_matches > 0
                else 0.0
            )
        except Exception:
            pass

        return StatsSummaryResponse(
            total_play_time_hours=total_hours,
            total_sessions_count=total_sessions,
            total_matches_count=total_matches,
            total_wins=total_wins,
            total_losses=total_losses,
            win_rate_percentage=win_rate,
            top_games=top_games,
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error obteniendo estadísticas desde Supabase: {str(e)}",
        )