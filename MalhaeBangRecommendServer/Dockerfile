FROM python:3.10-slim-bullseye

# 작업 디렉토리 생성
WORKDIR /app

# 시스템 패키지 최소 설치
RUN apt-get update && apt-get install -y \
    curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# requirements.txt 복사 및 설치
COPY requirements.txt .
#RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir --no-binary :all: -r requirements.txt

# 모델 캐시 및 기타 불필요한 파일 제거
RUN rm -rf /root/.cache /root/.huggingface

# 소스 복사
COPY . .


# 포트 노출
EXPOSE 5000

# 실행 명령
CMD ["python", "app.py"]