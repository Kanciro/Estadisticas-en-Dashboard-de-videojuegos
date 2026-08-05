'use client';

import { useEffect, useState } from 'react';
import { StatsSummary } from '@/types/stats';
import { Gamepad2, Clock, Trophy, Flame, Activity, AlertCircle } from 'lucide-react';

export default function DashboardPage() {
  const [stats, setStats] = useState<StatsSummary | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function fetchStats() {
      try {
        setError(null);
        // Fallback dinámico si process.env.NEXT_PUBLIC_API_URL no está cargado correctamente
        const baseUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';
        const res = await fetch(`${baseUrl}/stats/summary`);

        if (!res.ok) {
          throw new Error(`Error en el backend: ${res.status} ${res.statusText}`);
        }

        const data: StatsSummary = await res.json();
        setStats(data);
      } catch (err) {
        console.error('Error cargando métricas:', err);
        setError('No se pudo conectar con el servidor de telemetría (FastAPI).');
      } finally {
        setLoading(false);
      }
    }

    fetchStats();
  }, []);

  if (loading) {
    return (
      <div className="flex h-screen items-center justify-center bg-slate-950 text-white">
        <Activity className="h-8 w-8 animate-spin text-indigo-500" />
        <span className="ml-3 font-medium">Cargando telemetría...</span>
      </div>
    );
  }

  return (
    <main className="min-h-screen bg-slate-950 p-8 text-slate-100">
      <header className="mb-8 flex items-center justify-between border-b border-slate-800 pb-5">
        <div>
          <h1 className="text-3xl font-bold tracking-tight text-white flex items-center gap-3">
            <Gamepad2 className="h-8 w-8 text-indigo-500" />
            Gaming Analytics Dashboard
          </h1>
          <p className="text-sm text-slate-400 mt-1">
            Monitoreo en tiempo real de sesiones y rendimiento competitivo.
          </p>
        </div>
      </header>

      {/* ALERTA DE ERROR DE CONEXIÓN */}
      {error && (
        <div className="mb-6 flex items-center gap-3 rounded-xl border border-rose-500/30 bg-rose-500/10 p-4 text-rose-300">
          <AlertCircle className="h-5 w-5 shrink-0 text-rose-400" />
          <p className="text-sm font-medium">{error}</p>
        </div>
      )}

      {/* TARJETAS DE MÉTRICAS */}
      <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4 mb-8">
        <div className="rounded-xl border border-slate-800 bg-slate-900/60 p-5 shadow-lg backdrop-blur">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold uppercase tracking-wider text-slate-400">Tiempo Jugado</span>
            <Clock className="h-5 w-5 text-indigo-400" />
          </div>
          <p className="mt-3 text-3xl font-extrabold text-white">{stats?.total_play_time_hours ?? 0} hrs</p>
          <span className="text-xs text-slate-500">{stats?.total_sessions_count ?? 0} sesiones registradas</span>
        </div>

        <div className="rounded-xl border border-slate-800 bg-slate-900/60 p-5 shadow-lg backdrop-blur">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold uppercase tracking-wider text-slate-400">Win Rate</span>
            <Trophy className="h-5 w-5 text-amber-400" />
          </div>
          <p className="mt-3 text-3xl font-extrabold text-white">{stats?.win_rate_percentage ?? 0}%</p>
          <span className="text-xs text-slate-500">{stats?.total_wins ?? 0}V / {stats?.total_losses ?? 0}D</span>
        </div>

        <div className="rounded-xl border border-slate-800 bg-slate-900/60 p-5 shadow-lg backdrop-blur">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold uppercase tracking-wider text-slate-400">Partidas Totales</span>
            <Gamepad2 className="h-5 w-5 text-emerald-400" />
          </div>
          <p className="mt-3 text-3xl font-extrabold text-white">{stats?.total_matches_count ?? 0}</p>
          <span className="text-xs text-slate-500">Partidas competitivas</span>
        </div>

        <div className="rounded-xl border border-slate-800 bg-slate-900/60 p-5 shadow-lg backdrop-blur">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold uppercase tracking-wider text-slate-400">Burnout Index</span>
            <Flame className="h-5 w-5 text-rose-500" />
          </div>
          <p className="mt-3 text-3xl font-extrabold text-emerald-400">Óptimo</p>
          <span className="text-xs text-slate-500">Ritmo de descanso saludable</span>
        </div>
      </div>

      {/* SECCIÓN DE JUEGOS MÁS JUGADOS */}
      <section className="rounded-xl border border-slate-800 bg-slate-900/40 p-6">
        <h2 className="text-xl font-bold text-white mb-4">Desglose por Ejecutable</h2>
        <div className="divide-y divide-slate-800">
          {stats?.top_games && stats.top_games.length > 0 ? (
            stats.top_games.map((game, idx) => (
              <div key={idx} className="flex items-center justify-between py-3">
                <div className="flex items-center gap-3">
                  <span className="text-sm font-bold text-indigo-400">#{idx + 1}</span>
                  <span className="font-medium text-slate-200">{game.game_title}</span>
                </div>
                <div className="text-right">
                  <p className="text-sm font-semibold text-white">{game.total_hours} hrs</p>
                  <p className="text-xs text-slate-500">{game.total_sessions} sesiones</p>
                </div>
              </div>
            ))
          ) : (
            <p className="text-sm text-slate-500 py-4">No hay datos de sesiones aún.</p>
          )}
        </div>
      </section>
    </main>
  );
}