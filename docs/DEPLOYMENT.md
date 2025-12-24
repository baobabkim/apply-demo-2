# Streamlit Cloud 배포 가이드

## 자동 배포 설정

이 프로젝트는 Streamlit Community Cloud에 배포할 준비가 완료되었습니다.

### 1단계: Streamlit Cloud 계정 생성

1. https://streamlit.io/cloud 방문
2. GitHub 계정으로 로그인
3. 무료 Community Cloud 티어 선택

### 2단계: 앱 배포

1. Streamlit Cloud 대시보드에서 "New app" 클릭
2. 다음 정보 입력:
   - **Repository**: `baobabkim/apply-demo-2`
   - **Branch**: `main`
   - **Main file path**: `src/dashboard/app.py`
   - **App URL**: `apply-demo-2` (또는 원하는 이름)

3. "Deploy!" 클릭

### 3단계: 배포 완료

- 배포는 약 2-3분 소요
- 완료 후 URL: `https://apply-demo-2.streamlit.app`
- GitHub에 푸시할 때마다 자동으로 재배포됨

## 배포 파일 설명

### `.streamlit/config.toml`
Streamlit 앱의 테마 및 서버 설정을 정의합니다.

### `requirements.txt`
Python 패키지 의존성을 명시합니다. Streamlit Cloud가 자동으로 설치합니다.

### `runtime.txt`
Python 버전을 지정합니다 (Python 3.12.0).

## 주의사항

### 데이터 파일
- `data/` 디렉토리의 파일들은 `.gitignore`에 포함되어 있습니다
- 배포된 앱은 분석 결과 JSON 파일이 필요합니다
- 현재는 로컬에서 생성된 분석 결과를 사용합니다

### 해결 방법
1. 분석 결과 파일을 Git에 포함시키기 (`.gitignore` 수정)
2. 또는 앱 시작 시 자동으로 데이터 생성하도록 수정

## 현재 상태

✅ 배포 설정 파일 생성 완료
✅ README 업데이트 완료
✅ GitHub 푸시 완료
⏳ Streamlit Cloud에서 수동 배포 필요

## 다음 단계

1. https://streamlit.io/cloud 에서 앱 배포
2. 배포 완료 후 URL 확인
3. 대시보드 정상 작동 확인
