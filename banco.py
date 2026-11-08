"""Conexão com o banco de dados SQLite do QuadraFácil."""
import os
import sqlite3

PASTA = os.path.dirname(os.path.abspath(__file__))
CAMINHO_PADRAO = os.path.join(PASTA, "quadrafacil.db")


def conectar(caminho=CAMINHO_PADRAO):
    """Abre a conexão e liga a verificação de chaves estrangeiras."""
    con = sqlite3.connect(caminho)
    con.row_factory = sqlite3.Row
    con.execute("PRAGMA foreign_keys = ON")
    return con


def criar_banco(con):
    """Cria as tabelas (se não existirem) e cadastra as quadras iniciais."""
    with open(os.path.join(PASTA, "schema.sql"), encoding="utf-8") as arquivo:
        con.executescript(arquivo.read())

    if con.execute("SELECT COUNT(*) FROM quadra").fetchone()[0] == 0:
        con.executemany(
            "INSERT INTO quadra (nome, modalidade, valor_hora) VALUES (?, ?, ?)",
            [
                ("Quadra 1", "Society", 120.00),
                ("Quadra 2", "Futsal", 90.00),
                ("Quadra 3", "Vôlei de areia", 60.00),
            ],
        )
    con.commit()
