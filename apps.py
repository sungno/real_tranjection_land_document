from method import *
from moduls import *
import account

# import sys
# import types


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
    ### 필요한 모듈 다운로드 및 로드
    # method.py 다운로드 및 로드
    method_url = "https://raw.githubusercontent.com/sungno/real_tranjection_land_document/main/method.py"
    method_content = download_script(method_url)
    load_module_from_string("method", method_content)

    # moduls.py 다운로드 및 로드
    moduls_url = "https://raw.githubusercontent.com/sungno/real_tranjection_land_document/main/moduls.py"
    moduls_content = download_script(moduls_url)
    load_module_from_string("moduls", moduls_content)

    # account.py 다운로드 및 로드
    account_url = "https://raw.githubusercontent.com/sungno/real_tranjection_land_document/main/account.py"
    account_content = download_script(account_url)
    load_module_from_string("account", account_content)

    # DB 연결및
    # oracle_connection, oracle_cursor, new_select_all = db_connect()
    # VPN 연결및 로그인
    ip_connect_change()

except Exception as e:
    print(f"[apps.py] An error occurred: {e}")
