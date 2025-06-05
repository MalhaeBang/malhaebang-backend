FROM python:3.10-slim

WORKDIR /app

# Chrome 및 필요한 라이브러리 설치
RUN apt-get update && apt-get install -y \
    wget curl unzip gnupg \
    fonts-liberation libatk-bridge2.0-0 libxss1 libgtk-3-0 libasound2 \
    libnss3 libx11-xcb1 libxcomposite1 libxdamage1 libxrandr2 libgbm1 \
    libu2f-udev libvulkan1 \
    && rm -rf /var/lib/apt/lists/*

# Google Chrome 설치
RUN curl -sSL https://dl.google.com/linux/linux_signing_key.pub | gpg --dearmor -o /usr/share/keyrings/chrome-keyring.gpg && \
    echo "deb [arch=amd64 signed-by=/usr/share/keyrings/chrome-keyring.gpg] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google-chrome.list && \
    apt-get update && apt-get install -y google-chrome-stable && \
    rm -rf /var/lib/apt/lists/*

# 파이썬 패키지 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 소스 코드 복사
COPY . .

CMD ["python", "crawler.py"]