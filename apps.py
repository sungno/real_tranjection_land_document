from selenium.common import TimeoutException

from moduls import *
from method import *
import account
from mdriver import *
from datetime import datetime

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
    # scripts.json 파일의 URL
    scripts_json_url = "https://raw.githubusercontent.com/sungno/real_tranjection_land_document/main/scripts.json"
    # 모든 스크립트 다운로드 및 로드
    download_and_load_all_scripts(scripts_json_url)



    ################### 실행 코드 시작 ###########################################
    # DB 연결및
    oracle_connection, oracle_cursor, new_select_all = db_connect()

    # VPN 연결및 로그인
    # ip_connect_change()

    file_name = "실거래데이터_토지대장_결과.csv"
    fail_file_name = "실거래데이터_토지대장_실패.csv"

    ip_cnt = 0
    success_cnt = 0
    fail_cnt = 0

    total_box = []
    fail_total_box = []

    for pnu, bunji, addr_1, addr_2, addr_3, addr_4, addr_5 in new_select_all:
        start_time = time.time()  # 시작 시간 기록
        ip_cnt += 1
        user_id = random.choice(account.id_list)
        user_pw = account.pw_dict[user_id]
        print(user_id, user_pw)
        print(pnu, bunji, addr_1, addr_2, addr_3, addr_4, addr_5)
        do = addr_1
        si = addr_2
        dong = addr_3
        if addr_4 is None:
            ri = ""
        else:
            ri = addr_4

        if '산' in bunji:
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

        current_row = f"[{ip_cnt}] // {do, si, dong, ri, san, jibun, boobun}"
        print(f"■ {current_row} 수집 시도....")
        try:
            jibun_1 = float(jibun)
        except Exception as e:
            print(f"★ {current_row} 수집 실패")
            print(f"★ 토지대장_VM.csv 파일에서 지번 입력값 확인요망")
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
            total_mail = f"{do} {si} {dong} {ri} {san} {jibun} {boobun}"
            fail_cnt += 1
            continue

        try:
            if jibun != "":
                jibun = str(int(jibun))
            if boobun != "":
                boobun = str(int(boobun))

            ### 날짜
            tms = time.localtime()
            all_date = time.strftime('%Y-%m-%d', tms)

            driver, wait = make_driver()
            gov_login(driver, wait, user_id, user_pw)
            print(do)

            print('토지임야 체크')
            for c in wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, "swiper-slide"))):
                if '토지(임야)' in c.text:
                    c.click()
                    print('토지(임야) 클릭')
                    break
            wait.until(EC.presence_of_element_located((By.XPATH, """//a[text()='발급하기']"""))).click()
            print("발급하기 클릭")
            try:
                # wait.until(EC.presence_of_element_located((By.CLASS_NAME, "btn_tab_arrow")))
                # time.sleep(3)
                # wait.until(EC.presence_of_element_located((By.CLASS_NAME, "btn_tab_arrow"))).click()
                # print("펼쳐보기 클릭")
                #
                # # 토지(임야)대장열람 클릭(라디오버튼)
                # wait.until(EC.presence_of_element_located(
                #     (By.XPATH, """//a[@onclick="javascript:refreshFormRadio('03');"]""")))
                # print("토지(임야)대장열람 클릭(라디오버튼) 체크")
                # time.sleep(1)
                # wait.until(EC.element_to_be_clickable(
                #     (By.XPATH, """//a[@onclick="javascript:refreshFormRadio('03');"]"""))).click()
                # print("토지(임야)대장열람 클릭(라디오버튼) 클릭")
                wait.until(EC.presence_of_element_located((By.XPATH, "//span[text()='토지(임야)대장열람']"))).click()
                time.sleep(3)

                if san == '산':
                    wait.until(EC.presence_of_element_located((By.XPATH, """//label[text()='임야 대장']"""))).click()
                    print("임야대장 클릭(산)")

                driver.find_element(By.ID, "btnAddress").click()  # 대상토지 소재지 검색
                print('대상 토지 소재지 주소검색 클릭')
                time.sleep(1)
                driver.switch_to.window(driver.window_handles[-1])  # 새창 변환
                print("새창변환")
                time.sleep(1)
                driver.find_element(By.NAME, "txtAddr").send_keys(dong)  # 동읍면 입력
                print("동읍면 입력")
                driver.execute_script("isValid();return false;")  # 검색버튼
                print("검색버튼 클릭")
            except:
                # print("펼쳐보기 EXCEPTION!")
                # time.sleep(5)
                # driver.switch_to.window(driver.window_handles[-1])  # 새창 변환
                # driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.HOME)
                # time.sleep(1)
                # wait.until(EC.presence_of_element_located((By.CLASS_NAME, "btn_tab_arrow")))
                # time.sleep(10)
                # wait.until(EC.presence_of_element_located((By.CLASS_NAME, "btn_tab_arrow"))).click()
                # print("펼쳐보기 클릭")
                #
                # # 토지(임야)대장열람 클릭(라디오버튼)
                # wait.until(EC.presence_of_element_located(
                #     (By.XPATH, """//a[@onclick="javascript:refreshFormRadio('03');"]""")))
                # print("토지(임야)대장열람 클릭(라디오버튼) 체크")
                # time.sleep(1)
                # wait.until(EC.element_to_be_clickable(
                #     (By.XPATH, """//a[@onclick="javascript:refreshFormRadio('03');"]"""))).click()
                # print("토지(임야)대장열람 클릭(라디오버튼) 클릭")
                wait.until(EC.presence_of_element_located((By.XPATH, "//span[text()='토지(임야)대장열람']"))).click()
                time.sleep(3)
                if san == '산':
                    wait.until(EC.presence_of_element_located((By.XPATH, """//label[text()='임야 대장']"""))).click()
                    print("임야대장 클릭(산)")

                driver.find_element(By.ID, "btnAddress").click()  # 대상토지 소재지 검색
                print('대상 토지 소재지 주소검색 클릭')
                time.sleep(1)
                driver.switch_to.window(driver.window_handles[-1])  # 새창 변환
                print("새창변환")
                time.sleep(1)
                driver.find_element(By.NAME, "txtAddr").send_keys(dong)  # 동읍면 입력
                print("동읍면 입력")
                driver.execute_script("isValid();return false;")  # 검색버튼
                print("검색버튼 클릭")

            aa = driver.find_elements(By.CSS_SELECTOR, "#resultList > a")

            ## 선택해야할 총주소 만들기
            ## 시가 없는경우 리,동이 없는경우등에 맞춰 조건문으로 거르기
            if ri == "":
                # print('ri가 없으면')
                re_dong = re.sub('[^가-힣]', '', dong)
                total_mail = f"{do} {si} {dong}({re_dong})"
            elif si == "":
                # print('si가 없으면')
                re_dong = re.sub('[^가-힣]', '', dong)
                total_mail = f"{do} {dong}({ri})"
            else:
                # print('정상적이면')
                total_mail = f"{do} {si} {dong}({ri})"

            ### 주소선택창에서 해당주소가 있을때까지 비교후 클릭
            print('주소선택창에서 해당주소가 있을때까지 비교후 클릭')
            for i in aa:
                if ri == '':
                    if f'{si}' in i.text and f'({dong})' in i.text:
                        i.send_keys(Keys.ENTER)
                        break
                elif dong == "":
                    if f'{si}' in i.text and f'({ri})' in i.text:
                        i.send_keys(Keys.ENTER)
                        break
                else:
                    if f'{si}' in i.text and f'({ri})' in i.text:
                        i.send_keys(Keys.ENTER)
                        break
            print("클릭 완료")
            ### 주소 검색했을때 행정기관 선택하라는 팝업창이 나온다면
            driver.switch_to.window(driver.window_handles[-1])
            source = driver.page_source
            html = BeautifulSoup(source, 'lxml')
            if '검색결과' in str(html):
                driver.find_elements(By.TAG_NAME, "a")[1].click()

            ### 지번및 부번 입력
            driver.switch_to.window(driver.window_handles[-1])
            wait.until(EC.presence_of_element_located((By.NAME, "토지임야대장신청서/IN-토지임야대장신청서/신청토지소재지/주소정보/상세주소/번지"))).send_keys(
                jibun)
            print('지번 입력 완료')
            wait.until(EC.presence_of_element_located((By.NAME, "토지임야대장신청서/IN-토지임야대장신청서/신청토지소재지/주소정보/상세주소/호"))).send_keys(
                boobun)
            print('부번 입력 완료')
            ### 연혁 인쇄 유무(히스토리)
            wait.until(EC.presence_of_element_located((By.XPATH, """//label[text()='인쇄함']"""))).click()
            print(' 연혁 인쇄 유무 -> 인쇄함 클릭 ')
            ### 민원신청하기
            wait.until(EC.presence_of_element_located((By.ID, "btn_end"))).click()
            print("민원신청하기 클릭")

            # 팝업 처리
            try:
                temporary_wait = WebDriverWait(driver, 10)
                elements = temporary_wait.until(EC.presence_of_element_located((By.CLASS_NAME, "survey_pop")))
                wait.until(EC.presence_of_element_located((By.CLASS_NAME, "pop_btn_close"))).click()
            except TimeoutException:
                print("팝업 없음")


            driver.switch_to.window(driver.window_handles[-1])  # 새창 변환

            ### 문서 열람후 새창
            time.sleep(5)
            wait.until(EC.presence_of_element_located((By.CLASS_NAME, "ibtn.small.dark"))).click()  # 열람문서 클릭
            print("열람문서 클릭")
            driver.switch_to.window(driver.window_handles[-1])  # 새창 변환

            ### 지번-부번 과 열람문서의 지번과 일치하면 진행, 일치하지 않으면 새로고침후 다시 확인
            ### (5번 반복후 그래도 일치하지 않으면 예외처리하고 실패 목록에 넣기
            print("input 파일의 지번-부번과 열람문서 지번-부번이 같은지 체크")
            if boobun == "":
                total_jibun = str(jibun)
            else:
                total_jibun = str(f"{jibun}-{boobun}")

            for infi in range(5):
                document_jibun = driver.find_elements(By.CLASS_NAME, "BR1")[3].text

                document_jibun = wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, "BR1")))[3].text
                document_jibun = document_jibun.replace("산 ", "")

                print(f"total_jibun -- {total_jibun}")
                print(f"document_jibun -- {document_jibun}")
                if document_jibun == total_jibun:
                    print("   지번 일치")
                    break

                else:
                    print("   지번 불일치")
                    driver.close()
                    driver.switch_to.window(driver.window_handles[-1])
                    driver.refresh()
                    time.sleep(5)

                    wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, "ibtn.small.dark")))[
                        infi + 1].click()  # 열람문서 클릭
                    time.sleep(2)
                    driver.switch_to.window(driver.window_handles[-1])  # 새창 변환
                    time.sleep(2)

                if infi == 4:
                    break

            driver.switch_to.window(driver.window_handles[-1])  # 새창 변환
            time.sleep(2)

            #################### 수집 시작 ########################################
            #################### 수집 시작 ########################################
            #################### 수집 시작 ########################################
            #################### 수집 시작 ########################################
            print('토지대장 데이터 수집시작...')
            ### 공유지연명부 여부
            if '연명부' in driver.find_element(By.TAG_NAME, "body").text:
                category = '공유지연명부'
            else:
                category = '소유자'

            ### 고유번호
            pnu = driver.find_element(By.CLASS_NAME, "B1R2").text
            pnu = pnu.replace("-", "").replace(" ", "")

            ### 법정동명(토지소재)
            legal_dongname = driver.find_elements(By.CLASS_NAME, "B1R2")[1].text

            # ### 지번-부번
            # if boobun == "":
            #     total_jibun = jibun
            # else:
            #     total_jibun = f"{jibun}-{boobun}"

            ### 현재페이지의 html 파싱
            source = driver.page_source
            html = BeautifulSoup(source, 'lxml')

            ### 토지표시 목록중 마지막 값들을 수집하기위해 페이지 개수를 확인해야함
            ### 토지표시와 소유자 항목들이 같은 table에 묶여 있었고 페이지별로도 나눠져 있어서
            ### 지목, 면적, 사유 별로 모두 수집한후 마지막 값들만 가져오려고 한다.
            ### 각 페이지의 테이블
            l2_box = []
            for class_l2 in html.find_all('table', attrs={'class': 'L2'}):
                if '토     지    표    시' in class_l2.text:  # 임야대장에서 '토     지    표    시'라는 text가 있다면
                    l2_box.append(class_l2)  # l2_box 라는 list에 append
            ground_part_box = []
            for l2 in l2_box:
                ground_part_box.append(l2.find('tbody').find_all('tr')[3:])  # 3번째 index부터 값이 있음

            ### 토지표시와 , 소유자를 구분할수가 없어서
            ### 각 행의 첫번째줄, 두번째줄을 리스트에 담아서 구분
            line_1st_box = []  # tr중 홀수라인
            line_2nd_box = []  # tr중 짝수라인
            for gb in ground_part_box:
                for i, g in enumerate(gb):
                    if (i + 1) % 2 != 0:
                        line_1st_box.append(g)
                    else:
                        line_2nd_box.append(g)

            owrner_date_box = []
            owrner_reason_box = []
            owrner_mail_box = []
            owrner_name_box = []
            owrner_code_box = []
            cnt_box = []
            share_box = []
            category_box = []
            for st1 in line_1st_box:
                ### 지목
                ### 지목은 마지막 값만 넣으면 되기대문에 변수 jimok 에 대입
                ### 값이 '\n\n' 이면 거르기
                if st1.find_all('td')[0].text != '\n\n':
                    # print(st1.find_all('td')[0].text)
                    jimok = st1.find_all('td')[0].text.split(")")[-1]

                ### 면적
                ### 면적은 마지막 값만 넣으면 되기대문에 변수 m2 에 대입
                ### 값이 '' 이면 거르기
                if st1.find_all('td')[1].text != '':
                    # print(st1.find_all('td')[1].text)
                    m2 = st1.find_all('td')[1].text

                ### 토지표시변경사유, 토지표시변경일자
                ### 토지표시변경사유, 토지표시변경일자는 마지막 값만 넣으면 되기대문에 각각 변수 reason, reason_date에 대입
                if '여백' in st1.find_all('td')[2].text:
                    pass
                elif st1.find_all('td')[2].text == "":
                    pass
                else:
                    #             test_box.append(st1.find_all('td')[2].text)
                    reason = st1.find_all('td')[2].text.replace("\t", "").split("\n")[-1]
                    reason_date = st1.find_all('td')[2].text.replace("\t", "").split("\n")[:-1]
                    reason_date = \
                        " ".join(reason_date).replace("년  ", " - ").replace("월  ", " - ").replace("일 ", "").split(")")[
                            -1]

                ### 소유권변동일자
                ### 소유권변동일자는 첫번째줄에서 4번째 td에 해당
                # if st1.find_all('td')[3].text != "":
                #     owrner_date_box.append(
                #         st1.find_all('td')[3].text.replace("\n", "").replace("\t", "").replace("년 ", "-").replace("월 ",
                #                                                                                                   "-").replace(
                #             "일 ", ""))

                owrner_date_box.append(
                    st1.find_all('td')[3].text.replace("\n", "").replace("\t", "").replace("년 ", "-").replace("월 ",
                                                                                                              "-").replace(
                        "일 ", ""))

                ### 소유자 주소
                if '여백' in st1.find_all('td')[4].text:
                    break
                else:
                    owrner_mail_box.append(st1.find_all('td')[4].text)

            for nd2, st1 in zip(line_2nd_box, line_1st_box):
                ### 소유권변동원인
                if nd2.find_all('td')[0].text != "":
                    owrner_reason_box.append(nd2.find_all('td')[0].text[4:])
                elif '여백' in st1.find_all('td')[4].text:
                    break
                else:
                    owrner_reason_box.append("")

                ### 소유자명
                if nd2.find_all('td')[1].text != "":
                    owrner_name_box.append(nd2.find_all('td')[1].text)
                elif '여백' in st1.find_all('td')[4].text:
                    break
                else:
                    owrner_name_box.append("")

                ### 소유자코드(주민,법인)
                if nd2.find_all('td')[2].text != "":
                    owrner_code_box.append(nd2.find_all('td')[2].text)
                elif '여백' in st1.find_all('td')[4].text:
                    break
                else:
                    owrner_code_box.append("")

            ### 순번(등기순위번호)
            for i, o in enumerate(owrner_reason_box):
                cnt_box.append(i + 1)
                share_box.append("")
                category_box.append('소유자')

            ### 공유지 연명부가 있으면
            if category == '공유지연명부':
                print('공유지 연명부 있음')
                sh_cnt = []
                sh_change_date_box = []
                sh_share_box = []
                sh_mail_box = []
                sh_code_box = []

                sh_change_reason_box = []
                sh_name_box = []
                sh_category_box = []

                for p in html.find_all('div', attrs={'class': 'page'}):
                    if '공유지 연명부' in p.text:

                        ppp = p.find_all('table')
                        share = ppp[-1].find("tbody").find_all('tr')[7:]

                        ### 첫째줄의 정보와, 둘째쭐의 정보를 나눠서 각각 리스트 담기기
                        share_line_1st_box = []
                        share_line_2nd_box = []
                        for i, s in enumerate(share):
                            if (i + 1) % 2 != 0:
                                share_line_1st_box.append(s)
                            else:
                                share_line_2nd_box.append(s)

                        ### 공유지 연명부 첫번째 줄 ( 순번, 변공일자 , 소유권지분, 주소 , 등록번호 / 총 5개)
                        for sh1 in share_line_1st_box:
                            ### 공유지 연명부 순번
                            if sh1.find_all('td')[0].text == '\n\n':
                                pass
                            elif sh1.find_all('td')[0].text == '':
                                pass
                            else:
                                sh_cnt.append(sh1.find_all('td')[0].text)
                                sh_category_box.append("공유지 연명부")

                            ### 공유지 연명부 변동일자
                            if sh1.find_all('td')[1].text == '\n\n':
                                pass
                            elif sh1.find_all('td')[1].text == '':
                                pass
                            else:

                                sh_change_date_box.append(
                                    sh1.find_all('td')[1].text.replace("\n", "").replace("\t", "").replace("년 ",
                                                                                                           "-").replace(
                                        "월",
                                        "-").replace(
                                        "일 ", "").replace(" ", ""))

                            ### 공유지 연명부 소유권 지분
                            if sh1.find_all('td')[2].text == '\n\n':
                                pass
                            elif sh1.find_all('td')[2].text == '':
                                pass
                            else:
                                sh_share_box.append(sh1.find_all('td')[2].text)

                            ### 공유지 연명부 소유자 주소
                            if sh1.find_all('td')[3].text == '\n\n':
                                pass
                            elif sh1.find_all('td')[3].text == '':
                                pass
                            elif '여백' in sh1.find_all('td')[3].text:
                                pass
                            else:
                                sh_mail_box.append(sh1.find_all('td')[3].text)

                            ### 공유지 연명부 소유자 등록번호
                            if sh1.find_all('td')[4].text == '\n\n':
                                pass
                            elif sh1.find_all('td')[4].text == '':
                                pass
                            elif '여백' in sh1.find_all('td')[4].text:
                                pass
                            else:
                                # print(sh1.find_all('td')[4].text)
                                sh_code_box.append(sh1.find_all('td')[4].text)

                        ### 공유지 연명부 두번째 줄 ( 번동원인, 성명 또는 명칭 / 총 2개)
                        for sh2 in share_line_2nd_box:
                            ### 공유지 연명부 변동원인
                            if sh2.find_all('td')[0].text == '\n\n':
                                pass
                            elif sh2.find_all('td')[0].text == '':
                                pass
                            else:
                                sh_change_reason_box.append(sh2.find_all('td')[0].text[4:])

                            ### 공유지 연명부 성명 또는 명칭
                            if sh2.find_all('td')[1].text == '\n\n':
                                pass
                            elif sh2.find_all('td')[1].text == '':
                                pass
                            else:
                                # print(sh2.find_all('td')[1].text)
                                sh_name_box.append(sh2.find_all('td')[1].text)

                        ### 공유지 연명부가 있다면 양식에 맞게 저장하기위해 토지대장의 항목과 공유지연명부의 항목을 합치기
                        total_date_box = owrner_date_box + sh_change_date_box
                        total_change_reason_box = owrner_reason_box + sh_change_reason_box
                        total_mail_box = owrner_mail_box + sh_mail_box
                        total_name_box = owrner_name_box + sh_name_box
                        total_code_box = owrner_code_box + sh_code_box
                        total_cnt_box = cnt_box + sh_cnt
                        total_share_box = share_box + sh_share_box
                        total_category_box = category_box + sh_category_box

            else:
                print('공유지 연명부 없음')
                total_date_box = owrner_date_box
                total_change_reason_box = owrner_reason_box
                total_mail_box = owrner_mail_box
                total_name_box = owrner_name_box
                total_code_box = owrner_code_box
                total_cnt_box = cnt_box
                total_share_box = share_box
                total_category_box = category_box

            now = datetime.now()
            current_time = now.strftime('%Y-%m-%d %H:%M:%S')
            for t1, t2, t3, t4, t5, t6, t7, t8 in zip(total_date_box, total_change_reason_box, total_mail_box,
                                                      total_name_box, total_code_box, total_cnt_box, total_share_box,
                                                      total_category_box):
                df = pd.DataFrame({
                    #                 '일련번호': [num],
                    'pnu': [pnu],
                    '법정동명': [legal_dongname],
                    '지번': [total_jibun],
                    '지목': [jimok.strip()],
                    '면적': [m2],
                    '토지표시변경사유': [reason],
                    '토지표시변경일자': [reason_date],
                    "대장구분명": [san],
                    '대장발급일': [all_date],
                    '구분': [t8],
                    '등기순위번호': [t6],
                    '소유자구분': ["확인필요"],
                    "소유자명": [t4.strip().replace("\t","")],
                    "주민법인코드": [t5],
                    '소유자주소': [t3],
                    '소유권변동원인': [t2],
                    '소유권변동일자': [t1],
                    '지분': [t7],
                    '업데이트시간': [current_time]


                })
                # 탭 공백을 제거한 데이터프레임
                df = remove_tabs_from_dataframe(df)
                # 파일이 존재하는지 확인
                file_exists = os.path.isfile(file_name)
                # 파일이 존재하지 않으면 헤더 포함하여 저장, 존재하면 헤더 없이 추가
                df.to_csv(file_name, mode='a', header=not file_exists, index=False, encoding='ansi')

            print(f"■ {current_row} 수집 성공")
            minutes, seconds = get_lab_time(start_time)
            print(f"■ 소요시간 : {minutes}분 {seconds}초")
            success_cnt += 1

        except Exception as e:
            print(e)
            # total_mail = f"{do} {si} {dong} {ri} {san} {jibun} {boobun}"
            # append_to_csv(fail_file_name, f"{pnu} {total_mail}")
            # print(f'★★★ {total_mail} 실패 ★★★')

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
            print(f"★ {current_row} 실패")
            fail_cnt += 1

            ### alert 경고창이 나오면 닫아주고 안나오면 pass
            try:
                da = Alert(driver)
                da.accept()
            except:
                pass
        oracle_cursor.execute("delete from last_pnu_check")
        oracle_connection.commit()
        pnu_data = {'pnu': pnu}
        oracle_cursor.execute("""insert into last_pnu_check (pnu) values (:pnu)""", pnu_data)
        oracle_connection.commit()

        driver_close(driver)
        print(f"   ■ 성공개수 : {success_cnt}")
        print(f"   ■ 실패개수 : {fail_cnt}")
        try:
            if ip_cnt % 50 == 0:
                ip_change_click()
        except:
            print('★ 아이피 변경 실패')
        print()
    print('■■■■■■ 전체 수집 완료 ■■■■■■')

    # 커서와 연결 닫기
    oracle_cursor.close()
    oracle_connection.close()

except Exception as e:
    print(f"[apps.py] An error occurred: {e}")
