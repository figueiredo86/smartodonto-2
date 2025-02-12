import pandas as pd

# Dados JSON
data = [
    {
        "id": 1,
        "Motivo": "00001",
        "Descricao": "COB - NEGOCIAÇÃO REALIZADO",
        "DetalhamentoIA": "Utilizar quando o cliente concluir uma negociação"
    },
    {
        "id": 2,
        "Motivo": "00002",
        "Descricao": "COB - NEGOCIAÇÃO NÃO REALIZADO",
        "DetalhamentoIA": "Utilizar quando após as tratativas não conseguir chegar a um acordo com o cliente"
    },
    {
        "id": 3,
        "Motivo": "00003",
        "Descricao": "COB - SEM CONDIÇÕES FINANCEIRAS",
        "DetalhamentoIA": "Cliente deseja pagar, mas no momento não tem condições financeiras"
    },
    {
        "id": 4,
        "Motivo": "00004",
        "Descricao": "COB - NÃO RECONHECE/LEMBRA COMPRA",
        "DetalhamentoIA": "Cliente não se recorda do débito mesmo após passar as informações dos produtos adquiridos"
    },
    {
        "id": 5,
        "Motivo": "00005",
        "Descricao": "COB - DESEJA CONTATO OPERADOR",
        "DetalhamentoIA": "Cliente deseja falar com um operador de cobrança"
    },
    {
        "id": 6,
        "Motivo": "00006",
        "Descricao": "VENDAS - DESEJA CONTATO OPERADOR",
        "DetalhamentoIA": "Cliente deseja falar com um operador de Vendas"
    },
    {
        "id": 7,
        "Motivo": "00007",
        "Descricao": "FORA TARGET - RESTRIÇÃO",
        "DetalhamentoIA": "Cliente tem restrição e não será possível liberar pedido"
    },
    {
        "id": 8,
        "Motivo": "00008",
        "Descricao": "FORA TARGET - FALECIDO",
        "DetalhamentoIA": "Cliente informa que é Falecido"
    },
    {
        "id": 9,
        "Motivo": "00009",
        "Descricao": "SEM INTERESSE - SEM CONDIÇÕES FINANCEIRAS",
        "DetalhamentoIA": "Cliente informa que não tem condições financeiras para realizar a compra nesse momento"
    },
    {
        "id": 10,
        "Motivo": "00010",
        "Descricao": "SEM INTERESSE - ACHOU CARO",
        "DetalhamentoIA": "Cliente gostou do produto, mas achou um valor caro"
    },
    {
        "id": 11,
        "Motivo": "00011",
        "Descricao": "SEM INTERESSE - NÃO ATENDE NECESSIDADES",
        "DetalhamentoIA": "Cliente achou que o produto não atende as necessidades dele"
    },
    {
        "id": 12,
        "Motivo": "00012",
        "Descricao": "SEM INTERESSE - EM TRATAMENTO MÉDICO",
        "DetalhamentoIA": "Cliente esta em tratamento médico e não quer adquirir nesse momento"
    },
    {
        "id": 13,
        "Motivo": "00013",
        "Descricao": "TELEFONE - NÃO É WHATSAPP",
        "DetalhamentoIA": "Numero do telefone não é do whatsapp"
    },
    {
        "id": 14,
        "Motivo": "00014",
        "Descricao": "TELEFONE - NUMERO NÃO É DO CLIENTE",
        "DetalhamentoIA": "Cliente identificado nesse número não existe ou não conhece"
    },
    {
        "id": 15,
        "Motivo": "00015",
        "Descricao": "TELEFONE - SEM CONTATO",
        "DetalhamentoIA": "Sem nenhum retorno do cliente nesse número"
    },
    {
        "id": 16,
        "Motivo": "00016",
        "Descricao": "AGEND - SAC",
        "DetalhamentoIA": "Cliente quer tratar com o SAC"
    },
    {
        "id": 17,
        "Motivo": "00017",
        "Descricao": "AGEND - LOG",
        "DetalhamentoIA": "Cliente quer retorno da Logistica"
    },
    {
        "id": 18,
        "Motivo": "00018",
        "Descricao": "AGEND - SAC",
        "DetalhamentoIA": "Cliente quer Cancelar o Pedido"
    },
    {
        "id": 19,
        "Motivo": "00019",
        "Descricao": "VENDAS - PAROU DE RESPONDER",
        "DetalhamentoIA": "Cliente começa a interagir mas para de responder"
    },
    {
        "id": 20,
        "Motivo": "00020",
        "Descricao": "NAO RETORNADO IA",
        "DetalhamentoIA": "IA não tratou ou Finalizou o atendimento"
    },
    {
        "id": 21,
        "Motivo": "00021",
        "Descricao": "CHIP BANIDO",
        "DetalhamentoIA": "Utilizar quando o atendimento é interrompdido por conta do banimento de Chip"
    }
]

# Converter JSON para DataFrame
df = pd.DataFrame(data)

# Salvar DataFrame em um arquivo Excel
df.to_excel("motivos.xlsx", index=False, engine='openpyxl')

print("Arquivo Excel 'motivos.xlsx' criado com sucesso!")