
from moduls import *

useragent_list = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.135 Safari/537.36 Edge/12.246',
    'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.111 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.84 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.75 Safari/537.36 Edg/99.0.1150.36',
    'Mozilla/5.0 (Windows NT 10.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.75 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:99.0) Gecko/20100101 Firefox/99.0',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:105.0) Gecko/20100101 Firefox/105.0',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36 Edg/106.0.1370.34',

]

def make_user_agent(ua, is_mobile):
    user_agent = parse(ua)
    model = user_agent.device.model
    platform = user_agent.os.family
    platform_version = user_agent.os.version_string + ".0.0"
    version = user_agent.browser.version[0]
    ua_full_version = user_agent.browser.version_string
    architecture = "x86"
    print(platform)
    if is_mobile:
        platform_info = "Linux armv8l"
        architecture = ""
    else:  # Window
        platform_info = "Win32"
        model = ""
    RET_USER_AGENT = {
        "appVersion": ua.replace("Mozilla/", ""),
        "userAgent": ua,
        "platform": f"{platform_info}",
        "acceptLanguage": "ko-KR, kr, en-US, en",
        "userAgentMetadata": {
            "brands": [
                {"brand": " Not A;Brand", "version": "99"},
                {"brand": "Google Chrome", "version": f"{version}"},
                {"brand": "Chromium", "version": f"{version}"}
            ],
            "fullVersion": f"{ua_full_version}",
            "platform": platform,
            "platformVersion": platform_version,
            "architecture": architecture,
            "model": model,
            "mobile": is_mobile  # True, False
        }
    }
    return RET_USER_AGENT


def read_agents(useragent_list):
    return useragent_list


def make_driver():
    UA_list = read_agents(useragent_list)
    UA = random.choice(UA_list)  # seed = time.time()

    options = uc.ChromeOptions()

    # IP 변경
    # ip = ip_checked()
    # print(ip)
    # PROXY = str(ip)
    # options.add_argument(f'--proxy-server={PROXY}')

    # User Agent 속이기
    options.add_argument(f'--user-agent={UA}')
    # options.add_argument("--start-fullscreen")  # pc용 사이즈
    options.add_argument("--no-first-run --no-service-autorun --password-store=basic")
    options.add_argument('--disable-logging')
    # origin 허용(동적데이터 불러오기)
    options.add_argument("--disable-web-security")
    options.add_argument("--disable-site-isolation-trials")
    options.headless = False

    chrome_ver = chromedriver_autoinstaller.get_chrome_version().split('.')[0]
    print(chrome_ver)
    print(selenium.__version__)
    print(uc.__version__)

    driver = uc.Chrome(options=options)
    driver.maximize_window()
    driver.implicitly_wait(20)
    wait = WebDriverWait(driver, 60)

    UA_Data = make_user_agent(UA, False)
    driver.execute_cdp_cmd("Network.setUserAgentOverride", UA_Data)
    driver.execute_cdp_cmd("Emulation.setUserAgentOverride", UA_Data)

    return driver, wait


### 셀레니움 스타터 세팅
def starter():
    # user_agent세팅 (사용자가 직접 제어 하는것처럼 하기 위해 세팅)
    UA_list = read_agents()
    UA = random.choice(UA_list)  # seed = time.time()
    option = Options()
    option.add_argument('user-agent=' + UA)
    option.add_argument("--no-first-run --no-service-autorun --password-store=basic")
    option.add_argument('--disable-logging')
    # origin 허용(동적데이터 불러오기)
    option.add_argument("--disable-web-security")
    option.add_argument("--disable-site-isolation-trials")
    option.headless = False
    option.add_argument('window-size=1920x1080')
    option.add_argument('lang=ko_KR')
    option.add_experimental_option("detach", False)
    option.add_argument("disable-blink-features=AutomationControlled")  # 자동화 탐지 방지
    option.add_experimental_option("excludeSwitches", ["enable-automation"])  # 자동화 표시 제거
    option.add_experimental_option('useAutomationExtension', False)  # 자동화 확장 기능 사용 안 함

    driver = webdriver.Chrome(options=option)
    driver.maximize_window()
    driver.implicitly_wait(20)
    wait = WebDriverWait(driver, 60)
    UA_Data = make_user_agent(UA, False)
    driver.execute_cdp_cmd("Network.setUserAgentOverride", UA_Data)
    driver.execute_cdp_cmd("Emulation.setUserAgentOverride", UA_Data)
    return driver, wait