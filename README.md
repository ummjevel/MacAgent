# MacAgent

VLM(Vision Language Model) 기반 Mac 애플리케이션 자동화 시스템 POC

## 프로젝트 개요

MacAgent는 VLM을 활용하여 Mac 애플리케이션을 자동화하는 시스템입니다. 화면을 분석하고, 적절한 액션을 추론하여 자동으로 실행할 수 있습니다.

### 핵심 기능

- **VLM 기반 화면 분석**: OpenRouter API를 통한 Vision Language Model 활용
- **자동 액션 실행**: 클릭, 타이핑, 스크롤 등 UI 조작
- **세션 관리**: 자동화 작업 시작/중지/일시정지/재개
- **안전 장치**: 결제 화면 감지 및 자동 중단
- **트래킹**: 모든 액션 기록 및 추적

## 기술 스택

- **언어**: Python 3.11+
- **패키지 관리**: uv
- **API 프레임워크**: FastAPI
- **VLM Provider**: OpenRouter
- **데이터베이스**: Supabase (Mock 구현 포함)
- **UI 자동화**: pyautogui, Pillow

## 프로젝트 구조

```
MacAgent/
├── macagent/
│   ├── api/                    # FastAPI 애플리케이션
│   │   ├── routers/           # API 라우터
│   │   │   ├── sessions.py    # 세션 관리
│   │   │   ├── actions.py     # 액션 실행
│   │   │   ├── analyze.py     # VLM 분석
│   │   │   └── users.py       # 사용자 관리
│   │   ├── main.py            # FastAPI 앱
│   │   └── dependencies.py    # 의존성 주입
│   ├── vlm/                   # VLM 엔진
│   │   ├── screen_capture.py  # 화면 캡처
│   │   ├── vlm_client.py      # VLM API 클라이언트
│   │   └── action_executor.py # 액션 실행
│   ├── database/              # 데이터베이스
│   │   ├── interface.py       # DB 인터페이스
│   │   ├── mock_db.py         # Mock 구현
│   │   └── supabase_db.py     # Supabase 구현
│   ├── core/                  # 핵심 모듈
│   │   ├── config.py          # 설정 관리
│   │   ├── logger.py          # 로깅
│   │   └── models.py          # 데이터 모델
│   └── utils/                 # 유틸리티
├── tests/                     # 테스트
│   ├── test_vlm/             # VLM 테스트
│   ├── test_database/        # DB 테스트
│   ├── test_api/             # API 테스트
│   └── test_e2e.py           # E2E 테스트
├── main.py                    # 진입점
├── pyproject.toml            # 프로젝트 설정
└── requirements.md           # 요구사항 문서
```

## 설치 및 실행

### 1. 사전 요구사항

- Python 3.11 이상
- macOS (pyautogui 사용)
- uv 패키지 매니저

### 2. 프로젝트 클론

```bash
git clone https://github.com/yourusername/MacAgent.git
cd MacAgent
```

### 3. 의존성 설치

```bash
# uv가 설치되지 않은 경우
curl -LsSf https://astral.sh/uv/install.sh | sh

# 의존성 설치
uv sync --all-extras
```

### 4. 환경 변수 설정

`.env.example`을 복사하여 `.env` 파일 생성:

```bash
cp .env.example .env
```

`.env` 파일을 편집하여 필요한 값 입력:

```env
# OpenRouter API Key (필수)
OPENROUTER_API_KEY=your_api_key_here

# VLM 모델 선택
VLM_MODEL=anthropic/claude-3-5-sonnet

# Supabase 설정 (선택사항, Mock DB 사용 시 불필요)
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key
```

### 5. 서버 실행

```bash
# uv를 사용하여 실행
uv run python main.py

# 또는 직접 실행
python main.py
```

API 서버가 `http://localhost:8000`에서 실행됩니다.

### 6. API 문서 확인

브라우저에서 다음 URL로 접속:

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 테스트

### 전체 테스트 실행

```bash
uv run pytest
```

### 커버리지 포함 테스트

```bash
uv run pytest --cov=macagent --cov-report=html
```

### 특정 테스트 실행

```bash
# VLM 테스트만
uv run pytest tests/test_vlm/

# API 테스트만
uv run pytest tests/test_api/

# E2E 테스트만
uv run pytest tests/test_e2e.py
```

## Supabase 설정 (선택사항)

Mock 데이터베이스 대신 실제 Supabase를 사용하려면 다음 단계를 따르세요.

### 1. Supabase 프로젝트 생성

1. [Supabase](https://supabase.com) 접속 및 로그인
2. "New Project" 클릭
3. 프로젝트 이름, 비밀번호, 지역 선택
4. "Create new project" 클릭

### 2. 데이터베이스 테이블 생성

SQL Editor에서 다음 스키마를 실행:

```sql
-- Users 테이블
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    consent_given BOOLEAN DEFAULT FALSE,
    consent_timestamp TIMESTAMP WITH TIME ZONE
);

-- Sessions 테이블
CREATE TABLE sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    app_name TEXT NOT NULL,
    task_description TEXT NOT NULL,
    status TEXT NOT NULL CHECK (status IN ('running', 'paused', 'completed', 'failed', 'cancelled')),
    started_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    ended_at TIMESTAMP WITH TIME ZONE,
    current_step INTEGER DEFAULT 0
);

-- Actions 테이블
CREATE TABLE actions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID REFERENCES sessions(id) ON DELETE CASCADE,
    step_number INTEGER NOT NULL,
    action_type TEXT NOT NULL CHECK (action_type IN ('click', 'type', 'scroll', 'wait', 'double_click', 'right_click')),
    target_element JSONB,
    screenshot_url TEXT,
    status TEXT NOT NULL CHECK (status IN ('pending', 'success', 'failed')),
    execution_time INTEGER,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    error_message TEXT
);

-- Routes 테이블
CREATE TABLE routes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID REFERENCES sessions(id) ON DELETE CASCADE,
    planned_route JSONB NOT NULL,
    actual_route JSONB NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 인덱스 생성
CREATE INDEX idx_sessions_user_id ON sessions(user_id);
CREATE INDEX idx_actions_session_id ON actions(session_id);
CREATE INDEX idx_routes_session_id ON routes(session_id);
```

### 3. API 키 복사

1. Project Settings → API로 이동
2. "Project URL"과 "anon public" 키 복사
3. `.env` 파일에 설정:

```env
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key
```

### 4. 데이터베이스 사용

환경 변수가 설정되면 자동으로 Supabase가 사용됩니다. Mock DB와 전환하려면 환경 변수를 제거하거나 주석 처리하세요.

## OpenRouter API 키 획득

1. [OpenRouter](https://openrouter.ai) 접속
2. 계정 생성 또는 로그인
3. Settings → API Keys로 이동
4. "Create Key" 클릭하여 새 API 키 생성
5. `.env` 파일에 추가:

```env
OPENROUTER_API_KEY=your_key_here
```

### 지원 모델

다음 VLM 모델을 사용할 수 있습니다:

- `anthropic/claude-3-5-sonnet` (권장)
- `openai/gpt-4-vision-preview`
- `qwen/qwen-2-vl-72b-instruct`

`.env` 파일에서 `VLM_MODEL`을 원하는 모델로 설정하세요.

## API 사용 예제

### 세션 생성

```bash
curl -X POST "http://localhost:8000/api/v1/sessions" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "550e8400-e29b-41d4-a716-446655440000",
    "app_name": "McDonald'\''s",
    "task": "빅맥 세트 주문",
    "consent_confirmed": true
  }'
```

### 화면 분석

```bash
curl -X POST "http://localhost:8000/api/v1/analyze/screen" \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "session-uuid",
    "screenshot": "base64_encoded_image",
    "context": "맥도날드 메인 화면"
  }'
```

### 세션 일시정지

```bash
curl -X PATCH "http://localhost:8000/api/v1/sessions/{session_id}/pause"
```

## 개발

### 코드 스타일

프로젝트는 다음 도구를 사용합니다:

- Type hints (Python 3.11+)
- Pydantic for data validation
- Async/await for database operations

### 새 기능 추가

1. 적절한 모듈에 코드 작성
2. 단위 테스트 추가 (`tests/` 디렉토리)
3. API 변경 시 통합 테스트 추가
4. 문서 업데이트

### 디버깅

로그 레벨 변경:

```env
LOG_LEVEL=DEBUG
```

## 보안 및 법적 고지

⚠️ **중요**

- 이 프로젝트는 **학습 및 연구 목적**으로만 사용해야 합니다
- 타사 애플리케이션 자동화는 해당 앱의 이용약관을 위반할 수 있습니다
- **결제 화면이 감지되면 자동으로 중단**됩니다
- 사용자는 본 도구 사용으로 인한 모든 책임을 부담합니다

## 라이선스

이 프로젝트는 MIT 라이선스를 따릅니다. 자세한 내용은 [LICENSE](LICENSE) 파일을 참조하세요.

## 기여

기여를 환영합니다! 다음 단계를 따라주세요:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 문의

질문이나 제안사항이 있으시면 이슈를 생성해주세요.

## 참고 자료

- [OpenRouter API 문서](https://openrouter.ai/docs)
- [FastAPI 문서](https://fastapi.tiangolo.com)
- [Supabase 문서](https://supabase.com/docs)
- [pyautogui 문서](https://pyautogui.readthedocs.io)
