import pymysql
import pandas as pd
import pickle
import os
import glob
from elasticsearch import Elasticsearch, helpers
from tqdm import tqdm
from dotenv import load_dotenv

load_dotenv()

MYSQL_CONFIG = {
    "host": os.getenv("MYSQL_HOST"),
    "user": os.getenv("MYSQL_USER"),
    "password": os.getenv("MYSQL_PASSWORD"),
    "database": os.getenv("MYSQL_DATABASE"),
    "charset": "utf8mb4"
}
TABLE_NAME = "cleaned_house"
ES_HOST = "http://localhost:9200"
ES_INDEX = "cleaned_house"
es = Elasticsearch(ES_HOST)

# --- MySQL에서 데이터 로드 ---
print("📅 MySQL에서 house_id 및 색인용 컬럼 로드 중...")
conn = pymysql.connect(**MYSQL_CONFIG)
df = pd.read_sql(
    f"SELECT house_id, title, price, address, floor, deposit_type, management_fee, "
    f"available_from, house_num, agent_comm, agent_info, rooms_count, options, posted_at, "
    f"gu, dong, img_url, area_size, direction, built_date, parking, building_type, "
    f"house_feature, house_explanations, safety_grade, deposit, monthly_rent, space, "
    f"bath_count, total_floor, latitude, longitude, gpt_description "
    f"FROM {TABLE_NAME}",
    conn
)
conn.close()
df = df.set_index("house_id")

# --- pkl 파일 순회 ---
pkl_files = sorted(glob.glob("embedding_vectors_part*.pkl"))
print(f"🔍 총 {len(pkl_files)}개의 pkl 파일 발견됨")

for pkl_file in pkl_files:
    print(f"🔄 {pkl_file} 불러오는 중...")
    with open(pkl_file, "rb") as f:
        id_vector_dict = pickle.load(f)

    # --- 문서 생성 ---
    docs = []
    for house_id, vector in id_vector_dict.items():
        if house_id not in df.index:
            continue  # DB에 없는 경우 무시

        row = df.loc[house_id]
        agent_comm_val = int(row["agent_comm"]) if pd.notna(row["agent_comm"]) else None
        if agent_comm_val is not None and agent_comm_val > 2147483647:
            agent_comm_val = 2147483647  # ES int 최대값 제한

        doc_body = {
            "house_id": str(house_id),
            "title": str(row.get("title", "")),
            "price": str(row.get("price", "")),
            "address": str(row.get("address", "")),
            "floor": int(row["floor"]) if pd.notna(row["floor"]) else None,
            "deposit_type": str(row.get("deposit_type", "")),
            "management_fee": int(row["management_fee"]) if pd.notna(row["management_fee"]) else None,
            "available_from": str(row.get("available_from", "")),
            "house_num": str(row.get("house_num", "")),
            "agent_comm": agent_comm_val,
            "agent_info": str(row.get("agent_info", "")),
            "rooms_count": int(row["rooms_count"]) if pd.notna(row["rooms_count"]) else None,
            "options": str(row.get("options", "")),
            "posted_at": str(row.get("posted_at", "")),
            "gu": str(row.get("gu", "")),
            "dong": str(row.get("dong", "")),
            "img_url": str(row.get("img_url", "")),
            "area_size": str(row.get("area_size", "")),
            "direction": str(row.get("direction", "")),
            "built_date": str(row.get("built_date", "")),
            "parking": int(row["parking"]) if pd.notna(row["parking"]) else None,
            "building_type": str(row.get("building_type", "")),
            "house_feature": str(row.get("house_feature", "")),
            "house_explanations": str(row.get("house_explanations", "")),
            "safety_grade": str(row.get("safety_grade", "")),
            "deposit": int(row["deposit"]) if pd.notna(row["deposit"]) else None,
            "monthly_rent": int(row["monthly_rent"]) if pd.notna(row["monthly_rent"]) else None,
            "space": float(row["space"]) if pd.notna(row["space"]) else None,
            "bath_count": int(row["bath_count"]) if pd.notna(row["bath_count"]) else None,
            "total_floor": int(row["total_floor"]) if pd.notna(row["total_floor"]) else None,
            "gpt_description": str(row.get("gpt_description", "")),
            "gpt_description_vector": vector.tolist()
        }

        if pd.notna(row.get("latitude")) and pd.notna(row.get("longitude")):
            doc_body["location"] = {
                "lat": float(row["latitude"]),
                "lon": float(row["longitude"])
            }

        doc = {
            "_index": ES_INDEX,
            "_id": str(house_id),
            "_source": doc_body
        }
        docs.append(doc)

    # --- Elasticsearch 색인 ---
    print(f"📦 Elasticsearch 색인 시작 ({pkl_file})...")
    for ok, result in tqdm(
        helpers.streaming_bulk(es, docs, raise_on_error=False),
        total=len(docs),
        desc=f"Indexing {pkl_file}"
    ):
        if not ok:
            action = (
                result.get('index') or
                result.get('create') or
                result.get('update') or
                {}
            )
            doc_id = action.get('_id', 'unknown')
            error = action.get('error', {})
            print(f"❌ 색인 실패 - ID: {doc_id}, 이유: {error}")

print("✅ 전체 ES 색인 완료!")
