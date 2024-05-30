from moduls import *
from method import *


import account
from mdriver import *

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

def download_and_load_all_scripts(scripts_json_url):
    scripts_content = download_script(scripts_json_url)
    scripts_data = json.loads(scripts_content)
    for script_url in scripts_data["scripts"]:
        script_name = script_url.split('/')[-1].split('.')[0]
        print(script_name)
        script_content = download_script(script_url)
        load_module_from_string(script_name, script_content)

try:
    # ### 필요한 모듈 다운로드 및 로드
    # # method.py 다운로드 및 로드
    # method_url = "https://raw.githubusercontent.com/sungno/real_tranjection_land_document/main/method.py"
    # method_content = download_script(method_url)
    # load_module_from_string("method", method_content)
    #
    # # moduls.py 다운로드 및 로드
    # moduls_url = "https://raw.githubusercontent.com/sungno/real_tranjection_land_document/main/moduls.py"
    # moduls_content = download_script(moduls_url)
    # load_module_from_string("moduls", moduls_content)
    #
    # # account.py 다운로드 및 로드
    # account_url = "https://raw.githubusercontent.com/sungno/real_tranjection_land_document/main/account.py"
    # account_content = download_script(account_url)
    # load_module_from_string("account", account_content)
    #
    # # mdriver.py 다운로드 및 로드
    # mdriver_url = "https://raw.githubusercontent.com/sungno/real_tranjection_land_document/main/mdriver.py"
    # mdriver_content = download_script(mdriver_url)
    # load_module_from_string("mdriver", mdriver_content)

    # scripts.json 파일의 URL
    scripts_json_url = "https://raw.githubusercontent.com/sungno/real_tranjection_land_document/main/scripts.json"

    # 모든 스크립트 다운로드 및 로드
    download_and_load_all_scripts(scripts_json_url)



    ################### 실행 코드 시작 ###########################################
    # DB 연결및
    oracle_connection, oracle_cursor, new_select_all = db_connect()
    # # VPN 연결및 로그인
    # ip_connect_change()

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

        do = addr_1
        si = addr_2
        dong = addr_3
        if addr_4 is None:
            ri = ""
        else:
            ri = addr_4

        if '산' in addr_5:
            san = '산'
            addr_5 = addr_5.replace('산', "")
        else:
            san = '일반'

        if '-' in addr_5:
            jibun = addr_5.split("-")[0]
            boobun = addr_5.split("-")[1]
        else:
            jibun = addr_5
            boobun = ""

        print(f"{pnu} // {do} {si} {dong} {ri} {san} {jibun} {boobun}")

        try:
            jibun_1 = float(jibun)
        except Exception as e:
            print(e)
            print(f"INPUT 파일에서 지번 입력값 확인요망")
            print(e)
            fail_df = pd.DataFrame({
                'pnu': [pnu],
                '시도': [do],
                '시군구': [si],
                '읍면동': [dong],
                '리': [ri],
                '구분': [san],
                '번': [jibun],
                '지': [boobun],

            })
            # 파일이 존재하는지 확인
            file_exists = os.path.isfile(fail_file_name)
            # 파일이 존재하지 않으면 헤더 포함하여 저장, 존재하면 헤더 없이 추가
            fail_df.to_csv(fail_file_name, mode='a', header=not file_exists, index=False)
            continue

        try:
            if jibun != "":
                jibun = str(int(jibun))
            if boobun != "":
                boobun = str(int(boobun))

            ### 날짜
            tms = time.localtime()
            all_date = time.strftime('%Y-%m-%d', tms)
            all_date

            driver, wait = make_driver()
            # driver.get("https://www.naver.com")

        except Exception as e:
            print(f"[run code] An error occurred: {e}")






        break

except Exception as e:
    print(f"[apps.py] An error occurred: {e}")
