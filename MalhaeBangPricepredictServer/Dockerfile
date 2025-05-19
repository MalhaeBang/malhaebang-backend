# Python 3.12 slim 이미지 기반
FROM python:3.12-slim

# 필수: apt로 한글 폰트 설치
RUN apt-get update && apt-get install -y \
    fonts-nanum \
    fontconfig \
    && apt-get clean && rm -rf /var/lib/apt/lists/* \
    && fc-cache -fv

# 작업 디렉토리 설정
WORKDIR /app

# 종속성 설치를 위한 requirements 복사Ï

COPY requirements.txt .

# pip 업그레이드 및 의존성 설치
RUN pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# 나머지 애플리케이션 소스 복사
COPY . .

# Flask 실행 포트
EXPOSE 5000

# 환경변수 설정 (Flask 앱 이름)
ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0

# Flask 서버 실행
CMD ["flask", "run"]
