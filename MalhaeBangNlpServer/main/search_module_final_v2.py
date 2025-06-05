import os
import re
import json
import requests
import pandas as pd
import time
from elasticsearch import Elasticsearch
from openai import OpenAI
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer
import urllib.parse


def timeit(func):
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        print(f"⏱️ {func.__name__} 실행 시간: {end - start:.2f}초")
        return result
    return wrapper

# 환경 변수 로드
load_dotenv()

ES_HOST = os.getenv("ES_HOST", "elasticsearch")
ES_ID = os.getenv("ES_ID", "elastic")
ES_PW = os.getenv("ES_PW", "elasticteam3")
ES_INDEX = os.getenv("ES_INDEX") or "cleaned_house"
TMAP_API_KEY = os.getenv("TMAP_API_KEY")

es = Elasticsearch([f"http://{ES_HOST}:9200"], basic_auth=(ES_ID, ES_PW), verify_certs=False)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=OPENAI_API_KEY)
embed_model = SentenceTransformer("intfloat/e5-base")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
station_csv_path = os.path.join(BASE_DIR, "서울지하철_노선정보_평균좌표_정제.csv")
df_station = pd.read_csv(station_csv_path)
station_coords = {
    row["역사명"].replace(" ", "").strip(): (row["위도"], row["경도"])
    for _, row in df_station.iterrows()
}

ALL_GU_NAMES = [gu.replace("구", "") for gu in [
    "강남구", "강동구", "강북구", "강서구", "관악구", "광진구", "구로구", "금천구", "노원구", "도봉구",
    "동대문구", "동작구", "마포구", "서대문구", "서초구", "성동구", "성북구", "송파구", "양천구", "영등포구",
    "용산구", "은평구", "종로구", "중구", "중랑구"
]]

SAME_NAME_GU_DONG = {
    "구로": {"gu": "구로구", "dong": "구로동"},
    "도봉": {"gu": "도봉구", "dong": "도봉동"},
    "마포": {"gu": "마포구", "dong": "마포동"},
    "서초": {"gu": "서초구", "dong": "서초동"},
    "성북": {"gu": "성북구", "dong": "성북동"},
    "송파": {"gu": "송파구", "dong": "송파동"},
    "영등포": {"gu": "영등포구", "dong": "영등포동"}
}

def extract_conditions_with_openai(query):
    prompt = f"""
    사용자가 입력한 부동산 질의에 오타가 있더라도 의미를 추정하여 정확한 위치, 조건을 분석하세요.
    예를 들어 '수우역'은 '수유역'으로, '10븐'은 '10분'으로 판단합니다.

    다음 부동산 검색 질의를 아래 JSON 형식으로 변환하세요.

    출력 형식 예:
    {{
    "위치": "강남역",
    "거래유형": "월세",
    "보증금_최소": "1억",
    "보증금_최대": "3억",
    "월세_최소": "50만원",
    "월세_최대": "80만원",
    "평수_최소": 10,
    "평수_최대": 20,
    "의미조건": ["역세권", "냉장고"],
    "제외위치": ["상암동"],
    "제외의미조건": ["위험", "주의"]
    }}

    💡 주의:
    - 단순히 '지명'이나 '역 이름'만 언급된 경우에도, 사용자가 기본적으로 매물 추천을 원하는 것으로 간주합니다.
    - 질의에 등장하는 명사/형용사/의미 단어(예: '현관보안', '반려동물', '냉장고')는 의미조건 배열로 추출하세요.
    - 거리조건은 의미조건으로 분류하지 마세요.
    - 제외 조건은 반드시 '제외위치' 또는 '제외의미조건' 배열에 따로 기록하세요.
    - 단순 감탄, 잡담성 문장(예: '난 용산역이 좋아 ~')은 추천 요청으로 오해하지 말고 '기타'로 분류합니다.

    🔧 추가 규칙:
    - 사용자가 "보증금 1억", "월세 50만원"이라고 말하면 → "보증금_최소": "1억", "보증금_최대": "1억", "월세_최소": "50만원", "월세_최대": "50만원"
    - 사용자가 "보증금 1억~3억", "보증금 1억에서 3억"이라고 말하면 → "보증금_최소": "1억", "보증금_최대": "3억"
    - 사용자가 "보증금 1억 이상"이라고 말하면 → "보증금_최소": "1억"
    - 사용자가 "보증금 3억 이하"라고 말하면 → "보증금_최대": "3억"
    - 월세와 평수도 동일한 방식으로 최소/최대 범위를 추출하세요.
    - 단일 값만 언급된 경우에도 '최소' 또는 '최대'로 구분해 기록하세요.

    출력은 반드시 JSON 형식만 포함해야 하며, 불필요한 설명, 주석, 말머리 등을 붙이지 마세요.

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
            cond = json.loads(match.group())
            return cond
        except Exception as e:
            print(f"❗ JSON 파싱 에러: {e}")
            return {}
    print("❗ JSON 구조 인식 실패")
    return {}

def geocode_text_location(query_text):
    # 예시: 카카오 API 사용 (headers에 Kakao REST API 키 필요)
    kakao_key = os.getenv("KAKAO_API_KEY")
    if not kakao_key:
        print("❌ KAKAO_API_KEY 환경변수 없음")
        return None, None

    url = f"https://dapi.kakao.com/v2/local/search/keyword.json?query={urllib.parse.quote(query_text)}"
    headers = {"Authorization": f"KakaoAK {kakao_key}"}
    try:
        res = requests.get(url, headers=headers)
        res.raise_for_status()
        documents = res.json().get("documents", [])
        if documents:
            lat = float(documents[0]["y"])
            lon = float(documents[0]["x"])
            print(f"📍 '{query_text}' → 위경도 변환 성공: ({lat}, {lon})")
            return lat, lon
    except Exception as e:
        print(f"❌ Geocoding API 에러: {e}")
    return None, None

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
            duration = data["features"][0]["properties"]["totalTime"] / 60
            return distance, duration
    except Exception as e:
        print(f"❗ TMap API 에러: {e}")
    return None, None

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
    if not grade:
        return None  # 출력 안 함
    mapping = {
        "매우안전": "🟢 매우안전",
        "안전": "🔵 안전",
        "보통": "🟡 보통",
        "주의": "🟠 주의",
        "위험": "🔴 위험"
    }
    return mapping.get(grade.strip(), f"⚪️❓ {grade}")

def resolve_location_ambiguity(loc):
    base = loc.replace("구", "").replace("동", "")
    if base in SAME_NAME_GU_DONG:
        print(f"⚠️ '{base}'는 '{SAME_NAME_GU_DONG[base]['gu']}'와 '{SAME_NAME_GU_DONG[base]['dong']}' 중 어디를 뜻합니까?")
        choice = input("구 or 동 입력: ").strip()
        if choice == "동":
            return "dong", SAME_NAME_GU_DONG[base]['dong'], None
        else:
            return "gu", SAME_NAME_GU_DONG[base]['gu'], None
    return None, None, None

def parse_walking_time_to_meter(query, default_meter=1500):
    m = re.search(r"도보\s*(\d+)\s*분", query)
    if m:
        minute = int(m.group(1))
        return int(minute * 67)
    return default_meter

def resolve_location_ambiguity(loc):
    if loc in SAME_NAME_GU_DONG:
        print(f"⚠️ '{loc}'는 '{SAME_NAME_GU_DONG[loc]['gu']}'와 '{SAME_NAME_GU_DONG[loc]['dong']}' 중 어디를 뜻합니까?")
        choice = input("구 or 동 입력: ").strip()
        if choice == "동":
            return "dong", SAME_NAME_GU_DONG[loc]['dong'], None
        else:
            return "gu", SAME_NAME_GU_DONG[loc]['gu'], None
    return None, None, None

def parse_location(loc):
    if not loc:
        return None, None, None

    loc = loc.strip().replace(" ", "")

    # ambiguity 먼저 처리 (원본 문자열로)
    loc_type, resolved, _ = resolve_location_ambiguity(loc)
    if loc_type:
        return loc_type, resolved, None

    # 이후 일반 처리
    if loc.endswith("역") and loc.replace("역", "") in station_coords:
        station = loc.replace("역", "")
        return "station", station, station_coords[station]
    if loc.endswith("구"):
        return "gu", loc, None
    if loc.endswith("동"):
        return "dong", loc, None
    if loc in ALL_GU_NAMES:
        return "gu", loc + "구", None
    elif loc in station_coords:
        return "station", loc, station_coords[loc]
    else:
        return "dong", loc + "동", None

 
def handle_query(query):
    cond = extract_conditions_with_openai(query)
    # 의도 보정: 부동산 관련 키워드가 있으면 무조건 매물 추천
    intent = cond.get("intent", "")
    if intent in ["기타", "일상 대화"] and any(kw in query for kw in ["추천", "매물", "집", "방", "전세", "월세", "구해줘", "찾아줘"]):
        cond["intent"] = "매물 추천"
    #print("🛠️ OpenAI 파싱된 JSON:")
    #print(json.dumps(cond, ensure_ascii=False, indent=2))
    semantic_keywords = cond.get("의미조건", [])

    filter_conditions = []

    # ✅ 거래유형 필터
    if cond.get("거래유형"):
        filter_conditions.append({"term": {"deposit_type": cond["거래유형"]}})

    # ✅ 보증금 처리
    if (cond.get("보증금_최소") and cond.get("보증금_최대") and 
        parse_price(cond["보증금_최소"]) == parse_price(cond["보증금_최대"])):
        exact_deposit = parse_price(cond["보증금_최소"])
        filter_conditions.append({"term": {"deposit": exact_deposit}})
    else:
        deposit_range = {}
        if cond.get("보증금_최소"):
            deposit_range["gte"] = parse_price(cond["보증금_최소"])
        if cond.get("보증금_최대"):
            deposit_range["lte"] = parse_price(cond["보증금_최대"])
        if deposit_range:
            filter_conditions.append({"range": {"deposit": deposit_range}})

    # ✅ 월세 처리
    if (cond.get("월세_최소") and cond.get("월세_최대") and 
        parse_price(cond["월세_최소"]) == parse_price(cond["월세_최대"])):
        exact_monthly = parse_price(cond["월세_최소"])
        filter_conditions.append({"term": {"monthly_rent": exact_monthly}})
    else:
        monthly_range = {}
        if cond.get("월세_최소"):
            monthly_range["gte"] = parse_price(cond["월세_최소"])
        if cond.get("월세_최대"):
            monthly_range["lte"] = parse_price(cond["월세_최대"])
        if monthly_range:
            filter_conditions.append({"range": {"monthly_rent": monthly_range}})

    # ✅ 평수 처리
    if (cond.get("평수_최소") and cond.get("평수_최대") and 
        float(cond["평수_최소"]) == float(cond["평수_최대"])):
        exact_space = float(cond["평수_최소"])
        filter_conditions.append({"term": {"space": exact_space}})
    else:
        space_range = {}
        if cond.get("평수_최소"):
            space_range["gte"] = float(cond["평수_최소"])
        if cond.get("평수_최대"):
            space_range["lte"] = float(cond["평수_최대"])
        if space_range:
            filter_conditions.append({"range": {"space": space_range}})


    # ✅ 의미조건에서 '주차' 필터
    semantic_keywords = cond.get("의미조건", [])

    # 항상 초기화
    user_vec = None
    if '주차' in semantic_keywords or '주차가능' in semantic_keywords:
        filter_conditions.append({"term": {"parking": 1}})

    # ✅ 제외조건
    must_not_conditions = []
    for ex_loc in cond.get("제외위치", []):
        must_not_conditions.append({"term": {"dong": ex_loc}})
    for ex_meaning in cond.get("제외의미조건", []):
        must_not_conditions.append({"match": {"gpt_description": ex_meaning}})

    # ✅ 위치 필터
    loc_type, loc_name, coords = parse_location(cond.get("위치"))
    walking_meter = parse_walking_time_to_meter(query, default_meter=1000)
    is_station_query = loc_type == "station" and coords

    if is_station_query and "역" not in query:
        is_station_query = False

    if is_station_query:
        es_distance = int(max(walking_meter * 2, 1000))
        filter_conditions.append({
            "geo_distance": {
                "distance": f"{es_distance}m",
                "location": {"lat": coords[0], "lon": coords[1]}
            }
        })
    elif loc_type == "dong" and loc_name and coords:
        base = loc_name.replace("동", "").replace("가", "")
        filter_conditions.append({
            "bool": {
                "should": [
                    {"term": {"dong.keyword": loc_name}},
                    {"regexp": {"dong": f".*{base}.*"}}
                ]
            }
        })
    elif loc_type == "gu" and loc_name:
        filter_conditions.append({"term": {"gu": loc_name}})

    elif cond.get("위치"):
        unknown_loc = cond["위치"]
        #print(f"⚠️ '{unknown_loc}'의 위치 해석 실패 → 외부 Geocoding API 시도")

        lat, lon = geocode_text_location(unknown_loc)
        if lat and lon:
            coords = (lat, lon)
            is_station_query = False
            es_distance = int(max(walking_meter * 1.5, 1000))
            filter_conditions.append({
                "geo_distance": {
                    "distance": f"{es_distance}m",
                    "location": {"lat": lat, "lon": lon}
                }
            })
        else:
            print("❌ Geocoding 실패: 위치 조건 무시")

    else:
        print("⚠️ 위치 정보 없음: 지역 필터링 없이 검색합니다.")
        # ✅ should 클라우스 구성
    should_clauses = []
    for kw in semantic_keywords:
        if kw not in ['주차', '주차가능']:
            should_clauses.append({"match": {"gpt_description": kw}})
            should_clauses.append({"match": {"options": kw}})
            should_clauses.append({"match": {"house_feature": kw}})
            should_clauses.append({"match": {"house_explanations": kw}})

    if not filter_conditions and not should_clauses:
        # 조건이 아무것도 없을 때 → match_all 최신순
        query_body = {
            "size": 10,
            "query": {
                "match_all": {}
            },
            "sort": [
                {"posted_at": {"order": "desc"}}
            ]
        }
    elif semantic_keywords and user_vec is not None:
        # 의미조건 + 벡터 유사도 사용
        query_body = {
            "size": 10,
            "query": {
                "script_score": {
                    "query": {
                        "bool": {
                            "filter": filter_conditions,
                            "should": should_clauses,
                            "must_not": must_not_conditions,
                            "minimum_should_match": 1
                        }
                    },
                    "script": {
                        "source": "(cosineSimilarity(params.query_vector, 'gpt_description_vector') * 0.3) + 0.7",
                        "params": {
                            "query_vector": [float(x) for x in user_vec.tolist()]
                        }
                    }
                }
            }
        }
    else:
        # 의미조건 없이 일반 필터 + should 조건 (있으면 boost만)
        query_body = {
            "size": 10,
            "query": {
                "bool": {
                    "filter": filter_conditions,
                    "should": should_clauses,
                    "must_not": must_not_conditions,
                    **({"minimum_should_match": 1} if should_clauses else {})
                }
            }
        }




    res = es.search(index=ES_INDEX, body=query_body)
    hits = res["hits"]["hits"]

    if not hits:
        print("❌ 조건에 맞는 매물이 없습니다.")
        return []
    
    shown = 0
    result_list = []

    max_es_score = res["hits"]["max_score"] if res["hits"]["max_score"] else 1
    scored_hits = []

    for hit in hits:
        src = hit["_source"]
        es_score_raw = hit["_score"]
        es_score_norm = es_score_raw / max_es_score

        # 가격 점수
        max_rent = parse_price(cond.get("월세_최대") or "100만원") or 1
        actual_rent = src.get('monthly_rent', 0)
        price_score = max(0, 1 - (actual_rent / max_rent))

        # 평수 점수
        min_space_str = cond.get("평수_최소")
        min_space = float(min_space_str) if min_space_str else 1
        actual_space = src.get('space', 0)
        space_score = min(1, actual_space / min_space)

        # 안전 점수
        safety_grade = src.get('safety_grade', '').strip()
        safety_map = {'매우안전': 1.0, '안전': 0.8, '보통': 0.6, '주의': 0.3, '위험': 0.0}
        safety_score = safety_map.get(safety_grade, 0.5)

        # 종합 점수 계산 (0~10 변환)
        total_score = (
            (price_score * 0.3) +
            (space_score * 0.2) +
            (safety_score * 0.3) +
            (es_score_norm * 0.2)
        ) * 10

        scored_hits.append({
            "hit": hit,
            "total_score": total_score
        })

    # 종합 점수 기준 내림차순 정렬
    sorted_hits = sorted(scored_hits, key=lambda x: x["total_score"], reverse=True)

    shown = 0

    for i, item in enumerate(sorted_hits, 1):
        hit = item["hit"]
        total_score = item["total_score"]
        src = hit["_source"]

        safety_grade = src.get('safety_grade', '').strip()
        house_lat = src.get('location', {}).get('lat')
        house_lon = src.get('location', {}).get('lon')

        # 초기화
        walk_dist, walk_min = None, None

        # ✅ 역 기반일 경우에만 도보 거리 필터 적용
        if is_station_query and house_lat and house_lon:
            walk_dist, walk_min = get_tmap_walking_distance(
                coords[0], coords[1], house_lat, house_lon, TMAP_API_KEY
            )
            if walk_dist is None or walk_dist > walking_meter * 1.5:
                continue  # 거리가 너무 멀면 해당 매물은 스킵
        else:
            walk_dist, walk_min = None, None  # 비역기반 쿼리의 경우 None 처리

        shown += 1

        space = src.get('space')
        floor = src.get('floor')
        total_floor = src.get('total_floor')
        rooms = src.get('rooms_count')
        bath = src.get('bath_count')

        space_str = str(space) if space is not None else '-'
        floor_str = str(floor) if floor is not None else '-'
        total_floor_str = str(total_floor) if total_floor is not None else '-'
        rooms_str = str(rooms) if rooms is not None else '-'
        bath_str = str(bath) if bath is not None else '-'

        # 매물 정보 구성
        house_info = {
            "house_id": str(src.get('house_id', '')),
            "gu": str(src.get('gu', '')),
            "dong": str(src.get('dong', '')),
            "address": str(src.get('address', '')),
            "deposit_type": str(src.get('deposit_type', '')),
            "deposit": str(src.get('deposit', 0)),
            "monthly_rent": str(src.get('monthly_rent', 0)),
            "area_size": str(src.get('space', '')),  # 문자열로 변환
            "floor": str(src.get('floor', '-')),
            "total_floor": str(src.get('total_floor', '-')),
            "rooms_count": str(src.get('rooms_count', '-')),
            "bath_count": str(src.get('bath_count', '-')),
            "parking": str(src.get('parking', '')),
            "safety_grade": str(src.get('safety_grade', '')),
            "options": str(src.get('options', '')),
            "house_feature": str(src.get('house_feature', '')),
            "house_explanations": str(src.get('house_explanations', '')),
            "img_url": str(src.get('img_url', '')),
            "title": str(src.get('title', '')),
            "walking_distance": f"{round(walk_dist)} m / {round(walk_min, 1)}분" if walk_dist and walk_min else None
        }

        # 보안 경고 여부
        if safety_grade in ['주의', '위험']:
            house_info["security_warning"] = "전세사기, 허위매물의 가능성이 높은 매물입니다. 계약 전 반드시 추가 확인하세요!"

        # 매칭된 키워드
        if semantic_keywords:
            combined_text = " ".join([
                str(src.get("gpt_description", "")).lower(),
                str(src.get("house_feature", "")).lower(),
                str(src.get("house_explanations", "")).lower(),
                str(src.get("options", "")).lower()
            ])
            matched = [kw for kw in semantic_keywords if kw in combined_text]
            house_info["matched_keywords"] = matched

        result_list.append(house_info)

        # 콘솔 출력 (기존 방식 유지)
        print("\n" + "=" * 40)
        print(f"📍 {src.get('gu', '')} {src.get('dong', '')}")
        print(f"💰 {src.get('deposit_type', '')} {format_price(src.get('deposit', 0))} / {format_price(src.get('monthly_rent', 0))}")
        print(f"📏 {space_str}평 | 🏙️ {floor_str}/{total_floor_str}층")
        print(f"🏎️ 방: {rooms_str} / 욕실: {bath_str}")
        print(f"🔒 매물 안전등급: {render_safety_emoji(safety_grade)}")
        if safety_grade in ['주의', '위험']:
            print("⚠️ 전세사기, 허위매물의 가능성이 높은 매물입니다. 계약 전 반드시 추가 확인하세요!")

        none_field_detected = any(val is None for val in [space, floor, total_floor, rooms, bath])
        if none_field_detected:
            print("📢 [안내] 일부 정보는 보안상 공개되지 않았습니다. 자세한 사항은 부동산에 직접 확인 바랍니다!")

        if semantic_keywords:
            combined_text = " ".join([
                str(src.get("gpt_description", "")).lower(),
                str(src.get("house_feature", "")).lower(),
                str(src.get("house_explanations", "")).lower(),
                str(src.get("options", "")).lower()
            ])
            matched = [kw for kw in semantic_keywords if kw in combined_text]
            print(f"🏷️ (ID: {src.get('house_id', '')})")

        if is_station_query and house_lat and house_lon:
            if walk_dist is not None and walk_min is not None:
                print(f"🚶‍♂️ 역까지 도보거리: {round(walk_dist)} m / 도보시간: {round(walk_min, 1)}분")
            else:
                print("🚶‍♂️ 역까지 도보거리: 계산불가")

        if shown >= 5:
            break

    if shown == 0:
        print("❌ 도보 조건에 맞는 매물이 없습니다.")
        return []
    
    return result_list
