# 헬스장 소모품 신청 시스템

Streamlit 기반 헬스장 직원용 소모품 신청 및 관리 시스템

## 📋 프로젝트 정보

- **위치**: `/Users/chahyunseok/Documents/total/gym/1.물품신청받기`
- **GitHub**: https://github.com/gustjr0811-sys/gym-supplies-request
- **배포**: Streamlit Cloud
- **데이터베이스**: Supabase (PostgreSQL)

## 🛠 기술 스택

- **Frontend**: Streamlit 1.31.0+
- **Database**: Supabase (PostgreSQL)
- **Language**: Python 3.x
- **Deployment**: Streamlit Cloud

## ✨ 주요 기능

### 일반 사용자 (직원)
- 로그인 (username/password)
- 소모품 장바구니에 담기
- 품목별 수량, 가격, 옵션 입력
- 신청서 제출
- 본인 신청 내역 조회

### 관리자 (차현석)
- 모든 직원의 신청 내역 조회
- 다중 선택 후 일괄 다운로드
- 옵시디언 형식 .md 파일로 다운로드 (ZIP)

## 📁 프로젝트 구조

```
1.물품신청받기/
├── app.py                  # 메인 애플리케이션
├── requirements.txt        # Python 패키지 의존성
├── .gitignore             # Git 제외 파일 목록
├── start.command          # 로컬 실행 스크립트
├── stop.command           # 서버 종료 스크립트
├── .streamlit/
│   └── secrets.toml       # Supabase API 키 (Git 제외)
└── utils/
    ├── __init__.py
    ├── auth.py            # 인증 관련 (현재 미사용)
    └── database.py        # Supabase DB 함수들
```

## 🗄 데이터베이스 구조

### 테이블

1. **users** - 사용자 정보
   - username (PK)
   - password
   - name

2. **pending_cart** - 장바구니 (임시)
   - id (PK)
   - username
   - item_name, purchase_link, option_name
   - quantity, unit_price, total_price
   - added_date

3. **submitted_items** - 제출된 품목
   - id (PK)
   - username, batch_id
   - item_name, purchase_link, option_name
   - quantity, unit_price, total_price
   - submitted_date, status

4. **submission_summary** - 신청 요약
   - id (PK)
   - username, batch_id
   - item_count, total_amount
   - submitted_date

## 👥 사용자 정보

| Username | Password | Name   | Role  |
|----------|----------|--------|-------|
| 최영진    | 1111     | 최영진  | User  |
| 백지연    | 1111     | 백지연  | User  |
| 차현석    | 1111     | 차현석  | Admin |

**관리자 판단 로직**: `username == '차현석'` (app.py 코드에 하드코딩)

## 🚀 로컬 실행

```bash
# 1. 서버 시작
./start.command

# 또는
cd "/Users/chahyunseok/Documents/total/gym/1.물품신청받기"
.venv/bin/streamlit run app.py --server.port 9001

# 2. 브라우저 접속
http://localhost:9001
```

## 🌐 배포 정보

- **Streamlit Cloud**: 자동 배포 (GitHub push 시)
- **Secrets 설정**: Streamlit Cloud Dashboard → Settings → Secrets

```toml
[supabase]
url = "https://ueflrkvfhlftprptsplo.supabase.co"
key = "eyJhbG..."  # Supabase anon key
```

## 🔄 개발 워크플로우

### 코드 수정 시
```bash
# 1. 로컬에서 수정 및 테스트
./start.command

# 2. Git commit & push
git add .
git commit -m "설명"
git push

# 3. Streamlit Cloud 자동 재배포 (1-2분 소요)
```

### 데이터 관리
- **Supabase Dashboard**: https://supabase.com
- **SQL Editor**에서 데이터 조회/수정
- **Table Editor**에서 GUI로 데이터 관리

## 📥 다운로드 기능

관리자는 전체내역 탭에서:
- 여러 신청 선택 (체크박스)
- "선택한 항목 다운로드" 클릭
- ZIP 파일 다운로드 (품목별 .md 파일)

**파일 형식** (옵시디언용):
```markdown
---
품목명: 요가매트
신청자: 최영진
요청일: 2024-12-03
구매링크: https://...
옵션명: 퍼플 10mm
수량: 5
개당금액: 15000
신청일:
상태: 리스트업
---
```

## ⚠️ 중요 사항

1. **비밀번호 변경**: Supabase Table Editor에서 직접 수정
2. **관리자 변경**: app.py의 `is_admin` 로직 수정 필요
3. **테스트 데이터 삭제**:
   ```sql
   DELETE FROM submitted_items;
   DELETE FROM submission_summary;
   ```

## 🔧 문제 해결

### 배포 에러
- Streamlit Cloud → Manage app → Terminal 로그 확인
- requirements.txt 버전 확인

### 로컬 실행 에러
- `.venv` 삭제 후 재생성
- `pip install -r requirements.txt`

---

## 📝 다음 작업 시 안내

**새 대화 세션에서 이 프로젝트 작업 시:**

```
/Users/chahyunseok/Documents/total/gym/1.물품신청받기 README 읽고 시작
```

**모든 수정 후 README 파일을 최신 내용으로 업데이트해줘**
