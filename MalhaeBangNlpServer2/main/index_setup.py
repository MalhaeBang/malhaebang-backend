from elasticsearch import Elasticsearch
from elasticsearch.exceptions import BadRequestError, ConnectionError, TransportError

# --- Elasticsearch 접속 설정 ---
ES_HOST = "http://localhost:9200"
ES_ID = "elastic"
ES_PW = "elasticteam3"
index_name = "cleaned_house"  # 인덱스 이름 변경

print(f"📡 Elasticsearch 연결 시도: {ES_HOST}")
try:
    es = Elasticsearch(
        ES_HOST,
        basic_auth=(ES_ID, ES_PW),
        verify_certs=False
    )
    if not es.ping():
        print("❌ Elasticsearch 서버 응답 없음. 실행 중인지 확인하세요.")
        exit(1)
except Exception as e:
    print(f"❌ 연결 실패: {e}")
    exit(1)

print(f"📝 인덱스 이름: {index_name!r}")

# --- 기존 인덱스 삭제 ---
try:
    if es.indices.exists(index=index_name):
        print(f"🗑 기존 인덱스 '{index_name}' 삭제 중...")
        es.indices.delete(index=index_name)
except BadRequestError as e:
    print(f"❌ BadRequestError (존재 여부 확인 중): {e}")
    exit(1)
except Exception as e:
    print(f"❌ 기타 삭제 에러: {e}")
    exit(1)

# --- 인덱스 매핑 정의 ---
mapping = {
    "mappings": {
        "properties": {
            "house_id": {"type": "keyword"},
            "title": {"type": "text"},
            "price": {"type": "text"},
            "address": {"type": "text"},
            "floor": {"type": "integer"},
            "deposit_type": {"type": "keyword"},
            "management_fee": {"type": "integer"},
            "available_from": {"type": "text"},
            "house_num": {"type": "keyword"},
            "agent_comm": {"type": "integer"},
            "agent_info": {"type": "text"},
            "rooms_count": {"type": "integer"},
            "options": {"type": "text"},
            "posted_at": {"type": "text"},
            "gu": {"type": "keyword"},
            "dong": {"type": "keyword"},
            "img_url": {"type": "text"},
            "area_size": {"type": "text"},
            "direction": {"type": "keyword"},
            "built_date": {"type": "text"},
            "parking": {"type": "integer"},
            "building_type": {"type": "text"},
            "house_feature": {"type": "text"},
            "house_explanations": {"type": "text"},
            "safety_grade": {"type": "keyword"},
            "deposit": {"type": "integer"},
            "monthly_rent": {"type": "integer"},
            "space": {"type": "integer"},
            "bath_count": {"type": "integer"},
            "total_floor": {"type": "integer"},
            "gpt_description": {"type": "text"},
            "latitude": {"type": "double"},
            "longitude": {"type": "double"},
            "location": {"type": "geo_point"},
            "gpt_description_vector": {
                "type": "dense_vector",
                "dims": 768,
                "index": True,
                "similarity": "cosine"
            }
        }
    }
}

# --- 인덱스 생성 ---
try:
    print(f"📦 인덱스 '{index_name}' 생성 시도...")
    es.indices.create(index=index_name, body=mapping)
    print("✅ 인덱스 생성 완료 (geo_point 및 dense_vector 포함)")
except BadRequestError as e:
    print(f"❌ BadRequestError (매핑 오류): {e.info}")
except TransportError as e:
    print(f"❌ TransportError: {e.info}")
except Exception as e:
    print(f"❌ 예기치 못한 에러: {e}")
