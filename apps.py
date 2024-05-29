from method import *
import sys
import types


def download_script(url):
    headers = {'Cache-Control': 'no-cache'}
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.text

def load_module_from_string(module_name, module_content):
    module = types.ModuleType(module_name)
    exec(module_content, module.__dict__)
    sys.modules[module_name] = module
    return module

try:
    # 필요한 모듈 다운로드 및 로드
    method_url = "https://raw.githubusercontent.com/sungno/real_tranjection_land_document/main/method.py"
    method_content = download_script(method_url)
    load_module_from_string("method", method_content)

    # account.py 다운로드 및 로드
    moduls_url = "https://raw.githubusercontent.com/sungno/real_tranjection_land_document/main/moduls.py"
    moduls_content = download_script(moduls_url)
    load_module_from_string("models", moduls_content)

    # DB 연결및
    oracle_connection, oracle_cursor, new_select_all = db_connect()
    print(new_select_all)
except Exception as e:
    print(f"[apps.py] An error occurred: {e}")
