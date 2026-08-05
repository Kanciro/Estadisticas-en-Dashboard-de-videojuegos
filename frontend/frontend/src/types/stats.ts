export interface GameSummary {
  game_title: string;
  total_hours: number;
  total_sessions: number;
}

export interface StatsSummary {
  total_play_time_hours: number;
  total_sessions_count: number;
  total_matches_count: number;
  total_wins: number;
  total_losses: number;
  win_rate_percentage: number;
  top_games: GameSummary[];
}