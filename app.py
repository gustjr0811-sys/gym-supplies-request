import streamlit as st
import pandas as pd
from datetime import datetime
import io
import zipfile
from utils.database import (
    login,
    logout,
    load_pending_cart,
    add_to_pending_cart,
    remove_from_pending_cart,
    submit_cart,
    get_submission_history,
    get_all_submission_history
)

st.set_page_config(
    page_title="헬스장 팀 업무",
    page_icon="📦",
    layout="wide"
)

# Streamlit UI 요소 숨기기
st.markdown("""
    <style>
        /* 상단 헤더 전체 숨김 */
        header[data-testid="stHeader"] {
            display: none !important;
        }

        /* 하단 푸터 숨김 */
        footer {
            display: none !important;
        }

        /* Streamlit 메뉴 버튼 숨김 */
        #MainMenu {
            display: none !important;
        }

        /* 하단 "Made with Streamlit" 숨김 */
        footer:after {
            display: none !important;
        }

        /* 상단 toolbar 전체 숨김 */
        div[data-testid="stToolbar"] {
            display: none !important;
        }

        /* 우측 상단 배포 버튼들 숨김 */
        div[data-testid="stDecoration"] {
            display: none !important;
        }

        /* Fork, GitHub 아이콘 등 숨김 */
        .viewerBadge_container__1QSob {
            display: none !important;
        }

        /* 우측 하단 아이콘들 숨김 */
        .styles_viewerBadge__1yB5_ {
            display: none !important;
        }

        /* 하단 우측 모든 배지 숨김 (Streamlit 아이콘, 왕관 등) */
        div[data-testid="stStatusWidget"] {
            display: none !important;
        }

        /* 모든 iframe 배지 숨김 */
        iframe[title="streamlit_app"] {
            display: none !important;
        }

        /* 우측 하단 고정 배지들 숨김 */
        .stApp > footer,
        .stApp > div > div > div > div > footer {
            display: none !important;
        }

        /* Streamlit Community Cloud 배지 숨김 */
        [data-testid="stCommunityCloudBadge"] {
            display: none !important;
        }

        /* 추가 배지 타겟팅 */
        button[kind="header"],
        a[href*="streamlit.io"],
        div[class*="viewerBadge"],
        div[class*="StatusWidget"] {
            display: none !important;
        }

        /* 우측 하단 고정 위치 요소 모두 숨김 (가장 강력한 방법) */
        div[style*="position: fixed"][style*="bottom"],
        div[style*="position: fixed"][style*="right"],
        div[style*="position: fixed"][style*="bottom"][style*="right"] {
            display: none !important;
        }

        /* z-index 높은 하단 요소들 숨김 */
        div[style*="z-index"][style*="bottom"] {
            display: none !important;
        }

        /* 모든 하단 우측 절대/고정 위치 요소 */
        [style*="position: absolute; bottom"][style*="right"],
        [style*="position: fixed; bottom"][style*="right"] {
            display: none !important;
        }

        /* Streamlit의 동적 클래스명 모두 타겟 */
        div[class*="viewerBadge"],
        div[class*="ViewerBadge"],
        div[class*="badge"],
        div[class*="Badge"] {
            display: none !important;
            visibility: hidden !important;
            opacity: 0 !important;
        }
    </style>
""", unsafe_allow_html=True)

# 세션 상태 초기화
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'username' not in st.session_state:
    st.session_state.username = None
if 'name' not in st.session_state:
    st.session_state.name = None

def main():
    # 로그인 체크
    if not st.session_state.logged_in:
        show_login_page()
    else:
        show_main_page()

def show_login_page():
    # 중앙 정렬을 위한 여백
    st.markdown("<br>" * 3, unsafe_allow_html=True)

    # 타이틀
    st.markdown("<h1 style='text-align: center; color: #333; margin-bottom: 40px;'>헬스장 업무</h1>", unsafe_allow_html=True)

    # 로그인 카드
    col1, col2, col3 = st.columns([2, 1, 2])

    with col2:
        st.markdown("""
            <style>
            .stTextInput > div > div > input {
                background-color: white !important;
                color: black !important;
            }
            .stButton > button {
                background-color: #FF8C00 !important;
                color: white !important;
                border: none !important;
            }
            .stButton > button:hover {
                background-color: #FF7F00 !important;
            }
            </style>
        """, unsafe_allow_html=True)

        st.markdown("<h3 style='text-align: center; margin-bottom: 30px; color: #333;'>로그인</h3>", unsafe_allow_html=True)

        with st.form("login_form"):
            username = st.text_input("아이디", key="login_username", placeholder="아이디를 입력하세요")
            password = st.text_input("비밀번호", type="password", key="login_password", placeholder="비밀번호를 입력하세요")

            st.markdown("<br>", unsafe_allow_html=True)

            submitted = st.form_submit_button("로그인", use_container_width=True)

            if submitted:
                result = login(username, password)
                if result['success']:
                    st.session_state.logged_in = True
                    st.session_state.username = username
                    st.session_state.name = result['name']
                    st.rerun()
                else:
                    st.error(result['message'])

def show_main_page():
    # 페이지 너비 설정: 최대 1280px 또는 화면의 2/3
    st.markdown("""
        <style>
        .main .block-container {
            max-width: min(1280px, 66.67vw);
            padding-left: 2rem;
            padding-right: 2rem;
        }
        </style>
    """, unsafe_allow_html=True)

    # 헤더
    st.title(f"소모품 신청")
    st.caption(f"안녕하세요, {st.session_state.name}님")

    # 관리자 여부 확인
    is_admin = (st.session_state.username == '차현석')

    # 탭 생성 (관리자는 3개, 일반 사용자는 2개)
    if is_admin:
        tab1, tab2, tab3 = st.tabs(["📝 신청", "📜 내역", "📋 전체내역"])
    else:
        tab1, tab2 = st.tabs(["📝 신청", "📜 내역"])

    with tab1:
        show_request_tab()

    with tab2:
        show_history_tab()

    if is_admin:
        with tab3:
            show_all_history_tab()

def show_request_tab():
    # 버튼 색상 스타일
    st.markdown("""
        <style>
        div[data-testid="stForm"] button[kind="primary"],
        div.stButton > button[kind="primary"] {
            background-color: #FF8C00 !important;
            color: white !important;
            border: none !important;
        }
        div[data-testid="stForm"] button[kind="primary"]:hover,
        div.stButton > button[kind="primary"]:hover {
            background-color: #FF7F00 !important;
        }
        </style>
    """, unsafe_allow_html=True)

    # 입력 폼
    with st.form("add_item_form", clear_on_submit=True):
        st.markdown("### 품목 정보 입력")

        col1, col2, col3, col4, col5 = st.columns(5)

        with col1:
            item_name = st.text_input("이름", placeholder="예: 요가매트")

        with col2:
            purchase_link = st.text_input("링크", placeholder="https://...")

        with col3:
            option_name = st.text_input("옵션명(정확하게)", placeholder="예: 퍼플, 10mm")

        with col4:
            quantity_text = st.text_input("총수량", placeholder="예: 5")

        with col5:
            unit_price_text = st.text_input("1개당 금액(배송비제외)", placeholder="예: 15,000")

        submitted = st.form_submit_button("➕ 담기", use_container_width=True)

        if submitted:
            if not item_name or not purchase_link or not quantity_text or not unit_price_text:
                st.error("필수 항목을 모두 입력해주세요.")
            else:
                try:
                    # 콤마 제거 및 숫자 변환
                    quantity = int(quantity_text.replace(',', '').strip())
                    unit_price = int(unit_price_text.replace(',', '').strip())
                    total_price = quantity * unit_price

                    result = add_to_pending_cart(
                        st.session_state.username,
                        item_name,
                        purchase_link,
                        option_name,
                        quantity,
                        unit_price,
                        total_price
                    )
                    if result['success']:
                        st.success("✅ 장바구니에 담았습니다!")
                        st.rerun()
                    else:
                        st.error(result['message'])
                except ValueError:
                    st.error("수량과 금액은 숫자만 입력해주세요.")

    st.markdown("---")

    # 담긴 품목
    cart_items = load_pending_cart(st.session_state.username)

    if cart_items:
        st.markdown(f"### 담긴 품목 ({len(cart_items)}개)")

        # 헤더
        col1, col2, col3, col4, col5, col6, col7, col8 = st.columns([0.5, 1.5, 1.5, 1, 0.8, 1, 1, 0.3])
        with col1:
            st.markdown("**No**")
        with col2:
            st.markdown("**이름**")
        with col3:
            st.markdown("**링크**")
        with col4:
            st.markdown("**옵션**")
        with col5:
            st.markdown("**수량**")
        with col6:
            st.markdown("**개당금액**")
        with col7:
            st.markdown("**총금액**")
        with col8:
            st.markdown("**삭제**")

        st.markdown("---")

        total_amount = 0

        # 품목 행
        for idx, item in enumerate(cart_items):
            col1, col2, col3, col4, col5, col6, col7, col8 = st.columns([0.5, 1.5, 1.5, 1, 0.8, 1, 1, 0.3])

            with col1:
                st.write(f"{idx + 1}")
            with col2:
                st.write(item['item_name'])
            with col3:
                st.write(item['purchase_link'][:30] + "..." if len(item['purchase_link']) > 30 else item['purchase_link'])
            with col4:
                st.write(item['option_name'] if item['option_name'] else "-")
            with col5:
                st.write(f"{item['quantity']}개")
            with col6:
                st.write(f"{item['unit_price']:,}원")
            with col7:
                st.write(f"{item['total_price']:,}원")
            with col8:
                if st.button("삭제", key=f"delete_{idx}", use_container_width=True):
                    remove_from_pending_cart(st.session_state.username, idx)
                    st.rerun()

            total_amount += item['total_price']

            # 행 구분선
            st.markdown("---")

        col1, col2, col3, col4 = st.columns([2, 2, 1, 1])

        with col1:
            st.markdown(f"**총 품목 수:** {len(cart_items)}개")

        with col2:
            st.markdown(f"**총 금액:** {total_amount:,}원")

        with col3:
            if st.button("전체 삭제", use_container_width=True):
                for i in range(len(cart_items)):
                    remove_from_pending_cart(st.session_state.username, 0)
                st.rerun()

        with col4:
            if st.button("신청하기", type="primary", use_container_width=True):
                with st.spinner("신청 처리 중..."):
                    result = submit_cart(st.session_state.username, cart_items)
                    if result['success']:
                        st.success("✅ 신청이 완료되었습니다!")
                        st.rerun()
                    else:
                        st.error(result['message'])
    else:
        st.info("추가된 품목이 없습니다. 위에서 품목을 추가해주세요.")

def show_history_tab():
    st.subheader("신청 내역")

    history = get_submission_history(st.session_state.username)

    # Accordion 상태 초기화 (첫 번째 항목이 기본으로 열림)
    if 'expanded_idx' not in st.session_state:
        st.session_state.expanded_idx = 0

    if history:
        for idx, submission in enumerate(history):
            submit_date = submission['submitted_date'].split()[0]  # 날짜만 추출 (시간 제거)

            is_expanded = (idx == st.session_state.expanded_idx)

            # 토글 버튼
            if st.button(f"{'▼' if is_expanded else '▶'} {submit_date}", key=f"btn_{idx}", use_container_width=True):
                st.session_state.expanded_idx = idx
                st.rerun()

            # 선택된 항목만 내용 표시
            if is_expanded:
                # DataFrame 생성
                items_data = []
                for item_idx, item in enumerate(submission['items'], 1):
                    items_data.append({
                        'No': str(item_idx),
                        '이름': item['item_name'],
                        '링크': item['purchase_link'],
                        '옵션': item['option_name'] if item['option_name'] else '-',
                        '수량': f"{item['quantity']}개",
                        '1개당 금액': f"{item['unit_price']:,}원",
                        '총금액': f"{item['total_price']:,}원"
                    })

                df = pd.DataFrame(items_data)
                st.dataframe(df, use_container_width=True, hide_index=True)

                st.markdown("")  # 여백

                # 품목 수와 총 금액
                col1, col2, col3 = st.columns([2, 1, 1])
                with col1:
                    st.write("")  # 빈 공간
                with col2:
                    st.markdown(f"**품목 수:** {submission['item_count']}개")
                with col3:
                    st.markdown(f"**총 금액:** {submission['total_amount']:,}원")

                st.markdown("")  # 여백
    else:
        st.info("아직 신청 내역이 없습니다.")

def show_all_history_tab():
    st.subheader("전체 신청 내역 (관리자)")

    history = get_all_submission_history()

    # 상태 초기화
    if 'all_expanded_idx' not in st.session_state:
        st.session_state.all_expanded_idx = None  # None = 전체 닫힘
    if 'selected_submissions' not in st.session_state:
        st.session_state.selected_submissions = set()

    if history:
        # 상단 일괄 다운로드 버튼
        if st.session_state.selected_submissions:
            st.markdown("---")
            selected_count = len(st.session_state.selected_submissions)

            # 선택된 항목들의 ZIP 파일 생성
            zip_buffer = io.BytesIO()
            with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                for idx in st.session_state.selected_submissions:
                    submission = history[idx]
                    batch_id = submission['batch_id']
                    submit_date = submission['submitted_date'].split()[0]
                    username = submission['username']

                    for item_idx, item in enumerate(submission['items'], 1):
                        md_content = f"""---
품목명: {item['item_name']}
신청자: {username}
요청일: {submit_date}
구매링크: {item['purchase_link']}
옵션명: {item['option_name'] if item['option_name'] else ''}
수량: {item['quantity']}
개당금액: {item['unit_price']}
신청일:
상태: 리스트업
---

"""
                        filename = f"{batch_id}_{item_idx}.md"
                        zip_file.writestr(filename, md_content)

            zip_buffer.seek(0)

            col1, col2 = st.columns([3, 1])
            with col1:
                st.download_button(
                    label=f"📥 선택한 항목 다운로드 ({selected_count}개)",
                    data=zip_buffer,
                    file_name="물품신청_선택항목.zip",
                    mime="application/zip",
                    key="download_selected",
                    use_container_width=True
                )
            with col2:
                if st.button("선택 초기화", use_container_width=True):
                    st.session_state.selected_submissions = set()
                    st.rerun()

            st.markdown("---")

        # 각 신청 항목 표시
        for idx, submission in enumerate(history):
            submit_date = submission['submitted_date'].split()[0]
            username = submission['username']
            is_expanded = (idx == st.session_state.all_expanded_idx)

            # 체크박스 + 토글 버튼
            col_check, col_btn = st.columns([0.5, 9.5])

            with col_check:
                is_checked = st.checkbox(
                    "",
                    value=idx in st.session_state.selected_submissions,
                    key=f"check_{idx}",
                    label_visibility="collapsed"
                )
                # 상태 업데이트
                if is_checked:
                    if idx not in st.session_state.selected_submissions:
                        st.session_state.selected_submissions.add(idx)
                        st.rerun()
                else:
                    if idx in st.session_state.selected_submissions:
                        st.session_state.selected_submissions.discard(idx)
                        st.rerun()

            with col_btn:
                if st.button(
                    f"{'▼' if is_expanded else '▶'} {submit_date} [{username}]",
                    key=f"all_btn_{idx}",
                    use_container_width=True
                ):
                    # 토글: 같은 항목 클릭 시 닫기
                    if st.session_state.all_expanded_idx == idx:
                        st.session_state.all_expanded_idx = None
                    else:
                        st.session_state.all_expanded_idx = idx
                    st.rerun()

            # 선택된 항목만 내용 표시
            if is_expanded:
                items_data = []
                for item_idx, item in enumerate(submission['items'], 1):
                    items_data.append({
                        'No': str(item_idx),
                        '이름': item['item_name'],
                        '링크': item['purchase_link'],
                        '옵션': item['option_name'] if item['option_name'] else '-',
                        '수량': f"{item['quantity']}개",
                        '1개당 금액': f"{item['unit_price']:,}원",
                        '총금액': f"{item['total_price']:,}원"
                    })

                df = pd.DataFrame(items_data)
                st.dataframe(df, use_container_width=True, hide_index=True)

                st.markdown("")  # 여백

                # 품목 수와 총 금액
                col1, col2, col3 = st.columns([2, 1, 1])
                with col1:
                    st.write("")
                with col2:
                    st.markdown(f"**품목 수:** {submission['item_count']}개")
                with col3:
                    st.markdown(f"**총 금액:** {submission['total_amount']:,}원")

                st.markdown("")  # 여백
    else:
        st.info("아직 신청 내역이 없습니다.")

if __name__ == "__main__":
    main()
