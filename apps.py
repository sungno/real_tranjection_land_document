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

    ################### 실행 코드 시작 ###########################################
    # DB 연결및
    oracle_connection, oracle_cursor, new_select_all = db_connect()
    # VPN 연결및 로그인
    ip_connect_change()

    file_name = "실거래데이터_토지대장_결과.csv"
    fail_file_name = "실거래데이터_토지대장_실패.csv"

    cnt = 0
    total_box = []
    fail_total_box = []
    for pnu, addr_1, addr_2, addr_3, addr_4, addr_5 in new_select_all:
        cnt += 1
        user_id = random.choice(account.id_list)
        user_pw = account.pw_dict[user_id]
        print(user_id, user_pw)

except Exception as e:
    print(f"[apps.py] An error occurred: {e}")
