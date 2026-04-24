# 퀵스타트 (Quickstart): Problem Inquiry Engine (진단 엔진)

## 필수 선행 조건 (Prerequisites)
- **Python 3.13+** 및 **uv** 패키지 매니저 설치
- **PostgreSQL** 실행 및 데이터베이스 생성
- **Ollama** 실행 및 `gemma4:e4b` 모델 로드:
  ```bash
  ollama run gemma4:e4b
  ```

## 환경 설정 (Setup)
1. 의존성 설치:
   ```bash
   uv sync
   ```
2. 환경 변수 설정 (`.env`):
   ```env
   DATABASE_URL=postgres://user:password@localhost:5432/dbname
   OLLAMA_BASE_URL=http://localhost:11434
   ```
3. 마이그레이션 실행:
   ```bash
   python src/manage.py makemigrations
   python src/manage.py migrate
   ```

## 개발 서버 실행
```bash
python src/manage.py runserver
```

## 확인 방법
브라우저에서 `http://localhost:8000/inquiry/chat/`에 접속하여 모호한 문제(예: "우리 팀 생산성이 너무 낮아요")를 입력하고 AI의 진단 프로세스가 시작되는지 확인하십시오.
