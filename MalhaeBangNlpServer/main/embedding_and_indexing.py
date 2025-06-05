import pandas as pd
import pymysql
import requests
import json
import re
import random
import math
import os
from sentence_transformers import SentenceTransformer
from elasticsearch import Elasticsearch, helpers
from tqdm import tqdm
from time import sleep
from dotenv import load_dotenv

# --- 1. 설정 ---
load_dotenv()

MYSQL_CONFIG = {
    "host": os.getenv("MYSQL_HOST"),
    "user": os.getenv("MYSQL_USER"),
    "password": os.getenv("MYSQL_PASSWORD"),
    "database": os.getenv("MYSQL_DATABASE"),
    "charset": "utf8mb4"
}

VWORLD_API_KEY = os.getenv("VWORLD_API_KEY")
ES_HOST = os.getenv("ES_HOST") or "http://localhost:9200"
ES_INDEX = os.getenv("ES_INDEX") or "real_estate_location"
es = Elasticsearch(ES_HOST)
embed_model = SentenceTransformer("intfloat/e5-base")

# --- 현재 파일 기준 경로 설정 ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# --- dong_coords JSON 로드 ---
dong_coords_path = os.path.join(BASE_DIR, "dong_coords.json")
with open(dong_coords_path, "r", encoding="utf-8") as f:
    dong_coords = json.load(f)

# --- VWorld 주소 → 위경도 변환 함수 ---
def get_vworld_coords(address, api_key, addr_type="parcel"):
    if not address or address.strip() == "" or address.strip() == "주소 정보 없음":
        return None
    url = "https://api.vworld.kr/req/address"
    params = {
        "service": "address",
        "request": "getCoord",
        "format": "json",
        "key": api_key,
        "type": addr_type,
        "address": address
    }
    try:
        response = requests.get(url, params=params)
        if response.status_code == 200:
            data = response.json()
            if data["response"]["status"] == "OK":
                point = data["response"]["result"]["point"]
                lat = float(point["y"])
                lon = float(point["x"])
                return lat, lon
    except Exception as e:
        print(f"⚠️ 주소 변환 실패: {address} → {e}")
    return None

# --- fallback 동 기반 좌표 조회 함수 ---
def get_fallback_coords(gu, dong):
    key = f"{gu}_{dong}"
    return dong_coords.get(key)

def generate_random_seoul_coords():
    lat = random.uniform(37.45, 37.70)
    lon = random.uniform(126.80, 127.15)
    return lat, lon

def get_final_coords(address, gu, dong):
    coords = get_vworld_coords(address, VWORLD_API_KEY, addr_type="parcel")
    if coords:
        return coords, "vworld"
    fallback = get_fallback_coords(gu, dong)
    if fallback:
        return fallback, "dong_coords"
    return generate_random_seoul_coords(), "random"

# --- DB에서 매물 데이터 로드 ---
print("📅 MySQL에서 매물 데이터 로드 중...")
conn = pymysql.connect(**MYSQL_CONFIG)
df = pd.read_sql("SELECT * FROM real_estate", conn)
conn.close()

# --- 색인할 문서 리스트 생성 ---
def build_docs(df):
    docs = []
    texts = df["gpt_description"].fillna("").astype(str).tolist()
    vectors = embed_model.encode(texts, show_progress_bar=True)

    for i, (_, row) in enumerate(df.iterrows()):
        dong = str(row.get("dong", ""))
        gu = str(row.get("gu", ""))
        address = str(row.get("address", ""))

        latlon, method = get_final_coords(address, gu, dong)

        doc_body = {
            "house_id": str(row.get("house_id", "")),
            "title": str(row.get("title", "")),
            "price": str(row.get("price", "")),
            "address": str(row.get("address", "")),
            "floor": int(row["floor"]) if pd.notna(row.get("floor")) else None,
            "deposit_type": str(row.get("deposit_type", "")),
            "management_fee": int(row["management_fee"]) if pd.notna(row.get("management_fee")) else None,
            "rooms_count": int(row["rooms_count"]) if pd.notna(row.get("rooms_count")) else None,
            "options": str(row.get("options", "")),
            "gu": str(row.get("gu", "")),
            "dong": str(row.get("dong", "")),
            "area_size": str(row.get("area_size", "")),
            "direction": str(row.get("direction", "")),
            "built_date": str(row.get("built_date", "")),
            "parking": str(row.get("parking", "")),
            "building_type": str(row.get("building_type", "")),
            "house_feature": str(row.get("house_feature", "")),
            "house_explanations": str(row.get("house_explanations", "")),
            "safety_grade": str(row.get("safety_grade", "")),
            "deposit": int(row["deposit"]) if pd.notna(row.get("deposit")) else None,
            "monthly_rent": int(row["monthly_rent"]) if pd.notna(row.get("monthly_rent")) else None,
            "space": float(row["space"]) if pd.notna(row.get("space")) else None,
            "bath_count": int(row["bath_count"]) if pd.notna(row.get("bath_count")) else None,
            "total_floor": int(row["total_floor"]) if pd.notna(row.get("total_floor")) else None,
            "gpt_description": str(row.get("gpt_description", "")),
            "gpt_description_vector": vectors[i].tolist()
        }

        if latlon:
            doc_body["location"] = {"lat": latlon[0], "lon": latlon[1]}

        doc = {
            "_index": ES_INDEX,
            "_id": str(row["house_id"]),
            "_source": doc_body
        }
        docs.append(doc)
    return docs

# --- Elasticsearch 색인 시작 ---
print("📦 Elasticsearch 색인 시작...")
docs = build_docs(df)
for ok, result in tqdm(helpers.streaming_bulk(es, docs), total=len(docs), desc="Indexing"):
    if not ok:
        print("❌ 색인 실패 항목:", result)
print("✅ ES 색인 완료!")
