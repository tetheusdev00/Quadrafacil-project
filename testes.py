"""Executa os casos de teste do plano de testes (Fase 5).

Usa um banco novo, na memória, a cada execução, para não mexer nos dados reais.
Uso:  python testes.py            -> mostra o resultado na tela
      python testes.py --json     -> também salva resultados_testes.json
"""
import json
import sqlite3
import sys
from datetime import date

import banco
import servicos
from servicos import ErroDeNegocio

HOJE = date(2026, 11, 2)       # data fixa para o teste não depender do dia em que roda
DIA = "2026-11-20"


def banco_novo():
    con = sqlite3.connect(":memory:")
    con.row_factory = sqlite3.Row
    con.execute("PRAGMA foreign_keys = ON")
    banco.criar_banco(con)
    return con


def total(con, tabela):
    return con.execute(f"SELECT COUNT(*) FROM {tabela}").fetchone()[0]


def tentar(funcao, *args, **kwargs):
    """Roda a função e devolve ('OK', resultado) ou ('ERRO', mensagem)."""
    try:
        return "OK", funcao(*args, **kwargs)
    except ErroDeNegocio as erro:
        return "ERRO", str(erro)


def executar():
    con = banco_novo()
    resultados = []

    def registrar(id_, o_que, esperado, obtido, passou):
        resultados.append({"id": id_, "teste": o_que, "esperado": esperado,
                           "obtido": obtido, "passou": bool(passou)})

    # --- Funcionalidade 1: cadastro de cliente -----------------------------
    status, r = tentar(servicos.cadastrar_cliente, con, "Marcos Vinícius", "(21) 98877-6655", "marcos@email.com")
    listados = [c["nome"] for c in servicos.listar_clientes(con)]
    registrar("CT01", "Cadastro de cliente com dados válidos",
              "Cliente salvo e exibido na lista",
              "Cliente salvo (código %s) e presente na lista" % r if status == "OK" and "Marcos Vinícius" in listados
              else f"Falhou: {r}",
              status == "OK" and "Marcos Vinícius" in listados)
    marcos_id = r

    antes = total(con, "cliente")
    status, r = tentar(servicos.cadastrar_cliente, con, "   ", "21988776611")
    registrar("CT02", "Cadastro sem preencher o nome",
              "Mensagem de erro e nada é salvo",
              f"Erro: \"{r}\" (clientes no banco: {total(con, 'cliente')})",
              status == "ERRO" and total(con, "cliente") == antes)

    status, r = tentar(servicos.cadastrar_cliente, con, "Ana Paula", "2198x")
    registrar("CT03", "Cadastro com telefone inválido (\"2198x\")",
              "Mensagem de erro e nada é salvo",
              f"Erro: \"{r}\" (clientes no banco: {total(con, 'cliente')})",
              status == "ERRO" and total(con, "cliente") == antes)

    status, r = tentar(servicos.cadastrar_cliente, con, "Outro Marcos", "21 98877 6655")
    registrar("CT04", "Cadastro com telefone já cadastrado",
              "Sistema impede o cadastro duplicado e avisa",
              f"Erro: \"{r}\" (clientes no banco: {total(con, 'cliente')})",
              status == "ERRO" and total(con, "cliente") == antes)

    # --- Funcionalidade 2: reserva de quadra --------------------------------
    status, r = tentar(servicos.criar_reserva, con, marcos_id, 1, DIA, "18:00", 2, hoje=HOJE)
    valor = r[1] if status == "OK" else None
    registrar("CT05", "Reserva válida: Quadra 1 (Society), 18:00, 2 horas",
              "Reserva salva com valor de R$ 240,00",
              f"Reserva {r[0]} salva, valor R$ {valor:.2f}".replace(".", ",") if status == "OK" else f"Erro: {r}",
              status == "OK" and valor == 240.0)

    antes = total(con, "reserva")
    status, r = tentar(servicos.criar_reserva, con, marcos_id, 1, DIA, "18:00", 2, hoje=HOJE)
    registrar("CT06", "Reservar a mesma quadra no mesmo horário já ocupado",
              "Sistema impede e avisa que o horário está ocupado",
              f"Erro: \"{r}\" (reservas no banco: {total(con, 'reserva')})",
              status == "ERRO" and total(con, "reserva") == antes)

    status, r = tentar(servicos.criar_reserva, con, marcos_id, 1, DIA, "19:00", 2, hoje=HOJE)
    registrar("CT07", "Reserva que invade parte do horário ocupado (19:00 às 21:00)",
              "Sistema impede e avisa que o horário está ocupado",
              f"Erro: \"{r}\" (reservas no banco: {total(con, 'reserva')})",
              status == "ERRO" and total(con, "reserva") == antes)

    status, r = tentar(servicos.criar_reserva, con, marcos_id, 1, DIA, "20:00", 2, hoje=HOJE)
    registrar("CT08", "Reserva logo após o fim de outra (20:00 às 22:00)",
              "Reserva permitida, pois não há sobreposição",
              f"Reserva {r[0]} salva, valor R$ {r[1]:.2f}".replace(".", ",") if status == "OK" else f"Erro: {r}",
              status == "OK")

    antes = total(con, "reserva")
    status, r = tentar(servicos.criar_reserva, con, marcos_id, 2, DIA, "22:00", 2, hoje=HOJE)
    registrar("CT09", "Reserva passando do horário de funcionamento (22:00 por 2 horas)",
              "Mensagem de erro e nada é salvo",
              f"Erro: \"{r}\" (reservas no banco: {total(con, 'reserva')})",
              status == "ERRO" and total(con, "reserva") == antes)

    linhas = servicos.reservas_do_dia(con, DIA)
    horarios = [f"{l['hora_inicio']} {l['quadra']}" for l in linhas]
    registrar("CT10", "Consultar as reservas do dia 20/11/2026",
              "Lista com as 2 reservas, em ordem de horário",
              f"{len(linhas)} reservas listadas: " + "; ".join(horarios),
              horarios == ["18:00 Quadra 1", "20:00 Quadra 1"])

    con.close()
    return resultados


def imprimir(resultados):
    print("PLANO DE TESTES - QUADRAFÁCIL")
    print("=" * 72)
    for r in resultados:
        marca = "PASSOU" if r["passou"] else "FALHOU"
        print(f"{r['id']} [{marca}] {r['teste']}")
        print(f"     esperado: {r['esperado']}")
        print(f"     obtido:   {r['obtido']}")
    ok = sum(r["passou"] for r in resultados)
    print("=" * 72)
    print(f"Resultado: {ok} de {len(resultados)} casos de teste passaram.")


if __name__ == "__main__":
    resultados = executar()
    imprimir(resultados)
    if "--json" in sys.argv:
        with open("resultados_testes.json", "w", encoding="utf-8") as f:
            json.dump(resultados, f, ensure_ascii=False, indent=2)
