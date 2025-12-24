# Product Requirements Document (PRD)

## 프로젝트명: 로컬 환경 기반 사용자 행동 데이터 분석 및 실험 설계 MVP

**버전:** 1.0  
**작성일:** 2025-12-24  
**작성자:** Data Analyst  

---

## 1. 프로젝트 개요 (Executive Summary)

### 1.1 목적 (Purpose)
본 프로젝트는 데이터 분석가로서 비즈니스 문제를 정의하고, 가상의 로그 데이터를 생성하여 통계적 가설 검정 및 리텐션 분석을 수행하는 전체 과정을 로컬 환경에서 구현합니다. 대학원 수준의 분석 방법론을 실무적인 대시보드 형태로 시각화하여 데이터 분석가의 핵심 역량을 증명하는 것을 목표로 합니다.

### 1.2 배경 (Background)
- 별도의 비용이나 서버 구축 없이 로컬 환경에서 즉시 실행 가능한 MVP 형태
- 대학원생으로서의 분석적 전문성을 실무 프로젝트로 구현
- 데이터 생성부터 분석, 시각화까지의 End-to-End 파이프라인 구축

### 1.3 범위 (Scope)
- **In Scope:**
  - 가상 유저 및 로그 데이터 생성
  - SQLite 기반 데이터 저장 및 관리
  - 리텐션 분석 및 코호트 분석
  - A/B 테스트 통계적 검정
  - 유저 세그먼트 분석
  - Streamlit 기반 통합 대시보드
  
- **Out of Scope:**
  - 실제 프로덕션 환경 배포
  - 클라우드 인프라 구축
  - 실시간 데이터 처리
  - 외부 API 연동

---

## 2. 문제 정의 및 가설 (Problem Statement & Hypothesis)

### 2.1 비즈니스 문제
특정 건강 관리 앱에서 유저의 초기 이탈률이 높고, 보상 획득 경험이 리텐션에 미치는 영향이 불분명함.

### 2.2 분석 가설
**가설 1 (리텐션 분석):**  
가입 후 24시간 이내에 보상을 1회 이상 획득한 유저는 그렇지 않은 유저보다 7일 차 리텐션이 유의미하게 높을 것이다.

**가설 2 (A/B 테스트):**  
보상 획득을 독려하는 개인화 푸시 알림을 발송할 경우, 대조군 대비 보상 전환율이 10% 이상 상승할 것이다.

---

## 3. 기술 스택 (Technical Stack)

### 3.1 핵심 기술
| 구분 | 기술 | 선정 이유 |
|------|------|-----------|
| **데이터 저장소** | SQLite | 별도 설치 없는 파일 기반 DB, 비용 무료 |
| **분석 엔진** | Python (Pandas, NumPy, SciPy, Statsmodels) | 통계 분석 및 데이터 처리의 표준 도구 |
| **시각화 및 배포** | Streamlit | 로컬 웹 대시보드 구축, 빠른 프로토타이핑 |
| **버전 관리** | GitHub | 분석 코드 및 결과물 관리 |
| **클러스터링** | Scikit-learn | 유저 세그먼트 분석 |

### 3.2 개발 환경
- Python 3.8 이상
- 로컬 개발 환경 (별도 서버 불필요)
- Git/GitHub를 통한 버전 관리

---

## 4. 핵심 기능 (Core Features)

### 4.1 기능 목록

| 기능 | 설명 | 우선순위 | 비고 |
|------|------|----------|------|
| **데이터 생성** | Python을 활용한 유저 로그(가입, 행동, 실험) 합성 데이터 생성 | P0 | 대학원 수준의 분포 설계 적용 |
| **리텐션 분석** | SQL 쿼리 기반의 코호트 분석 및 리텐션 커브 시각화 | P0 | SQLite 활용 |
| **실험 검정** | A/B 테스트 결과의 통계적 유의성 검정 (P-value, Effect Size) | P0 | SciPy/Statsmodels 활용 |
| **세그먼트 분석** | 행동 패턴 기반의 유저 클러스터링 및 그룹별 특징 추출 | P1 | Scikit-learn 활용 |
| **통합 대시보드** | 위 모든 결과를 한눈에 확인 가능한 로컬 웹 페이지 | P0 | Streamlit 활용 |

### 4.2 기능별 상세 요구사항

#### 4.2.1 데이터 생성 모듈
- 가상 유저 생성 (최소 10,000명 이상)
- 유저별 행동 로그 생성 (가입, 보상 획득, 앱 사용 등)
- A/B 테스트 그룹 할당 및 전환 데이터 생성
- 통계적으로 의미 있는 분포 설계 (정규분포, 포아송분포 등)

#### 4.2.2 리텐션 분석 모듈
- 일별 리텐션 계산 (D1, D3, D7, D14, D30)
- 코호트별 리텐션 커브 시각화
- 보상 획득 여부에 따른 리텐션 비교
- SQL 쿼리 기반 분석 로직

#### 4.2.3 A/B 테스트 검정 모듈
- 실험군/대조군 간 전환율 비교
- 통계적 유의성 검정 (t-test, chi-square test)
- P-value, Effect Size, 신뢰구간 계산
- 통계적 검정력(Power) 분석

#### 4.2.4 세그먼트 분석 모듈
- K-means 클러스터링을 통한 유저 그룹화
- 세그먼트별 행동 패턴 분석
- 이질적 처치 효과(HTE) 분석

#### 4.2.5 통합 대시보드
- 주요 지표 요약 (KPI Dashboard)
- 리텐션 커브 시각화
- A/B 테스트 결과 시각화
- 세그먼트별 분석 결과 시각화
- 인터랙티브 필터링 기능

---

## 5. 데이터 스키마 (Data Schema)

### 5.1 SQLite 데이터베이스 구조

#### 5.1.1 users 테이블
```sql
CREATE TABLE users (
    user_id INTEGER PRIMARY KEY,
    signup_date TEXT NOT NULL,
    channel TEXT,
    segment TEXT
);
```

| 컬럼명 | 타입 | 설명 |
|--------|------|------|
| user_id | INTEGER | 유저 고유 ID (Primary Key) |
| signup_date | TEXT | 가입 날짜 (ISO 8601 형식) |
| channel | TEXT | 유입 채널 (organic, paid, referral 등) |
| segment | TEXT | 유저 세그먼트 (초기 분류) |

#### 5.1.2 user_logs 테이블
```sql
CREATE TABLE user_logs (
    log_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    event_name TEXT NOT NULL,
    event_timestamp TEXT NOT NULL,
    value REAL,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);
```

| 컬럼명 | 타입 | 설명 |
|--------|------|------|
| log_id | INTEGER | 로그 고유 ID (Primary Key) |
| user_id | INTEGER | 유저 ID (Foreign Key) |
| event_name | TEXT | 이벤트 명 (reward_earned, app_open 등) |
| event_timestamp | TEXT | 이벤트 발생 시각 (ISO 8601 형식) |
| value | REAL | 이벤트 관련 값 (보상 금액 등) |

#### 5.1.3 ab_test_results 테이블
```sql
CREATE TABLE ab_test_results (
    user_id INTEGER PRIMARY KEY,
    group_name TEXT NOT NULL,
    is_converted INTEGER NOT NULL,
    conversion_timestamp TEXT,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);
```

| 컬럼명 | 타입 | 설명 |
|--------|------|------|
| user_id | INTEGER | 유저 ID (Primary Key, Foreign Key) |
| group_name | TEXT | 실험 그룹 (A: 대조군, B: 실험군) |
| is_converted | INTEGER | 전환 여부 (0: 미전환, 1: 전환) |
| conversion_timestamp | TEXT | 전환 발생 시각 |

---

## 6. 분석 방법론 (Methodology)

### 6.1 통계적 분석 기법

#### 6.1.1 리텐션 분석
- **코호트 분석:** 가입 날짜별 유저 그룹의 리텐션 추이 분석
- **생존 분석:** Kaplan-Meier 곡선을 통한 유저 생존율 분석

#### 6.1.2 A/B 테스트 검정
- **가설 검정:**
  - 귀무가설(H0): 실험군과 대조군의 전환율에 차이가 없다
  - 대립가설(H1): 실험군의 전환율이 대조군보다 높다
- **검정 방법:**
  - 비율 검정 (Two-proportion z-test)
  - 카이제곱 검정 (Chi-square test)
- **효과 크기:** Cohen's h, Relative Lift
- **신뢰구간:** 95% 신뢰구간 계산

#### 6.1.3 인과추론 기법
- **성향 점수 매칭(PSM):** 교란 변수를 통제하기 위한 매칭 기법 적용 가능성 검토
- **이질적 처치 효과(HTE):** 유저 세그먼트별로 실험 효과가 다르게 나타나는지 분석

#### 6.1.4 클러스터링
- **K-means 클러스터링:** 유저 행동 패턴 기반 세그먼트 생성
- **최적 클러스터 수 결정:** Elbow Method, Silhouette Score

### 6.2 분석 깊이
- 단순 평균 비교를 넘어, 교란 변수를 통제하기 위한 고급 통계 기법 적용
- 실험 결과 해석 시 신뢰 구간(Confidence Interval)과 통계적 검정력(Power) 분석 포함
- 유저 세그먼트별 실험 효과 차이 분석

---

## 7. 성공 지표 (Success Metrics)

### 7.1 Primary Metrics
| 지표 | 목표 | 측정 방법 |
|------|------|-----------|
| **7일 차 리텐션** | 보상 획득 유저 > 미획득 유저 (통계적 유의성) | SQL 쿼리 + 통계 검정 |
| **A/B 테스트 전환율 차이** | 실험군 전환율 - 대조군 전환율 ≥ 10%p | 비율 검정 |
| **통계적 유의성** | P-value < 0.05 | SciPy/Statsmodels |

### 7.2 Technical Metrics
| 지표 | 목표 | 측정 방법 |
|------|------|-----------|
| **파이프라인 자동화** | 데이터 생성부터 시각화까지 자동화 | 스크립트 실행 성공 여부 |
| **코드 품질** | 모듈화, 재사용성, 문서화 | 코드 리뷰 |
| **대시보드 로딩 시간** | < 5초 | Streamlit 성능 측정 |

### 7.3 Product Metrics
| 지표 | 목표 | 측정 방법 |
|------|------|-----------|
| **비즈니스 액션 아이템** | 분석 인사이트로부터 도출된 구체적인 액션 아이템 3가지 이상 | 대시보드 인사이트 섹션 |

---

## 8. 구현 계획 (Implementation Plan)

### 8.1 Phase 1: 데이터 생성 및 저장 (Week 1)
- [ ] 가상 유저 데이터 생성 스크립트 작성
- [ ] 유저 행동 로그 생성 스크립트 작성
- [ ] A/B 테스트 데이터 생성 스크립트 작성
- [ ] SQLite 데이터베이스 생성 및 데이터 적재

### 8.2 Phase 2: 분석 모듈 개발 (Week 2)
- [ ] 리텐션 분석 SQL 쿼리 작성
- [ ] A/B 테스트 통계 검정 스크립트 작성
- [ ] 세그먼트 분석 (클러스터링) 스크립트 작성
- [ ] 분석 결과 저장 및 관리

### 8.3 Phase 3: 대시보드 개발 (Week 3)
- [ ] Streamlit 대시보드 기본 골격 작성
- [ ] 리텐션 커브 시각화
- [ ] A/B 테스트 결과 시각화
- [ ] 세그먼트 분석 결과 시각화
- [ ] 인터랙티브 필터링 기능 추가

### 8.4 Phase 4: 검증 및 문서화 (Week 4)
- [ ] 분석 결과 검증 및 통계적 타당성 확인
- [ ] 비즈니스 인사이트 도출
- [ ] 코드 문서화 및 README 작성
- [ ] GitHub 리포지토리 정리

---

## 9. 리스크 및 제약사항 (Risks & Constraints)

### 9.1 리스크
| 리스크 | 영향도 | 완화 방안 |
|--------|--------|-----------|
| 데이터 생성 로직의 비현실성 | Medium | 실제 비즈니스 데이터 분포 참고, 도메인 전문가 자문 |
| 통계적 검정력 부족 | Medium | 충분한 샘플 사이즈 확보 (최소 10,000명) |
| 대시보드 성능 이슈 | Low | 데이터 캐싱, 쿼리 최적화 |

### 9.2 제약사항
- 로컬 환경에서만 실행 (프로덕션 배포 불가)
- 가상 데이터 사용 (실제 유저 데이터 아님)
- 실시간 데이터 처리 미지원
- 비용 제약으로 인한 클라우드 인프라 미사용

---

## 10. 비즈니스 액션 아이템 (Business Action Items)

분석 결과를 바탕으로 도출 예상되는 액션 아이템:

1. **보상 획득 경험 최적화**
   - 가입 후 24시간 이내 보상 획득을 독려하는 온보딩 플로우 개선
   - 첫 보상 획득까지의 장벽 낮추기 (난이도 조정, 튜토리얼 개선)

2. **개인화 푸시 알림 전략**
   - A/B 테스트 결과가 유의미할 경우, 개인화 푸시 알림 전면 도입
   - 세그먼트별 최적 메시지 및 발송 타이밍 설계

3. **고위험 이탈 유저 타겟팅**
   - 세그먼트 분석 결과를 바탕으로 이탈 위험이 높은 유저 그룹 식별
   - 해당 그룹 대상 맞춤형 리텐션 캠페인 실행

---

## 11. 다음 단계 (Next Steps)

1. **데이터 생성 스크립트 작성**
   - 가상 유저와 로그 데이터를 생성하는 Python 스크립트 작성

2. **데이터베이스 구축**
   - SQLite DB에 데이터를 적재하고 리텐션을 계산하는 SQL 쿼리 작성

3. **대시보드 프로토타입**
   - 분석 결과를 보여주는 Streamlit 대시보드 기본 골격 코드 작성

---

## 12. 참고 자료 (References)

- [Streamlit Documentation](https://docs.streamlit.io/)
- [SQLite Documentation](https://www.sqlite.org/docs.html)
- [SciPy Statistical Functions](https://docs.scipy.org/doc/scipy/reference/stats.html)
- [Statsmodels Documentation](https://www.statsmodels.org/stable/index.html)
- [Scikit-learn Clustering](https://scikit-learn.org/stable/modules/clustering.html)

---

**문서 버전 히스토리**
- v1.0 (2025-12-24): 초안 작성
