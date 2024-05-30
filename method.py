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
        last_pnu_check_pnu = None

    # kr_land_deal 테이블에서 데이터를 조회하는 쿼리
    select_kr_land_deal_query = """
        SELECT pnu, addr_1, addr_2, addr_3, addr_4, addr_5 
        FROM kr_land_deal 
        WHERE trunc(update_date) >= TRUNC(SYSDATE-7)
        ORDER BY update_date
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
    return oracle_connection, oracle_cursor, new_select_all


# von 연결및 아이피변경
# 아이피변경 함수(ip_change_click())와 별도로 만든 이유는
# vpn 연결상태에서는 db 접속이 안되기 때문에
# db 접속 -> vpn연결및 아이피변경 -> 수집
# 이렇게 하기 위함
def ip_connect_change():
    procs = findwindows.find_elements()
    for proc in procs:
        print(f"{proc} / 프로세스 : {proc.process_id}")
    input()
    app = application.Application(backend='win32').connect(title_re="COOL IP - 로그인")
    dlg = app['Dialog']
    dlg.print_control_identifiers()  #속성값들 확인

    combo_boxes = dlg.children(class_name="ComboBox")
    print(len(combo_boxes))
    if len(combo_boxes) == 2:
        combo_box_index = 0
    else:
        combo_box_index = 4
    combo_box = combo_boxes[combo_box_index]  # 서버/상품선택 Combo Box

    for cb in combo_boxes:
        print(cb.window_text())
    input()
    # 콤보박스 클릭하여 열기
    combo_box.click_input()
    dlg.child_window(control_type="ComboBox", found_index=4).click_input()
    for i in range(10):
        current_combobox_text = dlg.child_window(control_type="ComboBox", found_index=1).window_text()
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