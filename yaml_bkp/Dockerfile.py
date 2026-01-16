FROM python:3.12-slim

# (선택) 빌드 속도/안정성용 기본 패키지
RUN apt-get update \
 && apt-get install -y --no-install-recommends curl \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# 의존성 먼저 설치 (캐시 효율)
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# 앱 코드 복사
COPY main.py /app/main.py

EXPOSE 8000

# 기본 실행 (필요 시 compose에서 override 가능)
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
