#FROM python:3.10-slim
#
#WORKDIR /app
#
#RUN apt-get update && apt-get install -y build-essential
#
#COPY requirements.txt .
#
#RUN pip install --upgrade pip && pip install --no-cache-dir --no-binary :all: -r requirements.txt
#
#COPY . /app
#
#EXPOSE 8000
#
#CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]