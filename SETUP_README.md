# QQQ/QLD/TQQQ 백테스트 — 자동 데이터 갱신 파이프라인 설치 가이드

## 1. 이 zip 안에 든 파일들

| 파일 | 역할 |
|---|---|
| `index.html` | 기존 백테스트 도구. `const PRICE = {...}` 하드코딩을 제거하고, 로드 시 `price_data.json`을 `fetch`로 불러오도록 수정됨 |
| `price_data.json` | 가격 데이터 (2000-01-03 ~ 2026-08-06, QQQ/QLD/TQQQ 종가) |
| `update_price_data.py` | `yfinance`로 최신 종가를 받아 `price_data.json` 뒤에 이어붙이는 스크립트 |
| `requirements.txt` | 위 스크립트 실행에 필요한 파이썬 패키지 |
| `.github/workflows/update-data.yml` | 매일 자동으로 스크립트를 실행하고 결과를 커밋/푸시하는 GitHub Actions 워크플로 |

## 2. 저장소에 올리는 방법

기존 저장소(`simgiwon/QQQ-200SMA-Simulation`)에 이 5개 파일 + `.github/workflows/` 폴더를 **같은 폴더 구조 그대로** 올리면 됩니다.

- 웹에서 하는 방법: 저장소 페이지 → `Add file` → `Upload files` → 이 zip을 풀어서 나온 파일들을 통째로 드래그 앤 드롭 (폴더 구조 유지됨) → `Commit changes`
- 기존에 있던 `index.html`(하드코딩 버전)은 **덮어써도 됩니다** — 새 버전이 완전히 대체합니다.

## 3. GitHub Actions가 자동으로 커밋하려면 권한 설정이 필요합니다

1. 저장소 → **Settings** → **Actions** → **General**
2. 아래로 스크롤해서 **Workflow permissions**
3. **"Read and write permissions"** 선택 → **Save**

(기본값이 "Read repository contents permission"으로 되어있으면 Actions가 커밋/푸시를 못 하고 실패합니다.)

## 4. 확인하는 방법

1. 저장소 → **Actions** 탭 → 왼쪽에 `Update QQQ/QLD/TQQQ price data` 워크플로가 보이면 정상 인식된 것
2. 매일 아침 자동 실행을 기다리기 싫으면, 해당 워크플로 클릭 → 오른쪽 **Run workflow** 버튼으로 즉시 1회 수동 실행 가능
3. 실행 로그에서 `N일치 데이터 추가 완료` 메시지가 뜨고, 저장소에 `price_data.json`이 변경된 커밋이 생기면 성공
4. `https://simgiwon.github.io/QQQ-200SMA-Simulation/` 를 새로고침해서 종료일 기본값이 오늘 날짜 근처로 잡히는지 확인

## 5. 스케줄 및 이후 커스터마이징

- 기본 스케줄: 평일(월~금) UTC 21:30 = 한국시간 익일 06:30 (미국 정규장 마감 이후)
- 바꾸고 싶으면 `.github/workflows/update-data.yml`의 `cron: "30 21 * * 1-5"` 부분을 수정
- 크론 표현식은 UTC 기준입니다 (분 시 일 월 요일)

## 6. 알아둘 점 (한계)

- **무료 데이터라 실시간은 아닙니다.** yfinance는 장 마감 후 EOD(일봉) 데이터 기준이고, 매일 새벽 1회 갱신되는 구조입니다. 장중 실시간 시세는 이 구조로는 못 잡습니다 (실시간을 원하면 유료 API + 서버가 필요해요).
- yfinance는 야후 파이낸스의 비공식 라이브러리라 야후 쪽 사정으로 가끔 응답이 실패할 수 있습니다. 실패하면 그날은 건너뛰고 다음날 자동으로 재시도됩니다 (기존 데이터는 안전하게 보존됨 — 스크립트가 항상 마지막 날짜 다음부터만 추가하도록 짜여 있습니다).
- 로컬에서 `index.html`을 더블클릭해서 열면 **작동 안 합니다** (`file://`는 CORS로 fetch가 막힘). 반드시 GitHub Pages 같은 `https://` 환경에서 열어야 합니다.
