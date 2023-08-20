# 베이스 이미지로 Python 3.9를 사용
FROM python:3.10-slim-buster

ENV PYTHONUNBUFFERED 1

# 작업 디렉토리 설정
WORKDIR /app

# 필요한 패키지 설치
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# 프로젝트 파일 복사
COPY . /app/

# 서버 실행 명령어
CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000"]
