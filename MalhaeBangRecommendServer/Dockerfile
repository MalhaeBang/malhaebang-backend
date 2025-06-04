FROM python:3.10-slim-bullseye as builder

WORKDIR /app

# 빌드 시에만 필요한 패키지 설치
RUN apt-get update && apt-get install -y \
    build-essential \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

# 의존성 설치
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# 최종 이미지
FROM python:3.10-slim-bullseye

WORKDIR /app

# 실행에 필요한 최소한의 패키지만 설치
RUN apt-get update && apt-get install -y \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# 빌더에서 설치한 패키지 복사
COPY --from=builder /usr/local/lib/python3.10/site-packages/ /usr/local/lib/python3.10/site-packages/

# 애플리케이션 코드 복사
COPY . .

# __pycache__ 제거
RUN find . -type d -name "__pycache__" -exec rm -r {} +

EXPOSE 5000

CMD ["python", "app.py"]