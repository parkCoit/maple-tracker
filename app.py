
import streamlit as st
import time
from streamlit_javascript import st_javascript
from modules import ui_components as ui

st.set_page_config(page_title="사냥띠", page_icon="🍁", layout="wide")
ui.inject_custom_css()

# 세션 상태 초기화
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'current_user' not in st.session_state:
    st.session_state.current_user = ""
if 'logout_refreshed' not in st.session_state:
    st.session_state.logout_refreshed = False

# 자동 로그인 로직 (로그아웃 직후가 아닐 때만 작동)
stored_nickname = st_javascript("localStorage.getItem('maple_user_token');")

if not st.session_state.logged_in and not st.session_state.logout_refreshed:
    if stored_nickname and str(stored_nickname) not in ["null", "undefined", "0", "None", "", None]:
        st.session_state.logged_in = True
        st.session_state.current_user = str(stored_nickname)
        st.switch_page("pages/farming.py")

# 4. 로그인 화면
if not st.session_state.logged_in:
    st.title("🍁 주5일 4소재 기릿")
    login_nickname = st.text_input("캐릭터 닉네임")
    access_password = st.text_input("접속 암호")
    auto_login_check = st.checkbox("자동 로그인 유지", value=True)

    if st.button("입장하기"):
        if access_password == "도류도" and login_nickname:
            st.session_state.logged_in = True
            st.session_state.current_user = login_nickname
            st.session_state.logout_refreshed = False # 로그인 성공 시 플래그 리셋
            if auto_login_check:
                st_javascript(f"localStorage.setItem('maple_user_token', '{login_nickname}');")
            st.success("로그인 성공!")
            time.sleep(0.5)
            st.switch_page("pages/farming.py")
        else:
            st.error("암호가 올바르지 않습니다.")
    st.stop()