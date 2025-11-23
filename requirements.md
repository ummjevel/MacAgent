# MacAgent VLM POC - Requirements Document

## 프로젝트 개요

VLM(Vision Language Model) 또는 OCR + VLM을 활용한 맥 애플리케이션 자동화 시스템 POC

### 핵심 기술 스택
- **VLM Provider**: OpenRouter API
- **API Framework**: FastAPI
- **Database**: Supabase (무료 티어)
- **Model**: AgentCPM-GUI 또는 기타 VLM 모델

---

## 1. 시스템 아키텍처

### 1.1 구성 요소
```
┌─────────────────┐
│  Client (Mac)   │
│  - UI/Controls  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   FastAPI       │
│   API Server    │
└────────┬────────┘
         │
    ┌────┴────┐
    ▼         ▼
┌────────┐ ┌──────────┐
│OpenRouter│Supabase  │
│VLM API  │ Database │
└─────────┘ └──────────┘
```

### 1.2 모듈 구조
1. **VLM Engine**
   - OpenRouter API 연동
   - 이미지 처리 및 분석
   - 액션 추론 및 생성

2. **API Server (FastAPI)**
   - RESTful API 엔드포인트
   - 요청/응답 처리
   - 세션 관리

3. **Database (Supabase)**
   - 실행 기록 저장
   - 사용자 동의 관리
   - 액션 트래킹 로그

---

## 2. 기능 요구사항

### 2.1 POC 단계 기능

#### 입출력
- **입력**: 텍스트 기반 명령
- **출력**: 텍스트 기반 응답 및 액션 정보
- *(음성 입출력은 고도화 단계에서 구현)*

#### 실행 제어
- [x] **시작**: 자동화 작업 시작
- [x] **중지**: 작업 완전 중단
- [x] **일시정지**: 작업 임시 중단
- [x] **취소 후 홈 이동**: 작업 취소 및 초기 화면 복귀

#### 피드백 시스템
- [x] **현재 진행 상태 표시**: 실시간 작업 진행 상황
- [x] **다음 동작 미리보기**: 다음 수행할 액션 사전 표시
- [x] **마지막 확인**: 작업 완료 전 사용자 최종 확인

#### 오류 처리
- [x] **실패 감지**: 액션 실패 자동 감지
- [x] **사용자 개입 요청**: 실패 시 사용자 개입 방법 안내
- [x] **재시도 옵션**: 실패한 단계 재시도 기능

#### 트래킹 및 로깅
- [x] **전체 루트 트래킹**: 인지 단계에서 전체 경로 저장
- [x] **액션 히스토리**: 모든 수행 액션 기록
- [x] **타임스탬프**: 각 단계별 실행 시간 기록

### 2.2 고도화 단계 기능 (향후)
- [ ] 음성 입력/출력
- [ ] Human-in-the-loop 자동화
- [ ] 배터리 최적화 및 전력 관리
- [ ] 범용 앱 지원

---

## 3. 타겟 애플리케이션

### 3.1 POC 타겟
- **앱**: 맥도날드 앱 (특정 앱)
- **자동화 범위**: 주문부터 **결제 이전 단계까지**
- **제외 사항**: 실제 결제 실행

### 3.2 제약사항
- **앱 업데이트 대응**: 지원하지 않음 (고정 버전)
- **확장성**: 향후 범용 앱 지원으로 확대 가능

---

## 4. 성능 요구사항

### 4.1 응답 시간
- **목표**: 한 단계당 10초 이내
- **측정 기준**: 액션 인식부터 실행 완료까지

### 4.2 정확도
- **단계별 정확도**: 60% 이상
- **전체 작업 정확도**: 60% 이상
- **측정 방법**: 성공한 액션 수 / 전체 액션 수

### 4.3 안정성
- **에러 복구**: 실패 시 사용자 개입으로 복구
- **세션 관리**: 중단된 세션 재개 가능

---

## 5. 데이터 관리

### 5.1 Supabase 스키마

#### Users Table
```sql
- id (uuid, primary key)
- created_at (timestamp)
- consent_given (boolean)
- consent_timestamp (timestamp)
```

#### Sessions Table
```sql
- id (uuid, primary key)
- user_id (uuid, foreign key)
- app_name (text)
- task_description (text)
- status (text: 'running', 'paused', 'completed', 'failed', 'cancelled')
- started_at (timestamp)
- ended_at (timestamp)
```

#### Actions Table
```sql
- id (uuid, primary key)
- session_id (uuid, foreign key)
- step_number (integer)
- action_type (text: 'click', 'type', 'scroll', etc.)
- target_element (jsonb)
- screenshot_url (text)
- status (text: 'pending', 'success', 'failed')
- execution_time (integer, milliseconds)
- timestamp (timestamp)
```

#### Routes Table
```sql
- id (uuid, primary key)
- session_id (uuid, foreign key)
- planned_route (jsonb)
- actual_route (jsonb)
- created_at (timestamp)
```

---

## 6. API 명세

### 6.1 엔드포인트

#### 세션 관리
```
POST   /api/v1/sessions              # 새 세션 시작
GET    /api/v1/sessions/{id}         # 세션 상태 조회
PATCH  /api/v1/sessions/{id}/pause   # 세션 일시정지
PATCH  /api/v1/sessions/{id}/resume  # 세션 재개
PATCH  /api/v1/sessions/{id}/cancel  # 세션 취소
DELETE /api/v1/sessions/{id}         # 세션 삭제
```

#### 액션 실행
```
POST   /api/v1/actions                # 다음 액션 요청
GET    /api/v1/actions/{id}           # 액션 결과 조회
POST   /api/v1/actions/{id}/confirm   # 액션 실행 확인
POST   /api/v1/actions/{id}/retry     # 액션 재시도
```

#### VLM 분석
```
POST   /api/v1/analyze/screen         # 스크린샷 분석
POST   /api/v1/analyze/element        # UI 요소 분석
```

#### 사용자 관리
```
POST   /api/v1/users/consent          # 사용자 동의 저장
GET    /api/v1/users/consent          # 동의 여부 조회
```

### 6.2 요청/응답 예시

#### POST /api/v1/sessions
```json
Request:
{
  "user_id": "uuid",
  "app_name": "McDonald's",
  "task": "주문하기: 빅맥 세트 1개",
  "consent_confirmed": true
}

Response:
{
  "session_id": "uuid",
  "status": "running",
  "current_step": 0,
  "next_action_preview": {
    "type": "click",
    "target": "메뉴 버튼",
    "description": "메인 메뉴로 이동"
  }
}
```

#### POST /api/v1/analyze/screen
```json
Request:
{
  "session_id": "uuid",
  "screenshot": "base64_encoded_image",
  "context": "현재 맥도날드 앱 메인 화면"
}

Response:
{
  "analysis": {
    "current_screen": "메인 화면",
    "available_actions": [
      {
        "type": "click",
        "element": "주문하기 버튼",
        "coordinates": {"x": 100, "y": 200},
        "confidence": 0.95
      }
    ],
    "recommended_action": {
      "type": "click",
      "target": "주문하기 버튼",
      "reasoning": "주문을 시작하기 위해 주문하기 버튼 클릭 필요"
    }
  }
}
```

---

## 7. 법적 및 윤리적 요구사항

### 7.1 사용 목적
- **명시**: 학습 및 연구 목적 전용
- **제한**: 상업적 자동화 금지

### 7.2 사용자 동의
- **초기 실행 시 필수 동의 항목**:
  1. 자동화 범위 명시 (결제 이전까지)
  2. 타 앱 자동화의 법적 리스크 고지
  3. 학습 목적 사용 확인
  4. 데이터 수집 및 저장 동의

### 7.3 악용 방지
- **결제 차단**: 결제 화면 감지 시 자동 중단
- **경고 메시지**: 초기 실행 시 책임 소재 안내
- **로깅**: 모든 액션 기록 및 추적 가능

### 7.4 안내 메시지 예시
```
⚠️  중요 안내

본 애플리케이션은 학습 및 연구 목적으로만 사용됩니다.

1. 자동화 범위: 맥도날드 앱에서 주문 과정 중 결제 이전 단계까지만 자동화됩니다.
2. 실제 결제는 수행되지 않으며, 결제 화면 감지 시 자동으로 중단됩니다.
3. 타사 애플리케이션 자동화는 해당 앱의 이용약관을 위반할 수 있습니다.
4. 사용자는 본 도구 사용으로 인한 모든 책임을 부담합니다.

계속 진행하시겠습니까? [동의함] [취소]
```

---

## 8. 개발 우선순위

### Phase 1: 기본 인프라 (Week 1-2)
- [ ] FastAPI 서버 구축
- [ ] OpenRouter API 연동
- [ ] Supabase 설정 및 스키마 생성
- [ ] 기본 API 엔드포인트 구현

### Phase 2: VLM 엔진 (Week 2-3)
- [ ] 스크린샷 캡처 및 전처리
- [ ] VLM 이미지 분석 파이프라인
- [ ] 액션 추론 로직
- [ ] 응답 파싱 및 구조화

### Phase 3: 실행 제어 (Week 3-4)
- [ ] 시작/중지/일시정지 구현
- [ ] 액션 실행 엔진
- [ ] 에러 처리 및 복구
- [ ] 피드백 시스템

### Phase 4: 맥도날드 앱 통합 (Week 4-5)
- [ ] 맥도날드 앱 UI 분석
- [ ] 주문 플로우 매핑
- [ ] 결제 차단 로직
- [ ] 엔드-투-엔드 테스트

### Phase 5: 안전 및 규정 준수 (Week 5-6)
- [ ] 사용자 동의 UI
- [ ] 경고 메시지 구현
- [ ] 로깅 및 트래킹 완성
- [ ] 법적 고지 문서

---

## 9. 기술 스택 상세

### 9.1 Backend
```python
# requirements.txt
fastapi==0.104.1
uvicorn==0.24.0
python-dotenv==1.0.0
supabase==2.0.3
openai==1.3.0  # OpenRouter compatible
pillow==10.1.0
pydantic==2.5.0
httpx==0.25.1
```

### 9.2 VLM 모델 옵션
1. **AgentCPM-GUI** (우선)
2. **GPT-4V** (OpenRouter)
3. **Claude 3 Sonnet** (OpenRouter)
4. **LLaVA** (백업)

### 9.3 환경 변수
```env
OPENROUTER_API_KEY=your_key
SUPABASE_URL=your_url
SUPABASE_KEY=your_key
VLM_MODEL=agentcpm-gui
MAX_RETRIES=3
TIMEOUT_SECONDS=10
LOG_LEVEL=INFO
```

---

## 10. 테스트 요구사항

### 10.1 단위 테스트
- API 엔드포인트 테스트
- VLM 응답 파싱 테스트
- 데이터베이스 CRUD 테스트

### 10.2 통합 테스트
- 전체 세션 플로우 테스트
- 에러 복구 시나리오 테스트
- 성능 벤치마크 (10초 응답 시간)

### 10.3 사용자 시나리오 테스트
- 맥도날드 앱 전체 주문 플로우
- 중간 일시정지/재개
- 에러 발생 시 복구
- 결제 직전 자동 중단

---

## 11. 모니터링 및 로깅

### 11.1 로깅 레벨
- **INFO**: 세션 시작/종료, 액션 실행
- **WARNING**: 재시도, 예상치 못한 UI 상태
- **ERROR**: API 실패, VLM 분석 실패
- **CRITICAL**: 결제 화면 감지, 시스템 오류

### 11.2 메트릭
- 평균 응답 시간
- 단계별 성공률
- 전체 작업 성공률
- API 호출 횟수 및 비용

---

## 12. 배포 및 운영

### 12.1 개발 환경
- Python 3.10+
- macOS 13.0+

### 12.2 POC 배포
- 로컬 FastAPI 서버
- Supabase 클라우드 (무료 티어)
- OpenRouter API (종량제)

### 12.3 비용 추정
- **Supabase**: $0 (무료 티어, 500MB DB)
- **OpenRouter**: ~$0.01-0.05 per request (모델별 상이)
- **예상 POC 비용**: ~$10-20/월

---

## 부록 A: 용어 정의

- **VLM**: Vision Language Model, 이미지와 텍스트를 동시에 이해하는 AI 모델
- **POC**: Proof of Concept, 개념 증명
- **Human-in-the-loop**: 자동화 과정에 사람의 개입이 포함되는 방식
- **Route Tracking**: 실행 경로 추적, 전체 작업 흐름 기록

## 부록 B: 참고 자료

- OpenRouter API Docs: https://openrouter.ai/docs
- FastAPI Docs: https://fastapi.tiangolo.com
- Supabase Docs: https://supabase.com/docs
- AgentCPM-GUI: [관련 문서 링크]
