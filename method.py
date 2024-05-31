from moduls import *

# db연결후 update_date가 7일이전인 데이터만 받아오고
# 조회된 데이터 중 last_pnu_check_pnu 값 이후의 데이터만 new_select_all 리스트에 추가
def db_connect():
    print("DB 연결중...")
    # Oracle 데이터베이스에 연결
    oracle_connection = cx_Oracle.connect('jang', 'jang', 'www.ssucompanion.com:1521/SSUDB')
    oracle_cursor = oracle_connection.cursor()

    # last_pnu_check 테이블에서 pnu 컬럼의 첫 번째 값을 추출하는 쿼리
    select_first_pnu_query = "SELECT pnu FROM last_pnu_check FETCH FIRST 1 ROWS ONLY"
    oracle_cursor.execute(select_first_pnu_query)
    first_pnu = oracle_cursor.fetchone()

    # 추출한 pnu 값을 last_pnu_check_pnu 변수에 저장
    if first_pnu:
        last_pnu_check_pnu = first_pnu[0]
    else:
        last_pnu_check_pnu = None # 3171026228201730016

    # kr_land_deal 테이블에서 데이터를 조회하는 쿼리
    select_kr_land_deal_query = """
        SELECT pnu, bunji, addr_1, addr_2, addr_3, addr_4, addr_5
        FROM KR_LAND_DEAL
        WHERE TRUNC(UPDATE_DATE) >= TRUNC(SYSDATE-7)
        AND LAND_AREA_M2 >= 1650
    """
    oracle_cursor.execute(select_kr_land_deal_query)
    select_all = oracle_cursor.fetchall()

    # 새로운 데이터를 저장할 리스트 초기화
    new_select_all = []

    # 조회된 데이터 중 last_pnu_check_pnu 값 이후의 데이터만 출력하고 리스트에 추가
    if last_pnu_check_pnu is not None:
        start_printing = False
        for row in select_all:
            pnu_value = row[0]
            if start_printing:
                new_select_all.append(row)
            if pnu_value == last_pnu_check_pnu:
                start_printing = True
    else:
        new_select_all = select_all
    print('DB 연결 완료.')
    print(f"총 {len(new_select_all)}건")
    return oracle_connection, oracle_cursor, new_select_all


# von 연결및 아이피변경
# 아이피변경 함수(ip_change_click())와 별도로 만든 이유는
# vpn 연결상태에서는 db 접속이 안되기 때문에
# db 접속 -> vpn연결및 아이피변경 -> 수집
# 이렇게 하기 위함
def ip_connect_change():
    procs = findwindows.find_elements()
    for proc in procs:
        target_title = f"""{str(proc).split("'")[1]}"""
        print(target_title)
        if 'COOL IP' in target_title:
            break

    app = application.Application(backend='win32').connect(title_re=target_title)
    dlg = app['Dialog']
    dlg.print_control_identifiers()  # 속성값들 확인

    combo_box = dlg['ComboBox0']
    combo_box.click()  # 클릭하기
    for i in range(10):
        current_combobox_text = dlg['ComboBox0'].window_text()
        if current_combobox_text == '일반D':
            combo_box.type_keys("{1}")
            break
        else:
            combo_box.type_keys("{DOWN}")  # 첫 번째 항목 선택
    dlg.child_window(title="로그인", class_name="Button").click()
    print('VPN 로그인및 접속중..')

    while True:
        edit_control = dlg['접속상태Edit']  # '접속상태Edit'로 컨트롤 가져오기
        edit_text = edit_control.window_text()  # 텍스트 가져오기

        if edit_text == '- 유동 IP 연결 성공 -':
            print('연결성공')
            dlg.child_window(title="IP변경", class_name="Button").click()
            time.sleep(1)
            print("IP변경 완료")
            break
        else:

            time.sleep(1)

### 정부24 Login
def gov_login(driver, wait, user_id, user_pw):
    print(user_id)
    print(user_pw)
    while True:
        driver.get("https://www.gov.kr/nlogin/?Mcode=10003&regType=ctab")
        wait.until(EC.presence_of_element_located((By.ID, '아이디'))).click()
        wait.until(EC.presence_of_element_located((By.ID, 'userId'))).send_keys(user_id)
        wait.until(EC.presence_of_element_located((By.XPATH, """//button[text()='다음']"""))).click()

        wait.until(EC.presence_of_element_located((By.ID, 'pwd'))).send_keys(user_pw)
        wait.until(EC.presence_of_element_located((By.XPATH, """//button[text()='로그인']"""))).click()
        time.sleep(1)

        if "비밀번호 변경" in wait.until(EC.presence_of_element_located((By.TAG_NAME, "body"))).text:
            print("비밀번호 나중에 변경하기")
            wait.until(EC.presence_of_element_located((By.XPATH, """//a[text()='나중에 변경하기']"""))).click()
            print('나중에 변경하기 클릭')
            time.sleep(1)
        login_check = wait.until(EC.presence_of_element_located((By.TAG_NAME, 'body'))).text
        if '로그아웃' in login_check:
            print('로그인 성공')
            return "로그인 성공1"
        elif '로그인' in login_check:
            print("로그인 실패")


# COOL IP 제어
def ip_change_click():
    app = application.Application(backend='win32').connect(title_re="COOL IP - *")
    dlg = app['Dialog']
    dlg.child_window(title="IP변경", class_name="Button").click()
    time.sleep(1)
    print("IP변경")


# 모든 문자열 데이터의 탭 공백을 제거하는 함수 정의
def remove_tabs_from_dataframe(df):
    # 데이터프레임 내의 모든 문자열 데이터에서 탭 공백 제거
    return df.applymap(lambda x: x.replace('\t', '') if isinstance(x, str) else x)