-- 1. Habilitar extensión para generación de UUIDs
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 2. Tabla de Usuarios
CREATE TABLE public.users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    username VARCHAR(50) UNIQUE NOT NULL,
    discord_id VARCHAR(50) NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 3. Catálogo de Juegos (Mapeo de Ejecutables de la PC)
CREATE TABLE public.games (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    title VARCHAR(100) NOT NULL,
    process_name VARCHAR(100) UNIQUE NOT NULL, -- Nombre exacto del archivo ejecutable (ej: 2XKO.exe)
    category VARCHAR(50) DEFAULT 'General',
    cover_image_url TEXT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 4. Sesiones de Juego (Registradas por el Agente Local)
CREATE TABLE public.game_sessions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
    game_id UUID NOT NULL REFERENCES public.games(id) ON DELETE CASCADE,
    start_time TIMESTAMPTZ NOT NULL,
    end_time TIMESTAMPTZ NULL,
    duration_seconds INT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 5. Registro de Victorias/Derrotas y Contexto (Win/Loss Log)
CREATE TABLE public.match_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_id UUID NOT NULL REFERENCES public.game_sessions(id) ON DELETE CASCADE,
    wins INT DEFAULT 0,
    losses INT DEFAULT 0,
    rank_tier VARCHAR(50) NULL, -- Ej: "Oro III", "Diamond 1", etc.
    notes TEXT NULL,
    played_with_discord JSONB DEFAULT '[]'::jsonb, -- Almacena array de IDs/Nombres de Discord
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexación estratégica para consultas rápidas en el Dashboard
CREATE INDEX idx_sessions_user_game ON public.game_sessions(user_id, game_id);
CREATE INDEX idx_sessions_start_time ON public.game_sessions(start_time);
CREATE INDEX idx_games_process_name ON public.games(process_name);


-- Usuario de desarrollo
INSERT INTO public.users (id, email, username)
VALUES ('a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11', 'dev@local.com', 'DevPlayer');

-- Catálogo base de juegos conocidos
INSERT INTO public.games (title, process_name, category) VALUES
('2XKO', '2XKO.exe', 'Fighting'),
('Street Fighter 6', 'StreetFighter6.exe', 'Fighting'),
('World of Warcraft', 'Wow.exe', 'MMORPG'),
('Valorant', 'VALORANT-Win64-Shipping.exe', 'FPS');