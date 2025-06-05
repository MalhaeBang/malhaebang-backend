import os
import re
import json
import time
import requests
import pandas as pd
from elasticsearch import Elasticsearch
from openai import OpenAI
from dotenv import load_dotenv

# 0. Load environment variables
load_dotenv()

# 1. Elasticsearch setup
ES_HOST = "http://localhost:9200"
ES_ID = "elastic"
ES_PW = "elasticteam3"

es = Elasticsearch(
    ES_HOST,
    basic_auth=(ES_ID, ES_PW),
    verify_certs=False
)

# 2. OpenAI setup
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=OPENAI_API_KEY)

# 3. TMap API key
TMAP_API_KEY = os.getenv("TMAP_API_KEY")

# 4. Load subway station coordinates
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
station_csv_path = os.path.join(BASE_DIR, "서울지하철_노선정보_평균좌표_정제.csv")
df_station = pd.read_csv(station_csv_path)
station_coords = {
    row["역사명"].replace(" ", "").strip(): (row["위도"], row["경도"])
    for _, row in df_station.iterrows()
}

# 5. Extract conditions using OpenAI
def extract_conditions_with_openai(query):
    prompt = f"""
다음 부동산 검색 질의를 단순 JSON 구조로 변환하세요.
조건 형식:
- 위치: 행정동 이름 또는 역 이름 (예: "노량진동", "강남역")
- 거래유형: "전세" 또는 "월세"
- 보증금_최대: 문자열 (예: "2억")
- 월세_최대: 문자열 (예: "80만원")
- 평수_최소: 숫자 또는 null
- 의미조건: ["역세권", "냉장고", ...] 형태로 추출
사용자 질의: "{query}"
""".strip()
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3
    )
    text = response.choices[0].message.content
    match = re.search(r"\{[\s\S]*?\}", text)
    if match:
        try:
            return json.loads(match.group())
        except:
            return {}
    return {}

# 6. Distance calculation via TMap API
def get_tmap_walking_distance(start_lat, start_lon, end_lat, end_lon, app_key):
    url = "https://apis.openapi.sk.com/tmap/routes/pedestrian?version=1"
    headers = {
        "Content-Type": "application/json",
        "appKey": app_key
    }
    body = {
        "startX": str(start_lon),
        "startY": str(start_lat),
        "endX": str(end_lon),
        "endY": str(end_lat),
        "reqCoordType": "WGS84GEO",
        "resCoordType": "WGS84GEO",
        "startName": "출발지",
        "endName": "도착지"
    }
    try:
        res = requests.post(url, json=body, headers=headers)
        data = res.json()
        if "features" in data:
            distance = data["features"][0]["properties"]["totalDistance"]
            duration = data["features"][0]["properties"]["totalTime"]
            return distance / 1000, duration / 60
    except:
        pass
    return None, None

# 7. Utility functions
def parse_price(val):
    if not val: return None
    val = val.replace(" ", "").replace(",", "")
    if "억" in val:
        return int(float(val.replace("억", "")) * 100_000_000)
    elif "만원" in val:
        return int(float(val.replace("만원", "")) * 10_000)
    return int(val)

def format_price(val):
    if val >= 100_000_000:
        return f"{val // 100_000_000}억 {((val % 100_000_000) // 10_000):,}만원"
    elif val >= 10_000:
        return f"{val // 10_000:,}만원"
    return f"{val:,}원"

def render_safety_emoji(grade):
    mapping = {
        "짱안전": "🟢😄 짱안전",
        "안전": "🟢🙂 안전",
        "보통": "🟡😐 보통",
        "주의": "🔴⚠️ 주의"
    }
    return mapping.get(grade.strip(), f"⚪️❓ {grade}" if grade else "❌ 정보 없음")

def parse_location(loc):
    if not loc: return None, None, None
    loc = loc.strip()
    if loc.endswith("역") and loc.replace("역", "") in station_coords:
        station = loc.replace("역", "")
        return "station", station, station_coords[station]
    elif loc.endswith("동"):
        return "dong", loc, None
    else:
        return "dong", loc + "동", None

# 8. Main execution
def main():
    while True:
        query = input("\n📥 사용자 쿼리를 입력하세요 (종료하려면 'exit'): ")
        if query.lower().strip() in ["exit", "quit"]:
            print("👋 검색을 종료합니다.")
            break

        cond = extract_conditions_with_openai(query)
        location_type, location_text, location_coords = parse_location(cond.get("위치"))

        filter_conditions = []
        if cond.get("거래유형"):
            filter_conditions.append({"term": {"deposit_type": cond["거래유형"]}})
        if cond.get("보증금_최대"):
            p = parse_price(cond["보증금_최대"])
            if p: filter_conditions.append({"range": {"deposit": {"lte": p}}})
        if cond.get("월세_최대"):
            p = parse_price(cond["월세_최대"])
            if p: filter_conditions.append({"range": {"monthly_rent": {"lte": p}}})

        semantic_keywords = list(set([kw.strip().lower() for kw in cond.get("의미조건", [])]))
        should_conditions = []
        for kw in semantic_keywords:
            should_conditions.extend([
                {"match": {"gpt_description": kw}},
                {"match": {"house_feature": kw}},
                {"match": {"house_explanations": kw}},
                {"match": {"options": kw}},
            ])

        base_query = {"bool": {"filter": filter_conditions, "should": should_conditions, "minimum_should_match": 1}}
        if location_type == "station":
            geo_query = {
                "query": {
                    "bool": {
                        "must": [base_query, {
                            "geo_distance": {
                                "distance": "1.5km",
                                "location": {
                                    "lat": location_coords[0],
                                    "lon": location_coords[1]
                                }
                            }
                        }]
                    }
                },
                "size": 5
            }
        else:
            base_query["bool"]["must"] = [{"wildcard": {"dong": location_text + "*"}}]
            geo_query = {"query": base_query, "size": 5}

        res = es.search(index="real_estate_location", body=geo_query)
        for i, hit in enumerate(res["hits"]["hits"], 1):
            src = hit["_source"]
            print(f"\n🟩 [Top-{i}] Score: {hit['_score']:.2f}")
            print(f"📍 {src.get('gu', '')} {src.get('dong', '')}")
            print(f"💰 {src.get('deposit_type', '')} {format_price(src.get('deposit', 0))} / {format_price(src.get('monthly_rent', 0))}")
            print(f"📏 {src.get('space', '?')}평 | 🏙️ {src.get('floor', '?')}/{src.get('total_floor', '?')}층")
            print(f"🛏️ 방: {src.get('rooms_count', '?')} / 욕실: {src.get('bath_count', '?')}")
            print(f"🅿️ 주차: {'가능' if src.get('parking', 0) else '불가'}")
            print(f"🔒 안전등급: {render_safety_emoji(src.get('safety_grade', ''))}")
            print(f"📫 주소: {src.get('address', '정보 없음')}")

            combined_text = " ".join([
                str(src.get("gpt_description", "")).lower(),
                str(src.get("house_feature", "")).lower(),
                str(src.get("house_explanations", "")).lower(),
                str(src.get("options", "")).lower()
            ])
            matched = [kw for kw in semantic_keywords if kw in combined_text]
            print(f"💡 일치한 조건: {matched if matched else '없음'}")

            if location_type == "station" and "location" in src:
                hlat, hlon = src["location"]["lat"], src["location"]["lon"]
                dist_km, dur_min = get_tmap_walking_distance(location_coords[0], location_coords[1], hlat, hlon, TMAP_API_KEY)
                if dist_km:
                    print(f"🚶 도보 거리: {dist_km:.2f}km / 약 {round(dur_min)}분 소요")
                else:
                    print("🚫 도보 거리 정보 없음")

if __name__ == "__main__":
    main()
