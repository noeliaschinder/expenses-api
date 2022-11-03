import yaml
from pathlib import Path
import requests


def get_page_params(request, entity, action, rows=None, entity_id: int = '', entityObject: dict = None):
    return {
        "entity": entity,
        "site_name": "Expenses App",
        "action": action,
        "request": request,
        "title": f"{entity}-{action}",
        "menu": get_menu_config(),
        "rows": rows,
        "view_config": get_view_config(entity, action),
        "fields_config": get_fields_config(entity),
        "entityId": entity_id,
        "entityObject": entityObject
    }


def get_menu_config():
    menu = yaml.safe_load(Path('config/menu.yaml').read_text())
    return menu


def get_view_config(entity, action):
    config = yaml.safe_load(Path('config/config.yaml').read_text())
    entity_config = config[entity]
    # fields_settings = entity_config['fields']
    # action_fields = entity_config['views'][action]['fields']
    # for field in action_fields:
    #     print(fields_settings[field])
    return entity_config['views'][action]['fields']


def get_fields_config(entity):
    config = yaml.safe_load(Path('config/config.yaml').read_text())
    entity_config = config[entity]
    return entity_config['fields']


def get_entity_config(entity):
    config = yaml.safe_load(Path('config/config.yaml').read_text())
    return config[entity]


def call_api(uri, method: str = 'get'):
    api_url = "http://127.0.0.1:8000/auth/token/"
    auth_response = requests.post(api_url, {'username': 'noelia', 'password': 'test123456'}).json()
    token = auth_response['access_token']
    api_url = f"http://127.0.0.1:8000/api{uri}"
    if method == 'get':
        response = requests.get(api_url, headers={'Authorization': 'Bearer ' + token})
        return response.json()
    elif method == 'delete':
        requests.delete(api_url, headers={'Authorization': 'Bearer ' + token})

