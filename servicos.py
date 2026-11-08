"""Regras do QuadraFácil: cadastro de clientes e reserva de quadras."""
import re
from datetime import date, datetime

HORA_ABERTURA = 8      # a quadra abre às 08:00
HORA_FECHAMENTO = 23   # e fecha às 23:00
DURACAO_MAXIMA = 3     # horas por reserva


class ErroDeNegocio(Exception):
    """Erro de regra do sistema (dado inválido, horário ocupado etc.)."""


# ---------------------------------------------------------------------------
# Funcionalidade 1 - Cadastro de cliente
# ---------------------------------------------------------------------------
def cadastrar_cliente(con, nome, telefone, email=None):
    """Valida os dados e grava o cliente no banco. Devolve o id novo."""
    nome = (nome or "").strip()
    telefone = re.sub(r"\D", "", telefone or "")   # deixa só os números
    email = (email or "").strip() or None

    if not nome:
        raise ErroDeNegocio("O nome é obrigatório.")
    if len(telefone) not in (10, 11):
        raise ErroDeNegocio(
            "Telefone inválido. Informe DDD + número (10 ou 11 dígitos).")
    if email and not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email):
        raise ErroDeNegocio("E-mail inválido.")

    ja_existe = con.execute(
        "SELECT id FROM cliente WHERE telefone = ?", (telefone,)
    ).fetchone()
    if ja_existe:
        raise ErroDeNegocio(
            "Já existe um cliente cadastrado com esse telefone.")

    cursor = con.execute(
        "INSERT INTO cliente (nome, telefone, email) VALUES (?, ?, ?)",
        (nome, telefone, email),
    )
    con.commit()
    return cursor.lastrowid


def listar_clientes(con):
    """Consulta ao banco: devolve todos os clientes em ordem alfabética."""
    return con.execute("SELECT id, nome, telefone, email FROM cliente ORDER BY nome").fetchall()


# ---------------------------------------------------------------------------
# Funcionalidade 2 - Reserva de quadra
# ---------------------------------------------------------------------------
def criar_reserva(con, cliente_id, quadra_id, data, hora_inicio, duracao_h,
                  hoje=None, usuario_id=None):
    """Valida e grava uma reserva. Devolve (id da reserva, valor total)."""
    hoje = hoje or date.today()

    try:
        dia = datetime.strptime(data, "%Y-%m-%d").date()
    except ValueError:
        raise ErroDeNegocio("Data inválida. Use o formato AAAA-MM-DD.")
    if dia < hoje:
        raise ErroDeNegocio(
            "Não é possível reservar em uma data que já passou.")

    try:
        inicio = datetime.strptime(hora_inicio, "%H:%M")
    except ValueError:
        raise ErroDeNegocio("Horário inválido. Use o formato HH:MM.")
    if inicio.minute != 0:
        raise ErroDeNegocio("As reservas começam em hora cheia (ex.: 19:00).")

    if not isinstance(duracao_h, int) or not 1 <= duracao_h <= DURACAO_MAXIMA:
        raise ErroDeNegocio(f"A duração deve ser de 1 a {DURACAO_MAXIMA} horas.")

    hora_fim_num = inicio.hour + duracao_h
    if inicio.hour < HORA_ABERTURA or hora_fim_num > HORA_FECHAMENTO:
        raise ErroDeNegocio(
            f"As quadras funcionam das {HORA_ABERTURA:02d}:00 às {HORA_FECHAMENTO:02d}:00."
        )
    hora_fim = f"{hora_fim_num:02d}:00"

    cliente = con.execute("SELECT id FROM cliente WHERE id = ?", (cliente_id,)).fetchone()
    if not cliente:
        raise ErroDeNegocio("Cliente não encontrado.")
    quadra = con.execute(
        "SELECT id, valor_hora FROM quadra WHERE id = ? AND ativa = 1", (quadra_id,)
    ).fetchone()
    if not quadra:
        raise ErroDeNegocio("Quadra não encontrada ou desativada.")

    # Consulta ao banco: existe reserva ativa que se sobreponha a esse horário?
    conflito = con.execute(
        """SELECT id FROM reserva
            WHERE quadra_id = ? AND data = ? AND status = 'ATIVA'
              AND hora_inicio < ? AND hora_fim > ?""",
        (quadra_id, data, hora_fim, hora_inicio),
    ).fetchone()
    if conflito:
        raise ErroDeNegocio(
            "Horário indisponível: a quadra já está reservada nesse período.")

    valor_total = quadra["valor_hora"] * duracao_h
    cursor = con.execute(
        """INSERT INTO reserva
               (cliente_id, quadra_id, usuario_id, data, hora_inicio, hora_fim, valor_total)
           VALUES (?, ?, ?, ?, ?, ?, ?)""",
        (cliente_id, quadra_id, usuario_id, data, hora_inicio, hora_fim, valor_total),
    )
    con.commit()
    return cursor.lastrowid, valor_total


def reservas_do_dia(con, data):
    """Consulta ao banco: reservas ativas de um dia, em ordem de horário."""
    return con.execute(
        """SELECT r.hora_inicio, r.hora_fim, q.nome AS quadra, q.modalidade,
                  c.nome AS cliente, c.telefone, r.valor_total
             FROM reserva r
             JOIN cliente c ON c.id = r.cliente_id
             JOIN quadra  q ON q.id = r.quadra_id
            WHERE r.data = ? AND r.status = 'ATIVA'
            ORDER BY r.hora_inicio, q.nome""",
        (data,),
    ).fetchall()


def listar_quadras(con):
    """Consulta ao banco: quadras ativas."""
    return con.execute(
        "SELECT id, nome, modalidade, valor_hora FROM quadra WHERE ativa = 1 ORDER BY id"
    ).fetchall()
