# Python 3.10 기반 이미지 사용 (numpy, pandas, faiss 호환성 고려)
FROM python:3.10-slim

# 시스템 패키지 업데이트 및 필수 패키지 설치 (FAISS 빌드에 필요한 항목 포함)
RUN apt-get update && apt-get install -y \
    build-essential \
    wget \
    curl \
    git \
    libopenblas-dev \
    && rm -rf /var/lib/apt/lists/*

# 작업 디렉토리 생성
WORKDIR /app

# requirements.txt 복사
COPY requirements.txt .

# 패키지 설치
RUN pip install --upgrade pip \
 && pip install --no-cache-dir -r requirements.txt

# 앱 코드 복사 (Flask app.py 기준)
COPY . .

# 기본 실행 포트 설정
EXPOSE 5000

# Flask 실행 (app.py 기준 / 원하는 파일명으로 바꾸세요)
CMD ["python", "app.py"]