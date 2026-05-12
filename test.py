import streamlit as st
import time
import pandas as pd
from supabase import create_client, Client
import requests
import calendar
from datetime import datetime, timedelta
from streamlit_javascript import st_javascript

st.set_page_config(
    page_title="사냥띠",
    page_icon="🍁",
    layout="wide"
)


# --- 1. 설정 및 Supabase 연결 ---
URL: str = st.secrets["SUPABASE_URL"]
KEY: str = st.secrets["SUPABASE_KEY"]
API_KEY: str = st.secrets["MAPLE_API_KEY"]

# Supabase 클라이언트 초기화
supabase: Client = create_client(URL, KEY)

# --- 2. 시간 설정 (한국 시간 KST) ---
KST_TIME = datetime.utcnow() + timedelta(hours=9)
current_kst = KST_TIME


# --- 3. 헬퍼 함수 ---
def format_korean_currency(amount_man):
    if amount_man < 10000: return f"{amount_man:,.0f}만"
    eok, man = divmod(amount_man, 10000)
    return f"{eok:,.0f}억 {man:,.0f}만" if man > 0 else f"{eok:,.0f}억"


def get_week_of_month(dt):
    first_day = dt.replace(day=1)
    dom = dt.day
    adjusted_dom = dom + first_day.weekday()
    return (adjusted_dom - 1) // 7 + 1


def get_character_info(nickname):
    headers = {"x-nxopen-api-key": API_KEY}
    try:
        id_url = f"https://open.api.nexon.com/maplestory/v1/id?character_name={nickname}"
        res = requests.get(id_url, headers=headers).json()
        ocid = res.get('ocid')
        if not ocid: return None
        info_url = f"https://open.api.nexon.com/maplestory/v1/character/basic?ocid={ocid}"
        return requests.get(info_url, headers=headers).json()
    except:
        return None


# --- 4. 로그인 시스템 ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in, st.session_state.current_user = False, ""

if 'logout_in_progress' not in st.session_state:
    st.session_state.logout_in_progress = False

stored_nickname = st_javascript("localStorage.getItem('maple_user_token');")


if not st.session_state.logged_in and not st.session_state.logout_in_progress:
    if stored_nickname and stored_nickname not in ["null", "undefined", ""]:
        st.session_state.logged_in = True
        st.session_state.current_user = stored_nickname
        st.rerun()

if not st.session_state.logged_in:
    st.session_state.logout_in_progress = False
    st.title("🍁 이성호 바보 멍충이")

    login_nickname = st.text_input("캐릭터 닉네임")
    access_password = st.text_input("접속 암호")

    auto_login = st.checkbox("이 컴퓨터에서 자동 로그인 유지", value=True)


    if st.button("입장하기"):
        if access_password == "도류도":
            st.session_state.logged_in = True
            st.session_state.current_user = login_nickname

            if auto_login:
                # 1. 로컬 스토리지에 저장 (반드시 소문자 localStorage 확인!)
                st_javascript(f"localStorage.setItem('maple_user_token', '{login_nickname}');")
                # 2. 자바스크립트가 브라우저에 도달할 시간을 아주 잠깐(0.1초) 줍니다.
                time.sleep(0.1)

            st.success(f"{login_nickname}님, 반가워요!")
            st.rerun()
        else:
            st.error("암호가 올바르지 않습니다.")
    st.stop()

user_nickname = st.session_state.current_user
char_data = get_character_info(user_nickname)
default_f_price, default_g_price = 500, 200

if char_data:
    world = char_data['world_name']
    if world == "스카니아":
        default_f_price, default_g_price = 600, 10
    elif world == "크로아":
        default_f_price, default_g_price = 700, 10
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, #1e272e, #2d3436); padding: 30px; border-radius: 20px; display: flex; align-items: center; color: white; border: 1px solid #444; margin-bottom: 20px;">
        <img src="{char_data['character_image']}" style="width: 130px; margin-right: 25px;">
        <div style="flex-grow: 1;">
            <h1 style="margin: 0; color: #f1c40f;">{char_data['character_name']} <span style="font-size: 14px; color: #aaa;">({world})</span></h1>
            <p style="margin: 5px 0; font-size: 18px;">Lv. {char_data['character_level']} | {char_data['character_class']}</p>
            <div style="width: 100%; background: #3d3d3d; border-radius: 10px; height: 15px; margin-top: 10px;">
                <div style="width: {char_data['character_exp_rate']}%; background: #00d2ff; height: 100%; border-radius: 10px;"></div>
            </div>
            <p style="text-align: right; font-size: 12px; margin-top: 5px;">EXP: {char_data['character_exp_rate']}%</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

# --- 사이드바 ---
with st.sidebar:
    st.header(f"✨ {user_nickname}님")
    if st.button("로그아웃"):
        # 1. 화면의 기존 내용을 싹 비웁니다.
        placeholder = st.empty()

        with placeholder.container():
            st.warning("로그아웃 중입니다... 잠시만 기다려주세요.")
            # 2. 여기서 자바스크립트를 실행 (화면에 그려져야 실행됨)
            st_javascript("localStorage.removeItem('maple_user_token');")

        # 3. 자바스크립트가 브라우저 저장소를 비울 시간을 충분히 줍니다.
        # 0.1초는 너무 짧을 수 있으니 0.5초 정도로 넉넉히 줍니다.
        time.sleep(0.5)

        # 4. 세션 상태 초기화
        st.session_state.logged_in = False
        st.session_state.current_user = ""
        st.session_state.logout_in_progress = True  # 아까 만든 플래그 유지

        # 5. 이제 새로고침
        st.rerun()
    with st.form("input_form", clear_on_submit=True):
        input_date = st.date_input("날짜", current_kst.date())
        input_stuff = st.number_input("소재 (재획비)", min_value=0, step=1)
        input_meso = st.number_input("순수 메소 (만)", min_value=0, step=100)
        input_frags = st.number_input("조각 (개)", min_value=0, step=1)
        input_gems = st.number_input("코잼 (개)", min_value=0, step=1)
        f_price = st.number_input("조각 시세(만)", value=default_f_price)
        g_price = st.number_input("코잼 시세(만)", value=default_g_price)

        if st.form_submit_button("기록 저장"):
            d_str = input_date.strftime('%Y-%m-%d')
            # 기존 데이터 확인 (합산 로직)
            res = supabase.table("logs").select("stuff, meso_man, frags, gems").eq("nickname", user_nickname).eq("date",
                                                                                                                 d_str).execute()

            if res.data:
                r = res.data[0]
                s, m, f, g = r['stuff'] + input_stuff, r['meso_man'] + input_meso, r['frags'] + input_frags, r[
                    'gems'] + input_gems
            else:
                s, m, f, g = input_stuff, input_meso, input_frags, input_gems

            # 데이터 저장 (UPSERT)
            log_entry = {
                "nickname": user_nickname, "date": d_str, "level": int(char_data['character_level']),
                "exp_pct": float(char_data['character_exp_rate']), "meso_man": m, "frags": f, "gems": g,
                "f_price": f_price, "g_price": g_price, "stuff": s
            }
            supabase.table("logs").upsert(log_entry).execute()
            st.success("클라우드에 저장 완료!")
            st.rerun()

# --- 메인 대시보드 ---
# 유저 데이터 불러오기
res = supabase.table("logs").select("*").eq("nickname", user_nickname).execute()
if res.data:
    df = pd.DataFrame(res.data)
    df['date'] = pd.to_datetime(df['date'])
    df['total_rev'] = df['meso_man'] + (df['frags'] * df['f_price']) + (df['gems'] * df['g_price'])
    df['month'] = df['date'].dt.strftime('%Y-%m')
    df['week_val'] = df['date'].apply(get_week_of_month)

    # 상단 요약 카드
    st.subheader("💰 수익 현황")
    m1, m2, m3 = st.columns(3)
    today_str = current_kst.strftime('%Y-%m-%d')
    today_v = df[df['date'].dt.strftime('%Y-%m-%d') == today_str]['total_rev'].sum()
    this_w_label = get_week_of_month(current_kst)
    this_m_label = current_kst.strftime('%Y-%m')

    week_v = df[(df['month'] == this_m_label) & (df['week_val'] == this_w_label)]['total_rev'].sum()
    month_v = df[df['month'] == this_m_label]['total_rev'].sum()

    m1.metric("오늘 수익", format_korean_currency(today_v))
    m2.metric(f"이번 주 ({this_w_label}주차)", format_korean_currency(week_v))
    m3.metric("이번 달 총합", format_korean_currency(month_v))

    st.divider()


    # 달력
    if not df.empty:

        st.subheader("🗓️ 월간 사냥 출석부")
        all_months = df['date'].dt.strftime('%Y-%m').unique()
        sel_m = st.selectbox("📅 조회할 달을 선택하세요", all_months, index=len(all_months) - 1)

        year, month_num = map(int, sel_m.split('-'))
        cal = calendar.monthcalendar(year, month_num)
        days = ["MON", "TUE", "WED", "THU", "FRI", "SAT", "SUN"]

        # [요일 헤더 및 달력 그리기 로직 시작]
        cols = st.columns(7)
        for i, d in enumerate(days):
            cols[i].markdown(
                f"<div style='text-align: center; color: #888; font-size: 11px; font-weight: bold; margin-bottom: 10px;'>{d}</div>",
                unsafe_allow_html=True)

        display_df = df.sort_values(by='date', ascending=False).copy()

        for week in cal:
            cols = st.columns(7)
            for i, day in enumerate(week):
                if day == 0:
                    cols[i].write("")
                else:
                    date_str = f"{year}-{month_num:02d}-{day:02d}"

                    target_row = display_df[display_df['date'].dt.strftime('%Y-%m-%d') == date_str]

                    if not target_row.empty:

                        pure_meso = target_row['meso_man'].iloc[0]
                        total_frags = target_row['frags'].iloc[0]

                        day_total_sum = target_row['total_rev'].iloc[0]

                        # 메이플 등급 색상 판정 (2.5억 단위)
                        if day_total_sum >= 100000:
                            accent_color, grade_name = "#c5ff00", "LEGENDARY"
                        elif day_total_sum >= 75000:
                            accent_color, grade_name = "#ffc600", "UNIQUE"
                        elif day_total_sum >= 50000:
                            accent_color, grade_name = "#a55eea", "EPIC"
                        elif day_total_sum >= 25000:
                            accent_color, grade_name = "#3498db", "RARE"
                        else:
                            accent_color = "#7f8c8d"; grade_name = "NORMAL"

                        html_content = f"""<div style="background:linear-gradient(135deg, rgba(35,35,40,0.95), rgba(25,25,30,0.95));border:1px solid {accent_color}55;border-left:4px solid {accent_color};border-radius:6px;padding:8px 4px;height:130px;width:100%;box-sizing:border-box;display:flex;flex-direction:column;justify-content:space-between;position:relative;overflow:hidden;box-shadow:0 4px 10px rgba(0,0,0,0.4);"><div style="position:absolute;top:5px;right:8px;font-size:0.65rem;color:#777;font-weight:bold;">{day}</div><div style="margin-top:15px;flex-grow:1;display:flex;flex-direction:column;justify-content:center;gap:3px;"><div style="font-size:0.75rem;color:#ddd;display:flex;align-items:center;justify-content:center;"><span style="margin-right:4px;">💰</span>{format_korean_currency(pure_meso)}</div><div style="font-size:0.75rem;color:#00d2ff;display:flex;align-items:center;justify-content:center;"><span style="margin-right:4px;">💎</span>{int(total_frags)} EA</div></div><div style="background:rgba(0,0,0,0.4);border-radius:4px;padding:4px 0;margin-top:4px;"><div style="font-size:0.55rem;color:{accent_color};font-weight:bold;letter-spacing:1px;text-align:center;">{grade_name}</div><div style="font-size:0.85rem;color:#fff;font-weight:900;text-align:center;text-shadow:0 0 5px {accent_color}aa;">{format_korean_currency(day_total_sum)}</div></div></div>"""
                        cols[i].markdown(html_content, unsafe_allow_html=True)
                    else:
                        html_empty = f"""<div style="background:rgba(255,255,255,0.02);border:1px dashed rgba(255,255,255,0.1);border-radius:6px;height:130px;width:100%;box-sizing:border-box;position:relative;display:flex;align-items:center;justify-content:center;"><div style="position:absolute;top:5px;right:8px;font-size:0.6rem;color:#444;">{day}</div><div style="font-size:0.8rem;color:#222;font-weight:bold;">EMPTY</div></div>"""
                        cols[i].markdown(html_empty, unsafe_allow_html=True)

    # 주간별 상세 분석
    st.divider()
    st.subheader("📊 주간별 분석")
    sel_m = st.selectbox("월 선택", sorted(df['month'].unique(), reverse=True))
    m_df = df[df['month'] == sel_m]

    year, month_num = map(int, sel_m.split('-'))
    last_day = calendar.monthrange(year, month_num)[1]
    total_weeks = get_week_of_month(datetime(year, month_num, last_day))

    weeks_data = []
    for w in range(1, total_weeks + 1):
        w_df = m_df[m_df['week_val'] == w]
        ts = w_df['stuff'].sum() if not w_df.empty else 0
        tr = w_df['total_rev'].sum() if not w_df.empty else 0
        tf = w_df['frags'].sum() if not w_df.empty else 0
        tm = w_df['meso_man'].sum() if not w_df.empty else 0
        weeks_data.append({"주차": f"{w}주차", "총수익": tr, "소재": ts, "총조각": tf, "총메소": tm,
                           "평균메소": tm / ts if ts > 0 else 0, "평균조각": tf / ts if ts > 0 else 0})

    w_final = pd.DataFrame(weeks_data)
    c1, c2 = st.columns([1.5, 1])
    with c1:
        st.bar_chart(w_final.set_index("주차")["총수익"], color="#f1c40f")
    with c2:
        for _, row in w_final.iterrows():
            label = f"📍 {row['주차']} ({format_korean_currency(row['총수익'])})" if row[
                                                                                   '소재'] > 0 else f"📍 {row['주차']} (기록 없음)"
            with st.expander(label):
                if row['소재'] > 0:
                    st.write(f"**[주간 합계]**")
                    st.write(f"📅 총 사냥: {int(row['소재'])}소재")
                    st.write(f"💰 총 메소: {format_korean_currency(row['총메소'])}")
                    st.write(f"💎 총 조각: {int(row['총조각'])}개")
                    st.divider()
                    st.write(f"💰 평균 메소: {format_korean_currency(row['평균메소'])}")
                    st.write(f"💎 평균 조각: {row['평균조각']:.1f}개")
                else:
                    st.info("기록이 없습니다.")

    # 상세 사냥 기록
    st.divider()
    st.subheader("📝 상세 사냥 기록")
    display_df = df.sort_values(by='date', ascending=False).copy()
    display_df['날짜'] = display_df['date'].dt.strftime('%Y-%m-%d')
    display_df['수익'] = display_df['total_rev'].apply(format_korean_currency)
    display_df['야미'] = display_df['meso_man'].apply(format_korean_currency)
    log_table = display_df[['날짜', 'stuff', '수익', '야미', 'frags', 'gems']]
    log_table.columns = ['날짜', '소재', '총 수익', '순수 메소', '조각', '코잼']
    st.dataframe(log_table, use_container_width=True, hide_index=True)


    # 삭제 기능
    with st.expander("🗑️ 기록 삭제하기"):
        delete_date = st.selectbox("날짜 선택", display_df['날짜'].unique())
        if st.button("삭제 실행", type="primary"):
            supabase.table("logs").delete().eq("nickname", user_nickname).eq("date", delete_date).execute()
            st.success(f"{delete_date} 기록 삭제됨")
            st.rerun()
else:
    st.info("기록이 없습니다. 사이드바에서 기록을 남겨보세요!")