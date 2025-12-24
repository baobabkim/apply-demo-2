# 데이터 스키마 문서

## 개요

이 프로젝트는 SQLite 데이터베이스를 사용하여 사용자 데이터, 행동 로그, A/B 테스트 결과를 저장합니다.

## 데이터베이스: app_data.db

### 테이블 구조

#### 1. users (사용자 정보)

사용자의 기본 정보와 가입 데이터를 저장합니다.

| 컬럼명 | 데이터 타입 | 제약조건 | 설명 |
|--------|------------|---------|------|
| user_id | INTEGER | PRIMARY KEY | 사용자 고유 ID |
| signup_date | TEXT | NOT NULL | 가입 날짜 (YYYY-MM-DD) |
| channel | TEXT | - | 유입 채널 (organic/paid/referral) |
| segment | TEXT | - | 초기 세그먼트 (high_potential/medium_potential/low_potential) |

**인덱스:** 없음 (PRIMARY KEY 자동 인덱싱)

**예시 데이터:**
```sql
user_id | signup_date | channel  | segment
--------|-------------|----------|------------------
1       | 2024-11-15  | organic  | high_potential
2       | 2024-11-20  | paid     | medium_potential
3       | 2024-12-01  | referral | low_potential
```

#### 2. user_logs (사용자 행동 로그)

사용자의 모든 행동 이벤트를 기록합니다.

| 컬럼명 | 데이터 타입 | 제약조건 | 설명 |
|--------|------------|---------|------|
| log_id | INTEGER | PRIMARY KEY AUTOINCREMENT | 로그 고유 ID |
| user_id | INTEGER | NOT NULL, FOREIGN KEY | 사용자 ID (users.user_id 참조) |
| event_name | TEXT | NOT NULL | 이벤트 타입 |
| event_timestamp | TEXT | NOT NULL | 이벤트 발생 시각 (ISO 8601) |
| value | REAL | - | 이벤트 값 (보상 금액 등) |

**이벤트 타입:**
- `app_open`: 앱 실행
- `reward_earned`: 보상 획득
- `activity_completed`: 활동 완료
- `app_close`: 앱 종료

**인덱스:**
- `idx_user_logs_user_id` ON user_id
- `idx_user_logs_event_name` ON event_name
- `idx_user_logs_timestamp` ON event_timestamp

**예시 데이터:**
```sql
log_id | user_id | event_name        | event_timestamp          | value
-------|---------|-------------------|--------------------------|-------
1      | 1       | app_open          | 2024-11-15T09:30:00     | NULL
2      | 1       | reward_earned     | 2024-11-15T09:45:00     | 25.50
3      | 1       | activity_completed| 2024-11-15T10:00:00     | NULL
```

#### 3. ab_test_results (A/B 테스트 결과)

A/B 테스트 그룹 할당 및 전환 데이터를 저장합니다.

| 컬럼명 | 데이터 타입 | 제약조건 | 설명 |
|--------|------------|---------|------|
| user_id | INTEGER | PRIMARY KEY, FOREIGN KEY | 사용자 ID (users.user_id 참조) |
| group_name | TEXT | NOT NULL | 테스트 그룹 (A/B) |
| is_converted | INTEGER | NOT NULL | 전환 여부 (0/1) |
| conversion_timestamp | TEXT | - | 전환 시각 (ISO 8601) |

**인덱스:**
- `idx_ab_test_group` ON group_name

**예시 데이터:**
```sql
user_id | group_name | is_converted | conversion_timestamp
--------|------------|--------------|---------------------
1       | A          | 1            | 2024-11-16T14:30:00
2       | B          | 0            | NULL
3       | A          | 1            | 2024-12-02T11:15:00
```

## 데이터 관계도

```
users (1) ----< (N) user_logs
  |
  |
  +------------< (1) ab_test_results
```

## 데이터 생성 통계

### users 테이블
- **총 레코드 수**: 10,000
- **가입 기간**: 최근 60일
- **채널 분포**: organic (50%), paid (30%), referral (20%)
- **세그먼트 분포**: high (30%), medium (50%), low (20%)

### user_logs 테이블
- **총 레코드 수**: ~746,632
- **사용자당 평균 이벤트**: ~75
- **이벤트 타입 분포**: app_open (30%), reward_earned (10%), activity_completed (40%), app_close (20%)
- **보상 금액 분포**: 로그정규분포 (평균 ~20)

### ab_test_results 테이블
- **총 레코드 수**: 10,000
- **그룹 분포**: A (50%), B (50%)
- **전환율**: A (~18.5%), B (~19.8%)

## 쿼리 예시

### 1. D7 리텐션 계산
```sql
WITH user_signup AS (
    SELECT user_id, signup_date
    FROM users
),
user_activity AS (
    SELECT DISTINCT 
        user_id,
        DATE(event_timestamp) as activity_date
    FROM user_logs
)
SELECT 
    COUNT(DISTINCT us.user_id) as total_users,
    COUNT(DISTINCT CASE 
        WHEN DATE(ua.activity_date) = DATE(us.signup_date, '+7 days')
        THEN us.user_id 
    END) as d7_retained
FROM user_signup us
LEFT JOIN user_activity ua ON us.user_id = ua.user_id
WHERE DATE(us.signup_date, '+7 days') <= DATE('now');
```

### 2. A/B 테스트 전환율
```sql
SELECT 
    group_name,
    COUNT(*) as total_users,
    SUM(is_converted) as conversions,
    ROUND(CAST(SUM(is_converted) AS FLOAT) / COUNT(*) * 100, 2) as conversion_rate
FROM ab_test_results
GROUP BY group_name;
```

### 3. 사용자별 행동 통계
```sql
SELECT 
    u.user_id,
    u.segment,
    COUNT(ul.log_id) as total_events,
    COUNT(DISTINCT DATE(ul.event_timestamp)) as active_days,
    SUM(CASE WHEN ul.event_name = 'reward_earned' THEN 1 ELSE 0 END) as reward_count,
    SUM(CASE WHEN ul.event_name = 'reward_earned' THEN ul.value ELSE 0 END) as total_reward_value
FROM users u
LEFT JOIN user_logs ul ON u.user_id = ul.user_id
GROUP BY u.user_id;
```

## 데이터 무결성

### Foreign Key 제약조건
- `user_logs.user_id` → `users.user_id`
- `ab_test_results.user_id` → `users.user_id`

### 데이터 검증
- 모든 user_id는 users 테이블에 존재
- event_timestamp는 signup_date 이후
- is_converted는 0 또는 1
- conversion_timestamp는 is_converted=1일 때만 존재
