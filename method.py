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
        select pnu, bunji, addr_1, addr_2, addr_3, addr_4, addr_5
        from kr_land_deal
        where trunc(update_date) >= trunc(sysdate-7)
        and ( 
                ( regexp_like(purpose,'공장|창고') and land_area_m2 >= 950 ) or
                ( not regexp_like(purpose,'공장|창고') and land_area_m2 >= 950 )
            )
        and addr_5 is not null
        order by update_date
    """
    oracle_cursor.execute(select_kr_land_deal_query)
    select_all = oracle_cursor.fetchall()
    print(f"select_all - {len(select_all)}건")
    # 새로운 데이터를 저장할 리스트 초기화
    new_select_all = []
    print(last_pnu_check_pnu)
    print()
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
    # dlg.print_control_identifiers()  # 속성값들 확인

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

def result_img():
    """
    가중치로 결과 도출
    :return:
    """
#     target_img_path = r'C:\Users\ysn39\파이썬 주피터\장앤장\캡챠\target_captcha.png'    #타켓 이미지 경로
    target_img_path = r'target_captcha.png'    #타켓 이미지 경로
    img_width = 200 #타켓 이미지 넓이
    img_height = 72 #타켓 이미지 높이
    img_length = 6  #타켓 이미지가 포함한 문자 수
    img_char = {'0', '1', '2', '3', '4', '5', '6', '7', '8', '9'}   #타켓 이미지안에 포함된 문자들
#     weights_path = r'C:\Users\ysn39\파이썬 주피터\장앤장\캡챠\gove24_weights.h5' #학습 결과 가중치 경로
    weights_path = r'gove24_20250708.h5' #학습 결과 가중치 경로
    AM = cc.ApplyModel(weights_path, img_width, img_height, img_length, img_char)   #결과 가중치를 가지는 모델 생성
    pred = AM.predict(target_img_path)  #결과 도출
    return pred


### 정부24 Login
def gov_login(driver, wait, user_id, user_pw):
    print(user_id)
    print(user_pw)
    while True:
        driver.get("https://plus.gov.kr/login/loginIdPwd")
        # 아이디 입력후 다음버튼 클릭
        wait.until(EC.presence_of_element_located((By.ID, """input_id""")))
        wait.until(EC.element_to_be_clickable((By.ID, """input_id"""))).send_keys(user_id)
        time.sleep(random.uniform(1, 2))
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, """btn.lg.btn-login"""))).click()

        # 비밀번호 입력
        wait.until(EC.presence_of_element_located((By.ID, """input_pwd""")))
        wait.until(EC.element_to_be_clickable((By.ID, """input_pwd"""))).send_keys(user_pw)

        # 캡차(보안문자) 이미지 캡쳐후 저장
        element1 = wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'img-captcha')))
        element_png = element1.screenshot_as_png
        with open("target_captcha.png", "wb") as file:
            file.write(element_png)

        # 저장된 캡차(보안문자) 이미지 해독
        capcha_number = result_img()

        # 보안문자 입력
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "input.lg"))).send_keys(capcha_number)
        time.sleep(1)
        # 로그인 버튼 클릭
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, """btn.lg.btn-login"""))).click()

        time.sleep(3)
        if "비밀번호 변경" in wait.until(EC.presence_of_element_located((By.TAG_NAME, "body"))).text:
            print("- 비밀번호 나중에 변경하기")
            wait.until(EC.presence_of_element_located((By.TAG_NAME, 'body'))).send_keys(Keys.END)
            time.sleep(1)
            wait.until(EC.presence_of_element_located((By.CLASS_NAME, """btn.xlg.tertiary"""))).click()
            print('- 다음에 변경하기 클릭')
        time.sleep(3)

        # '비밀번호 변경없이 진행합니다.' modal 처리
        time.sleep(1)
        body_text = wait.until(EC.presence_of_element_located((By.TAG_NAME, "body"))).text
        if '변경 없이 진행합니다.' in body_text:
            top_modal = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "iw-modal-alert.on")))
            top_modal.find_element(By.CLASS_NAME, "btn.tertiary.close-modal").click()

        # '정부24 개편 기념 이벤트' 모달 처리
        time.sleep(5)
        if 'iw-modal-auto main-popup on' in driver.page_source:
            print("'정부24 개편 기념 이벤트' 모달 처리 완료")
            popup_modal = wait.until(EC.presence_of_element_located((By.ID, "layerModal_main_popup")))
            popup_modal.find_element(By.TAG_NAME, 'button').click()

        # 로그인 성공여부 체크
        body_text = wait.until(EC.presence_of_element_located((By.TAG_NAME, "body"))).text
        if '아이디 또는 비밀번호가 일치하지 않습니다.' in body_text:
            print("로그인 실패")
        else:
            print("로그인 성공")
            return "로그인 성공"
        time.sleep(1)

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


# 크롬창 닫기
def driver_close(driver):
    # 현재 열려 있는 모든 창의 핸들을 가져옵니다.
    window_handles = driver.window_handles
    # 각 창을 하나씩 닫습니다.
    for handle in window_handles:
        driver.switch_to.window(handle)
        driver.close()
    driver.quit()


# 소요시간 계산산
def get_lab_time(start_time):
    end_time = time.time()  # 종료 시간 기록
    # 총 소요 시간 계산
    total_time = end_time - start_time
    # 분과 초로 변환
    minutes = int(total_time // 60)
    seconds = int(total_time % 60)
    return minutes, seconds