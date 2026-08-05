from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
import uuid


class SessionCreate(BaseModel):
    """Payload enviado por el Agente Local."""
    process_name: str = Field(..., example="2xko.exe")
    game_title: str = Field(..., example="2XKO")
    start_time: datetime
    end_time: datetime
    duration_seconds: int = Field(..., ge=0)


class SessionResponse(BaseModel):
    """Respuesta al registrar una sesión."""
    id: uuid.UUID
    user_id: uuid.UUID
    game_id: uuid.UUID
    start_time: datetime
    end_time: Optional[datetime]
    duration_seconds: Optional[int]
    is_active: bool

    class Config:
        from_attributes = True

class MatchCreate(BaseModel):
    """Payload para registrar el resultado de una partida competitiva."""
    game_id: uuid.UUID
    result: str = Field(..., example="WIN", description="Valores válidos: 'WIN', 'LOSS', 'DRAW'")
    character_played: Optional[str] = Field(None, example="Ahri")
    rank_at_time: Optional[str] = Field(None, example="Gold II")
    notes: Optional[str] = Field(None, example="Remontada en el round 3")


class GameSummary(BaseModel):
    game_title: str
    total_hours: float
    total_sessions: int


class StatsSummaryResponse(BaseModel):
    """Respuesta del resumen general de estadísticas."""
    total_play_time_hours: float
    total_sessions_count: int
    total_matches_count: int
    total_wins: int
    total_losses: int
    win_rate_percentage: float
    top_games: List[GameSummary]