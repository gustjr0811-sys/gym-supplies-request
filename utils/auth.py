import streamlit as st
from utils.sheets import get_worksheet

def login(username, password):
    """사용자 로그인"""
    try:
        # users 시트에서 사용자 정보 확인
        worksheet = get_worksheet("users")
        users = worksheet.get_all_records()

        for user in users:
            # 문자열로 변환하여 비교 (숫자/텍스트 타입 차이 해결)
            if str(user['username']) == str(username) and str(user['password']) == str(password):
                return {
                    'success': True,
                    'name': user['name']
                }

        return {
            'success': False,
            'message': '아이디 또는 비밀번호가 잘못되었습니다.'
        }

    except Exception as e:
        return {
            'success': False,
            'message': f'로그인 중 오류가 발생했습니다: {str(e)}'
        }

def logout():
    """로그아웃"""
    st.session_state.logged_in = False
    st.session_state.username = None
    st.session_state.name = None
