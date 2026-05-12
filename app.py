from datetime import datetime
import streamlit as st
import time
import pandas as pd
import calendar
from streamlit_javascript import st_javascript
from modules.utils import get_kst_now, format_korean_currency, get_week_of_month
from modules.database import DBManager
from modules.api import get_character_info
from modules import ui_components as ui

# 1. 페이지 초기 설정
st.set_page_config(page_title="사냥띠", page_icon="🍁", layout="wide")
ui.inject_custom_css()
db = DBManager()
current_kst = get_kst_now()

# 2. 세션 상태 초기화
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'current_user' not in st.session_state:
    st.session_state.current_user = ""
if 'logout_triggered' not in st.session_state:
    st.session_state.logout_triggered = False

# 3. 자동 로그인 및 로그아웃 로직
if not st.session_state.logout_triggered:
    stored_nickname = st_javascript("localStorage.getItem('maple_user_token');")

    if not st.session_state.logged_in:
        if stored_nickname and str(stored_nickname) not in ["null", "undefined", "0", "None", ""]:
            st.session_state.logged_in = True
            st.session_state.current_user = str(stored_nickname)
            st.rerun()
else:
    st.session_state.logout_triggered = False

# 4. 로그인 화면
if not st.session_state.logged_in:
    st.title("🍁 주5일 4소재 기릿")

    login_nickname = st.text_input("캐릭터 닉네임")
    access_password = st.text_input("접속 암호")
    auto_login_check = st.checkbox("이 컴퓨터에서 자동 로그인 유지", value=True)

    if st.button("입장하기"):
        if access_password == "도류도" and login_nickname:
            st.session_state.logged_in = True
            st.session_state.current_user = login_nickname
            if auto_login_check:
                st_javascript(f"localStorage.setItem('maple_user_token', '{login_nickname}');")
            st.success("로그인 성공!")
            time.sleep(0.5)
            st.rerun()
        else:
            st.error("암호가 올바르지 않습니다.")
    st.stop()

# ---------------------------------------------------------
# 5. 메인 화면
# ---------------------------------------------------------
user_nickname = st.session_state.current_user
char_data = get_character_info(user_nickname)
default_f_price, default_g_price = 500, 200

if char_data:
    ui.render_character_card(char_data)
    world = char_data['world_name']
    if world == "스카니아":
        default_f_price, default_g_price = 600, 10
    elif world == "크로아":
        default_f_price, default_g_price = 700, 10

with st.sidebar:
    st.header(f"✨ {user_nickname}님")

    if st.button("로그아웃"):

        st_javascript("localStorage.removeItem('maple_user_token');")

        st.session_state.logged_in = False
        st.session_state.current_user = ""
        st.session_state.logout_triggered = True  # 자동 로그인 재발동 방지 플래그
        time.sleep(0.5)
        st.rerun()

    with st.form("input_form", clear_on_submit=True):
        st.subheader("사냥 기록 추가")
        input_date = st.date_input("날짜", current_kst.date())
        input_stuff = st.number_input("소재 (재획비)", min_value=0, step=1)
        input_meso = st.number_input("순수 메소 (만)", min_value=0, step=100)
        input_frags = st.number_input("조각 (개)", min_value=0, step=1)
        input_gems = st.number_input("코잼 (개)", min_value=0, step=1)
        f_price = st.number_input("조각 시세(만)", value=default_f_price)
        g_price = st.number_input("코잼 시세(만)", value=default_g_price)

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

# 6. 통계 및 달력 섹션
res = db.fetch_logs(user_nickname)
if res:
    df = pd.DataFrame(res)
    df['date'] = pd.to_datetime(df['date'])
    df['total_rev'] = df['meso_man'] + (df['frags'] * df['f_price']) + (df['gems'] * df['g_price'])
    df['month'] = df['date'].dt.strftime('%Y-%m')
    df['week_val'] = df['date'].apply(get_week_of_month)

    st.subheader("💰 수익 현황")
    m1, m2, m3 = st.columns(3)
    today_v = df[df['date'].dt.date == current_kst.date()]['total_rev'].sum()
    this_w = get_week_of_month(current_kst)
    this_m = current_kst.strftime('%Y-%m')
    week_v = df[(df['month'] == this_m) & (df['week_val'] == this_w)]['total_rev'].sum()
    month_v = df[df['month'] == this_m]['total_rev'].sum()

    m1.metric("오늘 수익", format_korean_currency(today_v))
    m2.metric(f"이번 주 ({this_w}주차)", format_korean_currency(week_v))
    m3.metric("이번 달 총합", format_korean_currency(month_v))

    st.divider()
    st.subheader("🗓️ 월간 사냥 출석부")
    all_months = sorted(df['month'].unique(), reverse=True)
    sel_m = st.selectbox("📅 달 선택", all_months)
    year, month_num = map(int, sel_m.split('-'))
    cal = calendar.monthcalendar(year, month_num)

    h_cols = st.columns(7)
    for i, d in enumerate(["MON", "TUE", "WED", "THU", "FRI", "SAT", "SUN"]):
        h_cols[i].markdown(f"<p style='text-align:center;color:#888;font-size:11px;font-weight:bold;'>{d}</p>",
                           unsafe_allow_html=True)

    for week in cal:
        cols = st.columns(7)
        for i, day in enumerate(week):
            if day == 0:
                cols[i].write("")
            else:
                date_str = f"{year}-{month_num:02d}-{day:02d}"
                target = df[df['date'].dt.strftime('%Y-%m-%d') == date_str]
                if not target.empty:
                    r = target.iloc[0]
                    total = r['total_rev']
                    acc = "#c5ff00" if total >= 100000 else "#ffc600" if total >= 75000 else "#a55eea" if total >= 50000 else "#3498db" if total >= 25000 else "#7f8c8d"
                    gnt = "메제노 ㅋ" if total >= 100000 else "좀하네 ㅋ" if total >= 75000 else "도류도급" if total >= 50000 else "빵미농급" if total >= 25000 else "왜안함 ?"
                    cols[i].markdown(f'''
                        <div style="background:linear-gradient(135deg,#232328,#19191e);border-left:3px solid {acc};border-radius:4px;padding:5px;height:110px;position:relative;">
                            <div style="position:absolute;top:2px;right:4px;font-size:0.6rem;color:#777;">{day}</div>
                            <div style="margin-top:12px;text-align:center;">
                                <div style="font-size:0.55rem;color:#ddd;">💰{format_korean_currency(r["meso_man"])}</div>
                                <div style="font-size:0.6rem;color:#00d2ff;">💎{int(r["frags"])}</div>
                            </div>
                            <div style="margin-top:8px;background:rgba(0,0,0,0.4);text-align:center;border-radius:2px;padding:2px 0;">
                                <div style="font-size:0.45rem;color:{acc};font-weight:bold;">{gnt}</div>
                                <div style="font-size:0.65rem;color:#fff;font-weight:900;">{format_korean_currency(total)}</div>
                            </div>
                        </div>''', unsafe_allow_html=True)
                else:
                    cols[i].markdown(
                        f'<div style="border:1px dashed #333;height:110px;border-radius:4px;position:relative;display:flex;align-items:center;justify-content:center;"><div style="position:absolute;top:2px;right:4px;font-size:0.6rem;color:#333;">{day}</div><span style="color:#222;">-</span></div>',
                        unsafe_allow_html=True)

    # 주간별 분석
    st.divider()
    st.subheader("📊 주간별 분석")
    m_df = df[df['month'] == sel_m]
    last_day_val = calendar.monthrange(year, month_num)[1]
    total_weeks = get_week_of_month(datetime(year, month_num, last_day_val))

    weeks_data = []
    for w in range(1, total_weeks + 1):
        w_df = m_df[m_df['week_val'] == w]
        ts, tr, tf, tm = (w_df['stuff'].sum(), w_df['total_rev'].sum(), w_df['frags'].sum(),
                          w_df['meso_man'].sum()) if not w_df.empty else (0, 0, 0, 0)
        weeks_data.append({"주차": f"{w}주차", "총수익": tr, "소재": ts, "총조각": tf, "총메소": tm})

    w_final = pd.DataFrame(weeks_data)
    c1, c2 = st.columns([1.5, 1])
    with c1:
        st.bar_chart(w_final.set_index("주차")["총수익"], color="#f1c40f")
    with c2:
        for _, row in w_final.iterrows():
            with st.expander(f"📍 {row['주차']} ({format_korean_currency(row['총수익'])})"):
                if row['소재'] > 0:
                    st.write(f"📅 총 사냥: {int(row['소재'])}소재")
                    st.write(f"💰 총 메소: {format_korean_currency(row['총메소'])}")
                    st.write(f"💎 총 조각: {int(row['총조각'])}개")
                else:
                    st.info("기록 없음")

    # 상세 기록 표 및 삭제
    st.divider()
    st.subheader("📝 상세 사냥 기록")
    log_display = df.sort_values(by='date', ascending=False).copy()
    log_display['날짜'] = log_display['date'].dt.strftime('%Y-%m-%d')
    log_display['수익'] = log_display['total_rev'].apply(format_korean_currency)
    st.dataframe(log_display[['날짜', 'stuff', '수익', 'meso_man', 'frags', 'gems']], use_container_width=True,
                 hide_index=True)

    with st.expander("🗑️ 기록 삭제"):
        del_date = st.selectbox("삭제 날짜", log_display['날짜'].unique())
        if st.button("삭제", type="primary"):
            db.delete_log(user_nickname, del_date)
            st.rerun()
else:
    st.info("기록이 없습니다.")