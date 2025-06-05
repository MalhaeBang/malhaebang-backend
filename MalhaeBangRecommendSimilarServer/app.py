from flask import Flask, request, jsonify, render_template
from sqlalchemy import create_engine, text
import pandas as pd
import numpy as np
import faiss
import json
import os
import logging
from dotenv import load_dotenv
load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)

app = Flask(__name__, template_folder="templates")
app.config["PROPAGATE_EXCEPTIONS"] = True

# 환경변수 기반 DB 접속 설정
db_user = os.environ.get("DATABASE_USER", "root")
db_password = os.environ.get("DATABASE_PASSWORD", "1234")
db_host = os.environ.get("DATABASE_HOST", "mysql")
db_port = os.environ.get("DATABASE_PORT", "3306")
db_name = os.environ.get("DATABASE_NAME", "malhaebang")

# SQLAlchemy Engine
engine = create_engine(
    f"mysql+pymysql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}",
    pool_recycle=3600,
    pool_pre_ping=True
)

# FAISS 인덱스 로딩
index = faiss.read_index("faiss_index.faiss")

# 임베딩 로딩 함수
def get_embedding_from_db(house_num):
    logger.info(f"임베딩 조회 시작: house_num={house_num}")
    with engine.connect() as conn:
        result = conn.execute(
            text("SELECT final_embedding FROM house WHERE house_num = :house_num"),
            {"house_num": house_num}
        )
        row = result.fetchone()
        if row is None:
            logger.warning(f"[DB] house_num={house_num} not found")
            return None
        try:
            emb = np.array(json.loads(row[0]), dtype='float32')
            logger.info(f"임베딩 조회 성공: shape={emb.shape}")
            return emb
        except Exception as e:
            logger.error(f"임베딩 파싱 실패: {e}")
            return None

# 매물 정보 로딩
def get_house_info_by_ids(house_nums):
    if not house_nums:
        return pd.DataFrame(columns=[])
    placeholders = ','.join([f":id{i}" for i in range(len(house_nums))])
    param_dict = {f"id{i}": num for i, num in enumerate(house_nums)}
    query = text(f"""
        SELECT house_num, title, address, gu, dong, price, area_size,
               space, img_url, management_fee,
               rooms_count, bath_count, floor, total_floor, house_feature,
               safety_score
        FROM house
        WHERE house_num IN ({placeholders})
    """)
    with engine.connect() as conn:
        result = conn.execute(query, param_dict)
        df = pd.DataFrame(result.fetchall(), columns=result.keys())
    return df

@app.route("/recommend", methods=["GET"])
def recommend():
    try:
        house_num = request.args.get("house_num", type=int)
        top_k = request.args.get("top_k", default=10, type=int)
        logger.info(f"/recommend 요청 도착: house_num={house_num}, top_k={top_k}")

        if house_num is None:
            logger.warning("house_num 파라미터 없음")
            return jsonify({"error": "house_num parameter required"}), 400

        query_vec = get_embedding_from_db(house_num)
        if query_vec is None:
            return jsonify({"error": f"house_num {house_num} not found"}), 404

        query_vec = query_vec.reshape(1, -1)
        faiss.normalize_L2(query_vec)
        D, I = index.search(query_vec, top_k)

        logger.info(f"유사 매물 검색 완료: 결과 수={len(I[0])}")
        similar_ids = [int(i) for i in I[0]]
        df = get_house_info_by_ids(similar_ids)

        if df.empty:
            return jsonify({"recommendations": []})

        df['similarity'] = D[0][:len(df)]
        df = df[df['similarity'] < 0.9999]
        df = df.drop_duplicates(subset=['title', 'address', 'gu', 'dong', 'price', 'space'])

        return jsonify({"recommendations": df.to_dict(orient="records")})

    except Exception as e:
        logger.exception(f"추천 처리 중 예외 발생: {e}")
        return jsonify({"error": "internal server error"}), 500

@app.route("/list")
def house_list():
    query = request.args.get("q", "").strip()
    with engine.connect() as conn:
        if query:
            sql = text("""
                SELECT house_num, title, address, gu, dong, price, area_size,
                       space, img_url, management_fee,
                       rooms_count, bath_count, floor, total_floor, house_feature,
                       safety_score
                FROM house
                WHERE title LIKE :q
                ORDER BY RAND() LIMIT 20
            """)
            result = conn.execute(sql, {"q": f"%{query}%"})
        else:
            sql = text("""
                SELECT house_num, title, address, gu, dong, price, area_size,
                       space, img_url, management_fee,
                       rooms_count, bath_count, floor, total_floor, house_feature,
                       safety_score
                FROM house
                ORDER BY RAND() LIMIT 20
            """)
            result = conn.execute(sql)
        rows = result.fetchall()
        columns = result.keys()
        df = pd.DataFrame(rows, columns=columns)

    def safe_extract_thumbnail(x):
        try:
            parsed = json.loads(x) if isinstance(x, str) else x
            return parsed[0] if isinstance(parsed, list) and len(parsed) > 0 else "/static/default.jpg"
        except:
            return "/static/default.jpg"

    df["thumbnail"] = df["img_url"].apply(safe_extract_thumbnail)
    return render_template("house_list.html", houses=df.to_dict(orient="records"), query=query)

@app.route("/recommend_ui", methods=["GET"])
def recommend_ui():
    house_num = request.args.get("house_num", type=int)
    top_k = request.args.get("top_k", default=10, type=int)
    if not house_num:
        return "<h2>house_num 파라미터가 필요합니다.</h2>", 400

    df = pd.read_sql("SELECT * FROM house", engine)
    row_match = df[df["house_num"] == house_num]
    if row_match.empty:
        return f"<h2>매물번호 {house_num} 에 해당하는 매물이 없습니다.</h2>", 404

    target_series = row_match.iloc[0]
    target_dict = target_series.to_dict()
    logger.info(f"추천 대상 매물 정보: {target_dict}")

    # safety_score 없으면 기본값으로 대체
    target_dict["safety_score"] = target_series.get("safety_score", "-")

    def extract_thumbnail(img_url_str):
        try:
            imgs = json.loads(img_url_str)
            return imgs[0] if imgs and isinstance(imgs, list) else "/static/default.jpg"
        except:
            return "/static/default.jpg"

    target_dict["thumbnail"] = extract_thumbnail(target_dict.get("img_url", "[]"))

    result_df = pd.DataFrame(columns=["house_num", "title", "address", "gu", "dong", "price", "space", "img_url", "similarity", "safety_score"])

    # FAISS 예외처리: final_embedding이 없거나 잘못된 경우, 추천 생략
    try:
        embedding_str = target_series["final_embedding"]
        if embedding_str:
            query_vec = np.array(json.loads(embedding_str), dtype='float32').reshape(1, -1)
            faiss.normalize_L2(query_vec)
            D, I = index.search(query_vec, top_k + 5)

            result_rows = []
            for dist, idx in zip(D[0], I[0]):
                if 0 <= idx < len(df):
                    result_rows.append({**df.iloc[idx].to_dict(), "similarity": dist})

            result_df = pd.DataFrame(result_rows)
            result_df = result_df[result_df["house_num"] != house_num]
            result_df = result_df.drop_duplicates(subset=["title", "address", "gu", "dong", "price", "area_size"])
            result_df["thumbnail"] = result_df["img_url"].apply(extract_thumbnail)
            result_df = result_df.head(top_k)
        else:
            logger.warning(f"해당 매물 house_num={house_num} 의 final_embedding이 없음.")
    except Exception as e:
        logger.warning(f"추천 수행 중 오류 발생 (무시하고 UI만 렌더링): {e}")

    return render_template(
        "recommend.html",
        target=target_dict,
        title=target_dict["title"],
        house_num=house_num,
        items=result_df.to_dict(orient="records"),
        loads=json.loads
    )

@app.template_filter('from_json')
def from_json_filter(s):
    try:
        return json.loads(s)
    except:
        return []

@app.errorhandler(Exception)
def handle_exception(e):
    logger.exception("서버 내부 오류 발생")
    return jsonify({"error": "internal server error"}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)