import requests
import json
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

# Função para criar uma regra de descoberta (drule.create)
def create_discovery_rule(name, ip_range, proxy_id=None):
    payload = {
        "jsonrpc": "2.0",
        "method": "drule.create",
        "params": {
            "name": name,
            "iprange": ip_range,
            "delay": "3600",  # Descobre a cada 1 hora
            "dchecks": [
                {
                    "type": 9,  # Verifica se a porta 10050 (Zabbix Agent) está aberta
                    "key_": "system.uname",
                    "ports": "10050"
                }
            ]
        },
        "id": 1,
        "auth": None
    }

    if proxy_id:
        payload["params"]["proxy_hostid"] = proxy_id  # Usa um proxy, se necessário

    response = requests.post(ZABBIX_URL, headers=HEADERS, data=json.dumps(payload))
    return response.json()

# Função para criar uma ação de descoberta (action.create)
def create_discovery_action(name, drule_id, group_id, template_id):
    payload = {
        "jsonrpc": "2.0",
        "method": "action.create",
        "params": {
            "name": name,
            "eventsource": 1,  # 1 = Descoberta de rede
            "status": 0,  # 0 = Ativado
            "esc_period": "0",
            "filter": {
                "evaltype": 0,
                "conditions": [
                    {
                        "conditiontype": 24,  # Condição: Regra de descoberta
                        "operator": 2,  # 2 = Igual
                        "value": str(drule_id)  # ID da regra de descoberta
                    }
                ]
            },
            "operations": [
                {
                    "operationtype": 2,  # Adicionar host
                },
                {
                    "operationtype": 4,  # Adicionar ao grupo de hosts
                    "opgroup": [{"groupid": str(group_id)}]
                },
                {
                    "operationtype": 6,  # Aplicar um template ao host descoberto
                    "optemplate": [{"templateid": str(template_id)}]
                }
            ]
        },
        "id": 1,
        "auth": None
    }

    response = requests.post(ZABBIX_URL, headers=HEADERS, data=json.dumps(payload))
    return response.json()

# Configurações (Substitua pelos valores corretos do seu Zabbix)
DISCOVERY_NAME = "Descoberta Automática"
IP_RANGE = "192.168.1.1-192.168.1.254"
GROUP_ID = "2"  # ID do grupo de hosts
TEMPLATE_ID = "10001"  # ID do template de monitoramento
PROXY_ID = None  # Use None se não for necessário

# Criar regra de descoberta
print("Criando regra de descoberta...")
drule_response = create_discovery_rule(DISCOVERY_NAME, IP_RANGE, PROXY_ID)
print(json.dumps(drule_response, indent=4))

if "result" in drule_response:
    drule_id = drule_response["result"]["druleids"][0]
    print(f"Regra de descoberta criada com sucesso! ID: {drule_id}")

    # Criar ação de descoberta
    print("Criando ação de descoberta...")
    action_response = create_discovery_action("Ação de Descoberta", drule_id, GROUP_ID, TEMPLATE_ID)
    print(json.dumps(action_response, indent=4))

    if "result" in action_response:
        print(f"Ação de descoberta criada com sucesso! ID: {action_response['result']['actionids'][0]}")
else:
    print("Erro ao criar a regra de descoberta!")
