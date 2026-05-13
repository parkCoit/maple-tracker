import streamlit as st
import time
import pandas as pd
import calendar
from datetime import datetime
from streamlit_javascript import st_javascript
from modules.utils import get_kst_now, format_korean_currency, get_week_of_month
from modules.database import DBManager
from modules.api import get_character_info
from modules import ui_components as ui

# 1. 페이지 초기 설정 및 보안 체크
st.set_page_config(page_title="사냥 수입 관리", page_icon="💰", layout="wide")
if not st.session_state.get('logged_in', False):
    st.warning("로그인이 필요합니다.")
    st.switch_page("app.py")
    st.stop()

db = DBManager()
current_kst = get_kst_now()
user_nickname = st.session_state.current_user
char_data = get_character_info(user_nickname)

# 2. 캐릭터 카드 출력 (상단 고정)
if char_data:
    ui.render_character_card(char_data)

# 3. 사이드바 (기록 입력 및 로그아웃)
with st.sidebar:
    st.header(f"✨ {user_nickname}님")
    if st.button("로그아웃"):
        st_javascript("localStorage.removeItem('maple_user_token');")

        st.session_state.logged_in = False
        st.session_state.current_user = ""
        st.session_state.logout_refreshed = True

        st.switch_page("app.py")
        st.stop()

    with st.form("input_form", clear_on_submit=True):
        st.subheader("사냥 기록 추가")
        input_date = st.date_input("날짜", current_kst.date())
        input_stuff = st.number_input("소재 (재획비)", min_value=0, step=1)
        input_meso = st.number_input("순수 메소 (만)", min_value=0, step=100)
        input_frags = st.number_input("조각 (개)", min_value=0, step=1)
        input_gems = st.number_input("코잼 (개)", min_value=0, step=1)

        # 기본 시세 설정
        d_f_price, d_g_price = 500, 200
        if char_data and char_data['world_name'] == "스카니아":
            d_f_price, d_g_price = 600, 10
        elif char_data and char_data['world_name'] == "크로아":
            d_f_price, d_g_price = 700, 10

        f_price = st.number_input("조각 시세(만)", value=d_f_price)
        g_price = st.number_input("코잼 시세(만)", value=d_g_price)

        if st.form_submit_button("저장하기"):
            d_str = input_date.strftime('%Y-%m-%d')
            res_data = db.fetch_logs(user_nickname)
            r = next((x for x in res_data if x['date'] == d_str), None)
            s, m, f, g = (r['stuff'] + input_stuff, r['meso_man'] + input_meso, r['frags'] + input_frags,
                          r['gems'] + input_gems) if r else (input_stuff, input_meso, input_frags, input_gems)

            db.upsert_log({
                "nickname": user_nickname, "date": d_str, "level": int(char_data['character_level']),
                "exp_pct": float(char_data['character_exp_rate']), "meso_man": m, "frags": f, "gems": g,
                "f_price": f_price, "g_price": g_price, "stuff": s
            })
            st.success("저장 완료!")
            st.rerun()

# 4. 통계 및 데이터 렌더링 (기존 로직 유지)
res = db.fetch_logs(user_nickname)
if res:
    df = pd.DataFrame(res)
    df['date'] = pd.to_datetime(df['date'])
    day_map = {0: '월요일', 1: '화요일', 2: '수요일', 3: '목요일', 4: '금요일', 5: '토요일', 6: '일요일'}
    df['day_name'] = df['date'].dt.weekday.map(day_map)
    df['total_rev'] = df['meso_man'] + (df['frags'] * df['f_price']) + (df['gems'] * df['g_price'])
    df['month'] = df['date'].dt.strftime('%Y-%m')
    df['week_val'] = df['date'].apply(get_week_of_month)

    # 상단 수익 메트릭
    today_v = df[df['date'].dt.date == current_kst.date()]['total_rev'].sum()
    this_w = get_week_of_month(current_kst)
    this_m = current_kst.strftime('%Y-%m')
    week_v = df[(df['month'] == this_m) & (df['week_val'] == this_w)]['total_rev'].sum()
    month_v = df[df['month'] == this_m]['total_rev'].sum()

    ui.render_revenue_metrics(today_v, week_v, month_v, this_w, format_korean_currency)
    st.divider()

    # 월간 출석부
    all_months = sorted(df['month'].unique(), reverse=True)
    sel_m = st.selectbox("📅 달 선택", all_months)
    year, month_num = map(int, sel_m.split('-'))
    ui.render_monthly_calendar(df, year, month_num, format_korean_currency)
    st.divider()

    # 주간 분석
    m_df = df[df['month'] == sel_m]
    last_day_val = calendar.monthrange(year, month_num)[1]
    total_weeks = get_week_of_month(datetime(year, month_num, last_day_val))
    weeks_data = []
    for w in range(1, total_weeks + 1):
        w_df = m_df[m_df['week_val'] == w]
        if not w_df.empty:
            ts, tr, tf, tm = w_df['stuff'].sum(), w_df['total_rev'].sum(), w_df['frags'].sum(), w_df['meso_man'].sum()
            avg_m, avg_f = (tm / ts if ts > 0 else 0), (tf / ts if ts > 0 else 0)
        else:
            ts, tr, tf, tm, avg_m, avg_f = 0, 0, 0, 0, 0, 0
        weeks_data.append(
            {"주차": f"{w}주차", "week_val": w, "총수익": tr, "소재": ts, "총조각": tf, "총메소": tm, "평균메소": avg_m, "평균조각": avg_f})

    ui.render_weekly_analysis(df, pd.DataFrame(weeks_data), format_korean_currency)
    st.divider()

    # 상세 기록 표
    st.subheader("📝 상세 사냥 기록")
    log_display = df.sort_values(by='date', ascending=False).copy()
    log_display['날짜'] = log_display['date'].dt.strftime('%Y-%m-%d')
    log_display['소재'] = log_display['stuff'].apply(lambda x: f"{int(x)}개")
    log_display['총 금액'] = log_display['total_rev'].apply(format_korean_currency)
    log_display['순 메소'] = log_display['meso_man'].apply(format_korean_currency)
    log_display['조각'] = log_display['frags'].apply(lambda x: f"{int(x)}개")
    st.dataframe(log_display[['날짜', '소재', '총 금액', '순 메소', '조각']], use_container_width=True, hide_index=True)

    with st.expander("🗑️ 기록 삭제"):
        del_date = st.selectbox("삭제 날짜", log_display['날짜'].unique())
        if st.button("삭제", type="primary"):
            db.delete_log(user_nickname, del_date)
            st.rerun()
else:
    st.info("기록이 없습니다.")