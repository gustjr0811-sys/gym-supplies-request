import streamlit as st
from supabase import create_client, Client
from datetime import datetime
import uuid

# Supabase 클라이언트 (싱글톤)
_supabase_client: Client = None

def get_supabase_client():
    """Supabase 클라이언트 가져오기"""
    global _supabase_client
    if _supabase_client is None:
        url = st.secrets["supabase"]["url"]
        key = st.secrets["supabase"]["key"]
        _supabase_client = create_client(url, key)
    return _supabase_client

# ============================================
# 인증 관련 함수
# ============================================

def login(username, password):
    """사용자 로그인"""
    try:
        supabase = get_supabase_client()

        # users 테이블에서 사용자 조회
        response = supabase.table("users").select("*").eq("username", username).eq("password", password).execute()

        if response.data and len(response.data) > 0:
            user = response.data[0]
            return {
                'success': True,
                'name': user['name']
            }
        else:
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

# ============================================
# 장바구니 (pending_cart) 관련 함수
# ============================================

@st.cache_data(ttl=30)  # 30초 동안 캐시
def load_pending_cart(username):
    """사용자의 장바구니 불러오기"""
    try:
        supabase = get_supabase_client()

        # pending_cart 테이블에서 사용자의 항목 조회
        response = supabase.table("pending_cart")\
            .select("*")\
            .eq("username", username)\
            .order("added_date", desc=False)\
            .execute()

        if response.data:
            return response.data
        else:
            return []

    except Exception as e:
        st.error(f"장바구니 불러오기 오류: {str(e)}")
        return []

def add_to_pending_cart(username, item_name, purchase_link, option_name, quantity, unit_price, total_price):
    """장바구니에 품목 추가"""
    try:
        supabase = get_supabase_client()

        data = {
            "username": username,
            "item_name": item_name,
            "purchase_link": purchase_link,
            "option_name": option_name,
            "quantity": quantity,
            "unit_price": unit_price,
            "total_price": total_price
            # added_date는 DB에서 자동 설정 (DEFAULT NOW())
        }

        response = supabase.table("pending_cart").insert(data).execute()

        # 캐시 무효화
        load_pending_cart.clear()

        return {'success': True}

    except Exception as e:
        return {
            'success': False,
            'message': f'장바구니 추가 오류: {str(e)}'
        }

def remove_from_pending_cart(username, item_index):
    """장바구니에서 품목 삭제"""
    try:
        supabase = get_supabase_client()

        # 사용자의 항목 먼저 조회
        response = supabase.table("pending_cart")\
            .select("id")\
            .eq("username", username)\
            .order("added_date", desc=False)\
            .execute()

        if response.data and len(response.data) > item_index:
            item_id = response.data[item_index]['id']

            # 해당 항목 삭제
            supabase.table("pending_cart").delete().eq("id", item_id).execute()

            # 캐시 무효화
            load_pending_cart.clear()

        return {'success': True}

    except Exception as e:
        st.error(f"삭제 오류: {str(e)}")
        return {'success': False}

# ============================================
# 신청 제출 관련 함수
# ============================================

def submit_cart(username, cart_items):
    """장바구니 품목들을 제출"""
    try:
        supabase = get_supabase_client()

        batch_id = str(uuid.uuid4())[:8]
        submitted_date = datetime.now().isoformat()

        # submitted_items 테이블에 추가
        for item in cart_items:
            item_data = {
                "username": username,
                "item_name": item['item_name'],
                "purchase_link": item['purchase_link'],
                "option_name": item['option_name'],
                "quantity": item['quantity'],
                "unit_price": item['unit_price'],
                "total_price": item['total_price'],
                "batch_id": batch_id
                # submitted_date와 status는 DB에서 자동 설정
            }
            supabase.table("submitted_items").insert(item_data).execute()

        # submission_summary 테이블에 요약 추가
        total_amount = sum(item['total_price'] for item in cart_items)
        summary_data = {
            "username": username,
            "item_count": len(cart_items),
            "total_amount": total_amount,
            "batch_id": batch_id
            # submitted_date는 DB에서 자동 설정
        }
        supabase.table("submission_summary").insert(summary_data).execute()

        # pending_cart에서 사용자 항목 모두 삭제
        supabase.table("pending_cart").delete().eq("username", username).execute()

        # 캐시 무효화
        load_pending_cart.clear()
        get_submission_history.clear()

        return {'success': True}

    except Exception as e:
        return {
            'success': False,
            'message': f'제출 오류: {str(e)}'
        }

# ============================================
# 내역 조회 관련 함수
# ============================================

@st.cache_data(ttl=30)  # 30초 동안 캐시
def get_submission_history(username):
    """사용자의 신청 내역 조회"""
    try:
        supabase = get_supabase_client()

        # submission_summary에서 사용자의 요약 정보 조회
        summary_response = supabase.table("submission_summary")\
            .select("*")\
            .eq("username", username)\
            .order("submitted_date", desc=True)\
            .execute()

        if not summary_response.data:
            return []

        history = []

        for summary in summary_response.data:
            batch_id = summary['batch_id']

            # 해당 batch_id의 submitted_items 조회
            items_response = supabase.table("submitted_items")\
                .select("*")\
                .eq("batch_id", batch_id)\
                .execute()

            batch_items = []
            if items_response.data:
                batch_items = [
                    {
                        'item_name': item['item_name'],
                        'purchase_link': item['purchase_link'],
                        'option_name': item['option_name'],
                        'quantity': item['quantity'],
                        'unit_price': item['unit_price'],
                        'total_price': item['total_price']
                    }
                    for item in items_response.data
                ]

            history.append({
                'submitted_date': summary['submitted_date'],
                'item_count': summary['item_count'],
                'total_amount': summary['total_amount'],
                'batch_id': batch_id,
                'items': batch_items
            })

        return history

    except Exception as e:
        st.error(f"내역 조회 오류: {str(e)}")
        return []

# ============================================
# 관리자 전용: 전체 내역 조회
# ============================================

@st.cache_data(ttl=30)  # 30초 동안 캐시
def get_all_submission_history():
    """모든 사용자의 신청 내역 조회 (관리자용)"""
    try:
        supabase = get_supabase_client()

        # submission_summary에서 모든 요약 정보 조회 (최신순)
        summary_response = supabase.table("submission_summary")\
            .select("*")\
            .order("submitted_date", desc=True)\
            .execute()

        if not summary_response.data:
            return []

        history = []

        for summary in summary_response.data:
            batch_id = summary['batch_id']
            username = summary['username']

            # 해당 batch_id의 submitted_items 조회
            items_response = supabase.table("submitted_items")\
                .select("*")\
                .eq("batch_id", batch_id)\
                .execute()

            batch_items = []
            if items_response.data:
                batch_items = [
                    {
                        'item_name': item['item_name'],
                        'purchase_link': item['purchase_link'],
                        'option_name': item['option_name'],
                        'quantity': item['quantity'],
                        'unit_price': item['unit_price'],
                        'total_price': item['total_price']
                    }
                    for item in items_response.data
                ]

            history.append({
                'username': username,  # 사용자 이름 추가
                'submitted_date': summary['submitted_date'],
                'item_count': summary['item_count'],
                'total_amount': summary['total_amount'],
                'batch_id': batch_id,
                'items': batch_items
            })

        return history

    except Exception as e:
        st.error(f"전체 내역 조회 오류: {str(e)}")
        return []
