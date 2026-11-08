# QuadraFácil

Protótipo de um sistema de reserva de quadras esportivas (Projeto Integrado Interdisciplinar).

## O que ele faz
- **Cadastrar cliente** (valida nome, telefone e e-mail; não deixa repetir telefone)
- **Reservar quadra** (confere horário de funcionamento, impede horário ocupado e calcula o valor)
- **Consultar reservas do dia** e **listar clientes**

## Como rodar
Precisa apenas do Python 3 (o SQLite já vem junto).

```bash
python main.py      # abre o menu; o banco quadrafacil.db é criado na primeira execução
python testes.py    # roda os 10 casos de teste do plano
```

## Arquivos
| Arquivo | Função |
|---|---|
| `schema.sql` | Tabelas do MER (usuario, cliente, quadra, reserva) |
| `banco.py` | Conexão com o SQLite e criação do banco |
| `servicos.py` | Regras de negócio e consultas |
| `main.py` | Menu em modo texto |
| `testes.py` | Casos de teste |
| `docs/` | Diagramas, wireframes e prints usados no relatório |
