# --- [1] import (맨 위로 정리) ---
import os
import json
import time
import traceback
import re
import requests
import mysql.connector
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from urllib.parse import urlencode

# --- [2] DB 연결 (한 번만) ---
conn = mysql.connector.connect(
    host=os.environ.get("MYSQL_HOST", "127.0.0.1"),
    user=os.environ.get("MYSQL_USER", "root"),
    password=os.environ.get("MYSQL_PASSWORD", ""),
    database=os.environ.get("MYSQL_DATABASE", "real_estate"),
    charset='utf8mb4'
)
cursor = conn.cursor()

# --- [3] 테이블 생성 (한 번만) ---
cursor.execute('''
CREATE TABLE IF NOT EXISTS house (
    house_id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    price VARCHAR(255) NOT NULL,
    address VARCHAR(255) NOT NULL,
    floor VARCHAR(255) NOT NULL,
    deposit_type VARCHAR(255) NOT NULL,
    management_fee VARCHAR(255),
    availabe_from VARCHAR(255) NOT NULL,
    house_num BIGINT NOT NULL,
    agent_comm VARCHAR(255),
    agent_info VARCHAR(255) NOT NULL,
    rooms_count VARCHAR(255) NOT NULL,
    options TEXT,
    posted_at varchar(255) NOT NULL,
    gu VARCHAR(255) NOT NULL,
    dong VARCHAR(255) NOT NULL,
    img_url TEXT,
    area_size VARCHAR(255) NOT NULL,
    direction VARCHAR(255),
    built_date VARCHAR(255),
    parking varchar(255) NOT NULL,
    building_type VARCHAR(255) NOT NULL,
    house_feature TEXT,
    house_explanations TEXT,
    latitude DOUBLE,
    longitude DOUBLE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
''')

# # ====== 동 리스트 준비 ======
with open("dong_dict.json", "r", encoding="utf-8") as f:
    dong_dict = json.load(f)

cookies = {
        'NNB': '2EDYDBJPGL3WO',
        'NAC': 'VnyeDIBzyG3HB',
        'NID_AUT': 'zS4UaGslIvwS2lpPBwmL9lABh/eezkInkWX/ciUTYFDNQ7+13+zd1NjSura081G+',
        'NID_JKL': 't3aI2TNgbysosu594Kf5is2gtb30okG6MEBXY3y7Fj4=',
        '_fwb': '243CfZhJfAr6yJH5MHpimf8.1745305331108',
        'landHomeFlashUseYn': 'Y',
        '_fwb': '243CfZhJfAr6yJH5MHpimf8.1745305331108',
        '_ga': 'GA1.1.1284780960.1745558659',
        '_ga_451MFZ9CFM': 'GS1.1.1745991673.2.0.1745991674.0.0.0',
        'NFS': '2',
        'NACT': '1',
        'nhn.realestate.article.trade_type_cd': '""',
        'realestate.beta.lastclick.cortar': '4700000000',
        'nhn.realestate.article.rlet_type_cd': 'A01',
        'NID_SES': 'AAABouMCt93DujfZFnwC0sglL5Q6mqzMr3P/m1Ru9QP6gInMgHZwPX+bWzt+U3EMXjYc1HBeVHNtW2/Kwuc603d3u0hDh55SixgRUrNcbtQdaZk64ebmktMQDA9whCStdf7hzcOs6xRElebIwbEnw9LJ8qMzUGre2SCpOg8IFeWTP/yuka1ilrZqvjLIJp+jt83Pq4y8zDBLg5MIKqgUxsgzo4uuCgnhst0igVgt3TdH77ApSr/ELR5UVirFE7G8Yyq2mZL/LVEuuxoCElbV2cgaoD1F27XCVKUr2qQrKUG0QQFDRGKY5Y3o076LcmaUW+9aQ0GAi8QMBGlH5/h3MfdKSpWJNPpD9Hap40Ym6cVABiJNTHcWRmBZ5LJ5RlNX9MbHfV6JW1A31FQrdW2NwSSKZR6NAtX3L7+ad/nozKUb7Lv8R/mK/W5uQX9grpvW28j6LNhkC2d2zPCln8Usrvaor5wtMhQR9QUaOJ1hP95f4vO+53XgfQwDWE12oaU1njPdku22an+HIP0/Ytyt0PnQwSgYU4whCDcLmosv8xAW4voXgLkD0N3A1g24SIajDnC+3A==',
        'SRT30': '1747402080',
        'REALESTATE': 'Fri%20May%2016%202025%2022%3A40%3A37%20GMT%2B0900%20(Korean%20Standard%20Time)',
        'BUC': 'J8ZtC8hi6sWMagEfGwE_aCJ2rtzMZqJwFe2dpKFFWgQ=',
}
headers = {
        'accept': '*/*',
        'accept-language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
        'authorization': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6IlJFQUxFU1RBVEUiLCJpYXQiOjE3NDc0MDI4MzcsImV4cCI6MTc0NzQxMzYzN30.nEV62-Edbry937i4r_8x0YIr9hGupx5UgIsN-geJQeQ',
        'priority': 'u=1, i',
        'referer': 'https://new.land.naver.com/rooms?ms=37.4925347,127.0354309,16&a=APT:OPST:ABYG:OBYG:GM:OR:DDDGG:JWJT:SGJT:HOJT:VL&e=RETAIL&aa=SMALLSPCRENT&articleNo=2525598188',
        'sec-ch-ua': '"Chromium";v="136", "Google Chrome";v="136", "Not.A/Brand";v="99"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"macOS"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36',
        # 'cookie': 'NNB=2EDYDBJPGL3WO; NAC=VnyeDIBzyG3HB; NID_AUT=zS4UaGslIvwS2lpPBwmL9lABh/eezkInkWX/ciUTYFDNQ7+13+zd1NjSura081G+; NID_JKL=t3aI2TNgbysosu594Kf5is2gtb30okG6MEBXY3y7Fj4=; _fwb=243CfZhJfAr6yJH5MHpimf8.1745305331108; landHomeFlashUseYn=Y; _fwb=243CfZhJfAr6yJH5MHpimf8.1745305331108; _ga=GA1.1.1284780960.1745558659; _ga_451MFZ9CFM=GS1.1.1745991673.2.0.1745991674.0.0.0; NFS=2; NACT=1; nhn.realestate.article.trade_type_cd=""; realestate.beta.lastclick.cortar=4700000000; nhn.realestate.article.rlet_type_cd=A01; NID_SES=AAABouMCt93DujfZFnwC0sglL5Q6mqzMr3P/m1Ru9QP6gInMgHZwPX+bWzt+U3EMXjYc1HBeVHNtW2/Kwuc603d3u0hDh55SixgRUrNcbtQdaZk64ebmktMQDA9whCStdf7hzcOs6xRElebIwbEnw9LJ8qMzUGre2SCpOg8IFeWTP/yuka1ilrZqvjLIJp+jt83Pq4y8zDBLg5MIKqgUxsgzo4uuCgnhst0igVgt3TdH77ApSr/ELR5UVirFE7G8Yyq2mZL/LVEuuxoCElbV2cgaoD1F27XCVKUr2qQrKUG0QQFDRGKY5Y3o076LcmaUW+9aQ0GAi8QMBGlH5/h3MfdKSpWJNPpD9Hap40Ym6cVABiJNTHcWRmBZ5LJ5RlNX9MbHfV6JW1A31FQrdW2NwSSKZR6NAtX3L7+ad/nozKUb7Lv8R/mK/W5uQX9grpvW28j6LNhkC2d2zPCln8Usrvaor5wtMhQR9QUaOJ1hP95f4vO+53XgfQwDWE12oaU1njPdku22an+HIP0/Ytyt0PnQwSgYU4whCDcLmosv8xAW4voXgLkD0N3A1g24SIajDnC+3A==; SRT30=1747402080; REALESTATE=Fri%20May%2016%202025%2022%3A40%3A37%20GMT%2B0900%20(Korean%20Standard%20Time); BUC=J8ZtC8hi6sWMagEfGwE_aCJ2rtzMZqJwFe2dpKFFWgQ=',
}

    # url = 'https://new.land.naver.com/api/articles?cortarNo=1168010100&order=rank&realEstateType=APT%3AOPST%3AABYG%3AOBYG%3AGM%3AOR%3ADDDGG%3AJWJT%3ASGJT%3AHOJT%3AVL%3AYR%3ADSD%3AYR%3ADSD%3AYR%3ADSD&tradeType=&tag=%3A%3A%3A%3A%3A%3A%3ASMALLSPCRENT%3A&rentPriceMin=0&rentPriceMax=900000000&priceMin=0&priceMax=900000000&areaMin=0&areaMax=900000000&oldBuildYears&recentlyBuildYears&minHouseHoldCount&maxHouseHoldCount&showArticle=false&sameAddressGroup=false&minMaintenanceCost&maxMaintenanceCost&priceType=RETAIL&directions=&page=3&articleState'
def get_articles(cortar_no, page):
    params = {
        'realEstateType': 'APT:OPST:ABYG:OBYG:GM:OR:DDDGG:JWJT:SGJT:HOJT:VL:YR:DSD:YR:DSD:YR:DSD',
        'tradeType': '',
        'order': 'rank',
        'cortarNo': cortar_no,
        'tag': ':::::::SMALLSPCRENT:',
        'rentPriceMin': '0',
        'rentPriceMax': '900000000',
        'priceMin': '0',
        'priceMax': '900000000',
        'areaMin': '0',
        'areaMax': '900000000',
        'showArticle': 'false',
        'sameAddressGroup': 'false',
        'priceType': 'RETAIL',
        'page': str(page)
    }

    url = f"https://new.land.naver.com/api/articles?{urlencode(params)}"
    resp = requests.get(url, headers=headers, cookies=cookies)
    return resp.json().get("articleList", [])

def get_detail(article_no):
    url = f"https://new.land.naver.com/api/articles/{article_no}"
    resp = requests.get(url, headers=headers, cookies=cookies)
    return resp.json()


options = webdriver.ChromeOptions()
options.add_argument("--start-maximized")
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)


wait = WebDriverWait(driver, 10)

# ====== 네이버 부동산 접속 후 준비 ======
driver.get("https://new.land.naver.com/complexes")

time.sleep(2)

# 원룸/투룸 버튼 클릭
wait.until(EC.element_to_be_clickable((By.XPATH, '/html/body/div[2]/div/div[1]/a[3]'))).click()
time.sleep(1)

# ====== 구, 동별로 돌면서 매물 크롤링 ======
target_gu_list = ["강남구"]
# target_gu_list = ["강남구", "강동구", "강북구", "강서구", "관악구"]  # 경은
# target_gu_list = ["광진구", "구로구", "금천구", "노원구", "도봉구"]  # 지혜
# target_gu_list = ["동대문구", "동작구", "마포구", "서대문구", "서초구"]  # 선유
# target_gu_list = ["성동구", "성북구", "송파구", "양천구", "영등포구"]  # 정원
# target_gu_list = ["용산구", "은평구", "종로구", "중구", "중랑구"]  # 성주
# target_gu_list = ['강북구']  # test용

for target_gu in target_gu_list:
    dong_list = dong_dict.get(target_gu, [])

    for dong_code, dong_name in dong_list:
        try:
            print(f"▶️ {dong_name} 매물 시작")

            titles, prices, addresses = [], [], []
            floors, d_types, m_fees = [], [], []
            a_froms, nums, agent_comms = [], [], []
            rooms_cnts, options_list, agent_infos = [], [], []
            gus, dongs = [], []
            posted_ats = []
            img_urls = []
            areas, directions, approval_dates, parkings, b_types, features, explanations = [], [], [], [], [], [], []
            latitudes, longitudes = [], []  # 추가

            # 지역 선택 재진입
            wait.until(EC.element_to_be_clickable((By.XPATH, '/html/body/div[2]/div/section/div[2]/div[2]/div[1]/div/div/a/span[1]'))).click()
            time.sleep(1)
            wait.until(EC.element_to_be_clickable((By.XPATH, '//label[contains(text(), "서울")]'))).click()
            time.sleep(0.5)
            wait.until(EC.element_to_be_clickable((By.XPATH, f'//label[contains(text(), "{target_gu}")]'))).click()
            time.sleep(0.5)

            dong_xpath = f'//label[contains(text(), "{dong_name}")]'
            try:
                dong_element = wait.until(EC.presence_of_element_located((By.XPATH, dong_xpath)))
                driver.execute_script("arguments[0].scrollIntoView(true);", dong_element)
                time.sleep(0.5)
                dong_element.click()
                print(f"✅ {dong_name} 클릭 완료")
                time.sleep(2)
            except:
                print(f"❌ {dong_name} 클릭 실패")
                continue

            try:
                last_height = driver.execute_script("return document.body.scrollHeight")
                while True:
                    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                    time.sleep(1.5)
                    new_height = driver.execute_script("return document.body.scrollHeight")
                    if new_height == last_height:
                        break
                    last_height = new_height
            except Exception as e:
                print(f"❗ 스크롤 로딩 중 오류 발생: {e}")
                continue

            for idx in range(300):
                try:
                    listing_elements = driver.find_elements(By.CSS_SELECTOR, "div.item_inner")
                    if idx >= len(listing_elements):
                        print(f"✅ {dong_name} 매물 모두 크롤링 완료")
                        break

                    listing_element = listing_elements[idx]
                    print(f"[{dong_name}] {idx+1}번째 매물 크롤링")

                    try:
                        naver_btn = listing_element.find_element(By.XPATH, './/a[contains(@class, "label--cp")]')
                        if naver_btn.is_displayed():
                            driver.execute_script("arguments[0].scrollIntoView(true);", naver_btn)
                            WebDriverWait(driver, 3).until(EC.element_to_be_clickable(naver_btn)).click()
                        else:
                            raise Exception("버튼 숨김")
                    except:
                        driver.execute_script("arguments[0].scrollIntoView(true);", listing_element)
                        WebDriverWait(driver, 3).until(EC.element_to_be_clickable(listing_element)).click()

                    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.detail_contents")))

                    def text_not_empty(driver):
                        try:
                            elem = driver.find_element(By.CSS_SELECTOR, "div.info_title_wrap")
                            return elem.text.strip() if elem.text.strip() else False
                        except:
                            return False

                    title = WebDriverWait(driver, 10).until(text_not_empty)
                    titles.append(title)

                    try: price = driver.find_element(By.CSS_SELECTOR, "div.info_article_price").text.strip()
                    except: price = "가격 정보 없음"
                    prices.append(price)

                    try: address = driver.find_element(By.XPATH, '//th[contains(text(), "소재지")]/following-sibling::td').text.strip()
                    except: address = "주소 정보 없음"
                    addresses.append(address)

                    gus.append(target_gu)
                    dongs.append(dong_name)

                    try: floor = driver.find_element(By.XPATH, '//th[contains(text(), "해당층")]/following-sibling::td[1]').text.strip()
                    except: floor = "층수 정보 없음"
                    floors.append(floor)

                    try: d_type = driver.find_element(By.CSS_SELECTOR, "div.info_article_price .type").text.strip()
                    except: d_type = "구분 정보 없음"
                    d_types.append(d_type)

                    try: area = driver.find_element(By.XPATH, '//th[contains(text(), "전용면적")]/following-sibling::td').text.strip()
                    except: area = "전용면적 정보 없음"
                    areas.append(area)

                    try: feature = driver.find_element(By.XPATH, '//th[contains(text(), "매물특징")]/following-sibling::td').text.strip()
                    except: feature = "매물 특징 없음"
                    features.append(feature)

                    try: explanation = driver.find_element(By.XPATH, '//th[contains(text(), "매물설명")]/following-sibling::td').text.strip()
                    except: explanation = "매물 설명 없음"
                    explanations.append(explanation)

                    try:
                        b_type = driver.find_element(By.XPATH, '//th[contains(text(), "건축물 용도")]/following-sibling::td').text.strip()
                    except: b_type = "건축물 용도 정보 없음"
                    b_types.append(b_type)

                    try: direction = driver.find_element(By.XPATH, '//th[contains(text(), "방향")]/following-sibling::td').text.strip()
                    except: direction = "방향 정보 없음"
                    directions.append(direction)

                    try: approval_date = driver.find_element(By.XPATH, '//th[contains(text(), "사용승인일")]/following-sibling::td').text.strip()
                    except: approval_date = "사용승인일 정보 없음"
                    approval_dates.append(approval_date)

                    try: parking_available = driver.find_element(By.XPATH, '//th[contains(text(), "주차가능여부")]/following-sibling::td').text.strip()
                    except:
                        try:
                            parking_count = driver.find_element(By.XPATH, '//th[contains(text(), "총주차대수")]/following-sibling::td').text.strip()
                            parking_available = "가능" if parking_count else "불가능"
                        except:
                            parking_available = "불가능"
                    parkings.append(parking_available)

                    try:
                        m_fee_elem = driver.find_element(By.XPATH, '//th[contains(text(), "관리비")]/following-sibling::td')
                        m_fee_raw = m_fee_elem.text.strip().replace("상세보기", "").strip()

                        # 오직 숫자+단위 패턴만 유효값으로 인정
                        if re.fullmatch(r"\d+(,\d+)?(만원|원)", m_fee_raw):
                            m_fee = m_fee_raw
                        else:
                            m_fee = "관리비 정보 없음"
                    except:
                        m_fee = "관리비 정보 없음"
                    m_fees.append(m_fee)

                    try: a_from = driver.find_element(By.XPATH, '//th[contains(text(), "입주가능일")]/following-sibling::td').text.strip()
                    except: a_from = "입주가능일 정보 없음"
                    a_froms.append(a_from)

                    try: num = driver.find_element(By.XPATH, '//th[contains(text(), "매물번호")]/following-sibling::td').text.strip()
                    except: num = "매물번호 정보 없음"
                    nums.append(num)

                    try:
                        detail = get_detail(num)
                        lat = detail.get("articleAddition", {}).get("latitude", "")
                        lon = detail.get("articleAddition", {}).get("longitude", "")
                    except:
                        lat, lon = "", ""
                    latitudes.append(lat)
                    longitudes.append(lon)

                    try:
                        agent_info = driver.find_element(By.CSS_SELECTOR, "div.info_agent_title strong.info_title").text.strip()
                    except: agent_info = "중개사 정보 없음"
                    agent_infos.append(agent_info)

                    try: agent_comm = driver.find_element(By.CSS_SELECTOR, "strong.point5").text.strip()
                    except: agent_comm = "중개료 정보 없음"
                    agent_comms.append(agent_comm)

                    try: rooms_cnt = driver.find_element(By.XPATH, '//th[contains(text(), "방수")]/following-sibling::td').text.strip()
                    except: rooms_cnt = "방 개수 정보 없음"
                    rooms_cnts.append(rooms_cnt)

                    try:
                        notice_text = driver.find_element(By.CSS_SELECTOR, "p.info_notice").text
                        date_match = re.search(r"\d{4}\.\d{2}\.\d{2}", notice_text)
                        if date_match:
                            posted_date = date_match.group()
                        else:
                            posted_date = "날짜 없음"
                    except Exception as e:
                        print(f"게재일 추출 실패: {e}")
                    posted_ats.append(posted_date)

                    try:
                        option_elements = driver.find_elements(By.CSS_SELECTOR, "div.option_item_text")
                        options_temp = [elem.text.strip() for elem in option_elements if elem.text.strip()]
                        options_str = ", ".join(options_temp) if options_temp else "옵션 정보 없음"
                    except:
                        options_str = "옵션 정보 없음"

                    options_list.append(options_str)


                    img_temp = []
                    try:
                        tab_buttons = driver.find_elements(By.CSS_SELECTOR, "button.tab_item")
                        for btn in tab_buttons:
                            try:
                                span = btn.find_element(By.TAG_NAME, "span")
                                if "사진" in span.text:
                                    btn.click()
                                    time.sleep(2)
                                    break
                            except:
                                continue
                        photo_elements = driver.find_elements(By.CSS_SELECTOR, "div.detail_photo_wrap a.detail_photo_item")
                        for elem in photo_elements:
                            style = elem.get_attribute("style")
                            if "background-image" in style:
                                start = style.find('url("') + len('url("')
                                end = style.find('")')
                                url = style[start:end]
                                img_temp.append(url)
                    except:
                        pass
                    img_urls.append(img_temp)

                    try:
                        close_btn = WebDriverWait(driver, 3).until(
                            EC.presence_of_element_located((By.XPATH, "/html/body/div[2]/div/section/div[2]/div[2]/div/button"))
                        )
                        close_btn.click()
                        time.sleep(1)
                    except:
                        print("❗ 닫기 버튼 없음")

                except Exception as e:
                    print(f"[{dong_name}] {idx+1}번째 매물 크롤링 실패")
                    traceback.print_exc()
                    continue

            # INSERT 쿼리
            for row in zip(
                titles, prices, addresses, floors, d_types, m_fees, a_froms,
                nums, agent_comms, agent_infos, rooms_cnts, options_list,
                posted_ats, gus, dongs, img_urls,
                areas, directions, approval_dates, parkings, b_types, features, explanations, latitudes, longitudes
            ):
                cursor.execute('''
                    INSERT INTO house (
                        title, price, address, floor, deposit_type, management_fee,
                        availabe_from, house_num, agent_comm, agent_info, rooms_count, options,
                        posted_at, gu, dong, img_url,
                        area_size, direction, built_date, parking, building_type, house_feature, house_explanations,
                        latitude, longitude
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ''', (
                    row[0], row[1], row[2], row[3], row[4], row[5],
                    row[6], row[7], row[8], row[9], row[10], row[11],
                    row[12], row[13], row[14], json.dumps(row[15], ensure_ascii=False) if isinstance(row[15], list) else row[15],
                    row[16], row[17], row[18], row[19], row[20], row[21], row[22], row[23], row[24]
                ))

            print(f"💾 {dong_name} DB 저장 완료")


        except Exception as e:
            print(f"❌ {dong_name} 처리 실패")
            traceback.print_exc()
            continue

conn.commit()
conn.close()
driver.quit()
print("✅ 전체 작업 완료 및 종료")