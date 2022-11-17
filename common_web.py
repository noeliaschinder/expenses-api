import yaml
from pathlib import Path
import requests
import os
from dotenv import load_dotenv

load_dotenv()
BASE_URL = os.getenv('BASE_URL')
API_MAIN_USERNAME = os.getenv('API_MAIN_USERNAME')
API_MAIN_PASSWORD = os.getenv('API_MAIN_PASSWORD')

script_dir = os.path.dirname(__file__)
abs_file_path = os.path.join(script_dir, "config/")


def get_page_params(request, entity=None, action=None, rows=None, entity_id: int=None, entity_object: dict=None):
    view_config = None
    fields_config = None
    if entity is not None:
        view_config = get_view_config(entity, action)
        fields_config = get_fields_config(entity)
    return {
        "entity": entity,
        "site_name": "Expenses App",
        "action": action,
        "request": request,
        "title": f"{entity}-{action}",
        "menu": get_menu_config(),
        "rows": rows,
        "view_config": view_config,
        "fields_config": fields_config,
        "entityId": entity_id,
        "entityObject": entity_object
    }


def get_menu_config():
    menu = yaml.safe_load(Path(f'{abs_file_path}menu.yaml').read_text())
    return menu


def get_view_config(entity, action):
    config = yaml.safe_load(Path(f'{abs_file_path}config.yaml').read_text())
    entity_config = config[entity]
    return entity_config['views'][action]['fields']


def get_fields_config(entity):
    config = yaml.safe_load(Path(f'{abs_file_path}config.yaml').read_text())
    entity_config = config[entity]
    return entity_config['fields']


def get_entity_config(entity):
    config = yaml.safe_load(Path(f'{abs_file_path}config.yaml').read_text())
    return config[entity]


def call_api(uri, method: str = 'get'):
    api_url = f"{BASE_URL}/auth/token/"
    auth_response = requests.post(api_url, {'username': API_MAIN_USERNAME, 'password': API_MAIN_PASSWORD}).json()
    token = auth_response['access_token']
    api_url = f"{BASE_URL}/api{uri}"
    if method == 'get':
        response = requests.get(api_url, headers={'Authorization': 'Bearer ' + token})
        return response.json()
    elif method == 'delete':
        requests.delete(api_url, headers={'Authorization': 'Bearer ' + token})
