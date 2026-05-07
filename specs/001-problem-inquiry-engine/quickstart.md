# 빠른 시작 가이드 (Quickstart): Problem Inquiry Engine (진단 엔진)

## 1. 개발 환경 설정

- **Python**: 3.13 이상
- **패키지 관리**: `uv`
- **데이터베이스**: PostgreSQL 16 이상
- **LLM 서버**: Ollama (gemma4:e4b 모델 설치 필수)

```bash
# 의존성 설치
uv sync

# Ollama 모델 준비
ollama pull gemma4:e4b
```

## 2. 환경 변수 설정 (.env)

```text
DATABASE_URL=postgres://user:password@localhost:5432/speckit_db
OLLAMA_BASE_URL=http://localhost:11434
SECRET_KEY=your-django-secret-key
```

## 3. 데이터베이스 초기화 및 실행

```bash
# 마이그레이션 실행
python src/manage.py makemigrations inquiry
python src/manage.py migrate

# 개발 서버 실행
python src/manage.py runserver
```

## 4. 진단 테스트

1. 브라우저에서 `http://localhost:8000/inquiry/` 접속.
2. 분석하고 싶은 모호한 문제 상황 입력.
3. AI의 질문에 답변하며 5단계 진단 진행.
4. 최종 Markdown 보고서 다운로드 확인.
