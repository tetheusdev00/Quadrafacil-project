-- QuadraFácil - criação das tabelas (SQLite)

CREATE TABLE IF NOT EXISTS usuario (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    nome        TEXT NOT NULL,
    login       TEXT NOT NULL UNIQUE,
    senha_hash  TEXT NOT NULL,
    perfil      TEXT NOT NULL CHECK (perfil IN ('ATENDENTE', 'ADMIN'))
);

CREATE TABLE IF NOT EXISTS cliente (
    id        INTEGER PRIMARY KEY AUTOINCREMENT,
    nome      TEXT NOT NULL,
    telefone  TEXT NOT NULL UNIQUE,
    email     TEXT
);

CREATE TABLE IF NOT EXISTS quadra (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    nome        TEXT NOT NULL,
    modalidade  TEXT NOT NULL,
    valor_hora  REAL NOT NULL CHECK (valor_hora > 0),
    ativa       INTEGER NOT NULL DEFAULT 1
);

CREATE TABLE IF NOT EXISTS reserva (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    cliente_id   INTEGER NOT NULL REFERENCES cliente (id),
    quadra_id    INTEGER NOT NULL REFERENCES quadra (id),
    usuario_id   INTEGER REFERENCES usuario (id),
    data         TEXT NOT NULL,          -- AAAA-MM-DD
    hora_inicio  TEXT NOT NULL,          -- HH:MM
    hora_fim     TEXT NOT NULL,          -- HH:MM
    valor_total  REAL NOT NULL,
    status       TEXT NOT NULL DEFAULT 'ATIVA' CHECK (status IN ('ATIVA', 'CANCELADA'))
);
