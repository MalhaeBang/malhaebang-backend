import pandas as pd
import pymysql
import pickle
import os
from sentence_transformers import SentenceTransformer
from tqdm import tqdm
from dotenv import load_dotenv
import torch

load_dotenv()

MYSQL_CONFIG = {
    "host": os.getenv("MYSQL_HOST"),
    "user": os.getenv("MYSQL_USER"),
    "password": os.getenv("MYSQL_PASSWORD"),
    "database": os.getenv("MYSQL_DATABASE"),
    "charset": "utf8mb4"
}

# --- MySQL에서 데이터 로드 ---
print("📅 MySQL에서 house_id 및 색인용 컬럼 로드 중...")
conn = pymysql.connect(**MYSQL_CONFIG)
df = pd.read_sql(
    """
    SELECT house_id, gpt_description 
    FROM house
    """,
    conn
)
conn.close()

# --- 벡터 생성 ---
print("🔄 벡터 생성 중...")
device = "cpu"
print(f"💻 사용 중인 디바이스: {device}")

embed_model = SentenceTransformer("intfloat/e5-base")
embed_model.to(device)

texts = df["gpt_description"].fillna("").astype(str).tolist()
vectors = embed_model.encode(
    texts, 
    show_progress_bar=True,
    batch_size=16,  # CPU에서는 배치 크기를 줄임
    convert_to_numpy=True,
    normalize_embeddings=True  # 벡터 정규화 추가
)

# --- 벡터를 딕셔너리로 변환 ---
id_vector_dict = {str(row["house_id"]): vector for row, vector in zip(df.itertuples(), vectors)}

# --- pkl 파일로 저장 ---
print("💾 벡터 저장 중...")
with open("main/embedding_vectors.pkl", "wb") as f:
    pickle.dump(id_vector_dict, f)

print("✅ 벡터 생성 및 저장 완료!") 