# 🏠 부동산 의미기반 검색 시스템 실행 가이드

사용자의 자연어 질의에서 조건을 추출하고,
의미 기반 임베딩(E5-base)과 Elasticsearch를 통해 부동산 매물을 추천하는 검색 시스템입니다.

---

## 📁 프로젝트 디렉토리 구조

```
FINAL_PROJECT_MERGE_1/
├── main/                                # 실행 코드 및 데이터 파일
│   ├── dong_coords.json                 # 행정동 기반 위경도 좌표 정보
│   ├── embedding_and_indexing_final.py # MySQL → ES 색인 및 임베딩 수행 스크립트
│   ├── embedding_vectors_part*.pkl     # E5 임베딩 벡터 파일 (분할 저장)
│   ├── index_setup.py                  # ES 인덱스 초기화 및 매핑 설정
│   ├── intent_classifier.py            # 사용자 의도 분류기 (옵션)
│   ├── main_router.py                  # 메인 실행 라우터
│   ├── search_module_final_v2.py       # 자연어 기반 부동산 검색 모듈
│   └── 서울지하철_노선정보_평균좌표_정제.csv # 지하철역 평균 위경도 정보
├── .env                                 # API 키 환경변수 (OpenAI, TMap 등)
├── Dockerfile                           # Docker 실행 환경 설정
├── requirements.txt                     # 필요한 패키지 목록
├── .gitignore                           # Git 추적 제외 설정
├── .dockerignore                        # Docker 이미지 제외 설정
├── README.md                            # 프로젝트 설명 및 실행 가이드
```

---

## 🚀 실행 순서

### 1️⃣ 환경 설정

```bash
pip install -r requirements.txt
```

### 2️⃣ Elasticsearch 색인 및 임베딩 생성

```bash
# 1. Elasticsearch 인덱스 초기화 (매핑 포함)
python main/index_setup.py

# 2. MySQL → Elasticsearch 색인 + E5 임베딩 수행
python main/embedding_and_indexing_final.py
```

* `gpt_description` 필드 기준 E5 임베딩 생성 후 `gpt_description_vector` 컬럼에 저장됨
* 전체 매물 약 1,000건 기준, 수행 시간 2\~3분 내외

---

### 3️⃣ 사용자 질의 실행

```bash
python main/main_router.py
```

* 예시 질의:

  ```
  강남역 도보 10분 이내, 월세 80만원 이하, 반려동물 가능하고 냉장고 있는 집 찾아줘
  ```

* 예시 출력:

  ```
  📍 강남구 역삼동
  💰 월세 2,000만원 / 70만원
  📏 7.5평 | 🏙️ 3/5층
  🏎️ 방: 1 / 욕실: 1
  🔒 매물 안전등급: 🟢 매우안전
  🚶‍♂️ 역까지 도보거리: 528 m / 도보시간: 7.2분
  💡 일치한 조건: ['반려동물', '냉장고']
  ```

---

## ⚙️ 빠른 실행 요약

```bash
pip install -r requirements.txt
python main/index_setup.py
python main/embedding_and_indexing_final.py
python main/main_router.py
```

---

## 📌 기타 사항

* `.env` 파일에 다음 환경변수가 필요합니다:

  * `OPENAI_API_KEY` = (GPT-4o용)
  * `KAKAO_API_KEY` = (좌표 변환용)
  * `TMAP_API_KEY` = (도보 거리 측정용)

* Elasticsearch는 8.x 이상이어야 `dense_vector` 검색 기능을 지원합니다

* 전체 검색 프로세스는 다음과 같은 구조입니다:

  1. 사용자 질의 → 조건 추출 (`OpenAI` 기반)
  2. 필터링 조건 구성 (보증금, 위치 등)
  3. 의미조건 포함 시 `E5` 임베딩 기반 의미 검색
  4. 종합 점수 계산 및 Top-N 추천 출력
