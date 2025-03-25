import requests
import json
import argparse
import os

# Função para carregar o API Token do arquivo .zbxtoken
def get_api_token():
    token_file = ".zbxtoken"
    if not os.path.exists(token_file):
        print(f"Erro: Arquivo {token_file} não encontrado! Crie-o e adicione seu token.")
        exit(1)
    with open(token_file, "r") as file:
        return file.read().strip()

# Configuração da API do Zabbix
ZABBIX_URL = "https://zabbix-homolog.tre-ms.jus.br/zabbix/api_jsonrpc.php"
API_TOKEN = get_api_token()

# Cabeçalhos da requisição
HEADERS = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {API_TOKEN}"
}

# Função para chamar a API
def zabbix_get(method, output_fields=None, filters=None):
    payload = {
        "jsonrpc": "2.0",
        "method": method,
        "params": {"output": output_fields if output_fields else "extend"},
        "id": 1,
        "auth": None  # API Token já está no cabeçalho
    }

    if filters:
        payload["params"]["filter"] = filters

    response = requests.post(ZABBIX_URL, headers=HEADERS, data=json.dumps(payload))
    return response.json()

# Configuração do argparse
parser = argparse.ArgumentParser(description="Consulta a API do Zabbix")
parser.add_argument("method", choices=["host", "hostgroup", "user", "usergroup"], help="Método GET da API")
parser.add_argument("--fields", nargs="+", help="Campos a serem retornados (ex: hostid name)")
parser.add_argument("--filter_key", help="Chave do filtro (ex: host, name)")
parser.add_argument("--filter_value", help="Valor do filtro (ex: ServidorX)")

args = parser.parse_args()

# Configurar filtros, se fornecidos
filters = {args.filter_key: [args.filter_value]} if args.filter_key and args.filter_value else None

# Chamar a API e exibir o resultado formatado
resultado = zabbix_get(f"{args.method}.get", args.fields, filters)
print(json.dumps(resultado, indent=4))
