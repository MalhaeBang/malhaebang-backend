# 🏠 부동산 의미기반 검색 시스템 실행 가이드

사용자의 자연어 질의에서 조건을 추출하고, 의미 기반 임베딩(E5)과 Elasticsearch를 통해 부동산 매물을 추천하는 검색 시스템입니다.

---

## 📁 프로젝트 디렉토리 구조

```
FINAL_PROJECT_MERGE/
├── main/                                 # 실행 코드 및 데이터 파일 모음
│   ├── dong_coords.json                  # 행정동 기반 좌표 정보
│   ├── 서울지하철_노선정보_평균좌표_정제.csv   # 지하철역 평균 위경도 정보
│   ├── real_estate_full_1000_ignore.sql  # 테스트용 MySQL 부동산 데이터 (1000건)
│   ├── embedding_and_indexing.py         # MySQL → Elasticsearch 색인 및 E5 임베딩 생성
│   ├── index_setup.py                    # ES 인덱스 초기화 및 매핑 설정
│   ├── real_estate_search.py             # 자연어 질의 기반 부동산 검색 실행
│
├── .env                                  # OpenAI / TMap API 키 등 환경변수 (Git 제외)
├── .gitignore                            # Git 추적 제외 설정
├── .dockerignore                         # Docker 이미지 빌드 시 제외 파일
├── Dockerfile                            # Docker 환경 설정 파일
├── requirements.txt                      # 필요한 Python 패키지 목록
├── README.md                             # 프로젝트 설명 및 실행 가이드

```

---

## 🚀 실행 순서

### 1️⃣ 환경 설정

```bash
# 1. 필수 패키지 설치
pip install -r requirements.txt
```

```bash
# 2. MySQL 데이터베이스 초기화
mysql -u root -p real_estate_db < real_estate_full_1000_ignore.sql
```

* 데이터베이스 이름: `real_estate_db`
* 테이블명: `real_estate`
* 해당 테이블로 사용해주셔야 결과 출력됩니다 !!!!!
* 주의: `gpt_description` 컬럼이 반드시 포함되어 있어야 검색 시스템이 정상 작동합니다.
* MYSQL CONFIG 부분(포트,ID,PW)은 연결되어있는 MYSQL 설정으로 바꿔서 진행해주세요 ~

```bash
# 3. Elasticsearch가 실행 중인지 확인
브라우저에서 http://localhost:9200 접속 → JSON 응답 확인
```

---

### 2️⃣ 색인 및 임베딩 (최초 1회만 수행)

```bash
# 1. Elasticsearch 인덱스 생성
python index_setup.py
```

```bash
# 2. MySQL → Elasticsearch 데이터 색인 및 임베딩 수행
python embedding_and_indexing.py
```

* `gpt_description`을 E5-base 모델로 임베딩하여 `gpt_description_vector` 필드에 저장
* 위,경도 포함
* 주요 필드 34개가 Elasticsearch에 색인됨

---

### 3️⃣ 사용자 쿼리 검색 실행

```bash
python real_estate_search.py
```

* 예시 쿼리:

```
신사역 도보 10분 이내 전세 3억 이하이고 냉장고 세탁기 있는 집 있어?
```

* 예시 출력:

```
🟩 [Top-1] Score: 6.52
📍 강남구 신사동
💰 전세 1억 8,000만원 / 0원
📏 8.0평 | 🏙️ 2/4층
🛏️ 방: 1 / 욕실: 1
🅿️ 주차: 가능
🔒 안전등급: 🟢😄 짱안전
📫 주소: 서울시 강남구 신사동 518-12
💡 일치한 조건: ['세탁기', '냉장고', '역세권']
🚶 도보 거리: 0.54km / 약 7분 소요
```

---

## ⚙️ 빠른 실행 요약

```bash
pip install -r requirements.txt
mysql -u root -p real_estate_db < real_estate_full_1000_ignore.sql
python index_setup.py
python embedding_and_indexing.py
python real_estate_search.py
```

---

## 📌 기타 사항

* `.env` 파일에 OpenAI API 키(`OPENAI_API_KEY`), TMap API 키 등이 필요합니다.
* Elasticsearch 버전은 8.x 이상이어야 `dense_vector` 필드 사용이 가능합니다.
* 검색은 조건 필터링 + 의미 유사도 검색이 결합된 구조입니다.
