from moduls import *


### IP 선택 함수
# def ip_checked():
#     ip_file = open("ip.txt", "r", encoding="utf-8")
#     ip_list = ip_file.readlines()
#     ip_list_box = []
#     for i in ip_list:
#         ip_list_box.append(str(i).replace('\n', ""))
#     return random.choice(ip_list_box)


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


def read_agents():
    agents = []
    f = open("./useragents.txt", "r", encoding="utf8")
    while True:
        line = f.readline()
        if not line:
            break
        agents.append(line.rstrip())
    return agents


def make_driver():
    UA_list = read_agents()
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
