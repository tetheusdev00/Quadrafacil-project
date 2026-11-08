"""QuadraFácil - protótipo em modo texto (menu no terminal)."""
import sys

import banco
import servicos
from servicos import ErroDeNegocio


def ler(mensagem):
    """Lê o que a pessoa digitou. Se a entrada vier de um arquivo/script
    (e não do teclado), repete o texto na tela para o registro ficar completo."""
    valor = input(mensagem)
    if not sys.stdin.isatty():
        print(valor)
    return valor.strip()


def real(valor):
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def tela_cadastrar_cliente(con):
    print("\n--- CADASTRAR CLIENTE ---")
    nome = ler("Nome: ")
    telefone = ler("Telefone (com DDD): ")
    email = ler("E-mail (opcional): ")
    try:
        novo_id = servicos.cadastrar_cliente(con, nome, telefone, email)
        print(f"[OK] Cliente cadastrado com sucesso! (código {novo_id})")
    except ErroDeNegocio as erro:
        print(f"[ERRO] {erro}")


def tela_listar_clientes(con):
    print("\n--- CLIENTES CADASTRADOS ---")
    for c in servicos.listar_clientes(con):
        print(f"{c['id']:>3} | {c['nome']:<24} | {c['telefone']}")


def tela_nova_reserva(con):
    print("\n--- NOVA RESERVA ---")
    tela_listar_clientes(con)
    cliente_id = ler("\nCódigo do cliente: ")
    print("\nQuadras disponíveis:")
    for q in servicos.listar_quadras(con):
        print(f"{q['id']:>3} | {q['nome']:<9} | {q['modalidade']:<15} | {real(q['valor_hora'])}/hora")
    quadra_id = ler("\nCódigo da quadra: ")
    data = ler("Data (AAAA-MM-DD): ")
    hora = ler("Horário de início (HH:MM): ")
    duracao = ler("Duração em horas (1 a 3): ")
    try:
        reserva_id, valor = servicos.criar_reserva(
            con, int(cliente_id), int(quadra_id), data, hora, int(duracao)
        )
        print(f"[OK] Reserva {reserva_id} confirmada! Valor total: {real(valor)}")
    except ValueError:
        print("[ERRO] Código e duração devem ser números.")
    except ErroDeNegocio as erro:
        print(f"[ERRO] {erro}")


def tela_reservas_do_dia(con):
    print("\n--- RESERVAS DO DIA ---")
    data = ler("Data (AAAA-MM-DD): ")
    linhas = servicos.reservas_do_dia(con, data)
    if not linhas:
        print("Nenhuma reserva para esse dia.")
        return
    total = 0
    for r in linhas:
        print(f"{r['hora_inicio']}-{r['hora_fim']} | {r['quadra']:<9} | "
              f"{r['cliente']:<22} | {real(r['valor_total'])}")
        total += r["valor_total"]
    print(f"Total do dia: {real(total)}")


def menu():
    con = banco.conectar()
    banco.criar_banco(con)
    acoes = {
        "1": tela_cadastrar_cliente,
        "2": tela_nova_reserva,
        "3": tela_reservas_do_dia,
        "4": tela_listar_clientes,
    }
    while True:
        print("\n===== QUADRAFÁCIL =====")
        print("1 - Cadastrar cliente")
        print("2 - Nova reserva")
        print("3 - Reservas do dia")
        print("4 - Listar clientes")
        print("0 - Sair")
        opcao = ler("Escolha: ")
        if opcao == "0":
            print("Até logo!")
            break
        acoes.get(opcao, lambda _con: print("[ERRO] Opção inválida."))(con)
    con.close()


if __name__ == "__main__":
    menu()
