import streamlit as st
import pandas as pd
import sqlite3
import requests
import calendar
from datetime import datetime, timedelta

# --- 1. 설정 및 API 키 ---
API_KEY = st.secrets["MAPLE_API_KEY"]

# --- 2. 시간 설정 (한국 시간 KST) ---
KST_TIME = datetime.utcnow() + timedelta(hours=9)
current_kst = KST_TIME  # 현재 한국 시간

# --- 3. 데이터베이스 설정 ---
conn = sqlite3.connect('maple_tracker.db', check_same_thread=False)
cur = conn.cursor()
cur.execute("CREATE TABLE IF NOT EXISTS users (nickname TEXT PRIMARY KEY)")
cur.execute("""
            CREATE TABLE IF NOT EXISTS logs
            (
                nickname
                TEXT,
                date
                TEXT,
                level
                INTEGER,
                exp_pct
                REAL,
                meso_man
                INTEGER,
                frags
                INTEGER,
                gems
                INTEGER,
                f_price
                INTEGER,
                g_price
                INTEGER,
                stuff
                INTEGER
                DEFAULT
                0,
                PRIMARY
                KEY
            (
                nickname,
                date
            ))
            """)
conn.commit()


# --- 4. 헬퍼 함수 ---
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


# --- 5. 로그인 시스템 ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in, st.session_state.current_user = False, ""

if not st.session_state.logged_in:
    st.title("🍁 이성호 바보 멍충이")
    login_nickname = st.text_input("캐릭터 닉네임")
    access_password = st.text_input("접속 암호", type="password")
    if st.button("입장하기"):
        if access_password == "도류도":
            cur.execute("SELECT nickname FROM users WHERE nickname = ?", (login_nickname,))
            if not cur.fetchone():
                cur.execute("INSERT INTO users VALUES (?)", (login_nickname,))
                conn.commit()
            st.session_state.logged_in = True
            st.session_state.current_user = login_nickname
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
    if st.button("로그아웃"): st.session_state.logged_in = False; st.rerun()
    st.divider()
    with st.form("input_form", clear_on_submit=True):
        # [수정] 날짜 기본값을 한국 시간 기준 오늘로 설정
        input_date = st.date_input("날짜", current_kst.date())
        input_stuff = st.number_input("소재 (재획비)", min_value=0, step=1)
        input_meso = st.number_input("순수 메소 (만)", min_value=0, step=100)
        input_frags = st.number_input("조각 (개)", min_value=0, step=1)
        input_gems = st.number_input("코잼 (개)", min_value=0, step=1)
        f_price = st.number_input("조각 시세(만)", value=default_f_price)
        g_price = st.number_input("코잼 시세(만)", value=default_g_price)

        if st.form_submit_button("기록 저장"):
            d_str = input_date.strftime('%Y-%m-%d')
            cur.execute("SELECT stuff, meso_man, frags, gems FROM logs WHERE nickname=? AND date=?",
                        (user_nickname, d_str))
            r = cur.fetchone()
            s, m, f, g = (r[0] + input_stuff, r[1] + input_meso, r[2] + input_frags, r[3] + input_gems) if r else (
                input_stuff, input_meso, input_frags, input_gems)
            cur.execute("INSERT OR REPLACE INTO logs VALUES (?,?,?,?,?,?,?,?,?,?)",
                        (user_nickname, d_str, int(char_data['character_level']),
                         float(char_data['character_exp_rate']), m, f, g, f_price, g_price, s))
            conn.commit();
            st.rerun()

# --- 메인 대시보드 ---
df = pd.read_sql("SELECT * FROM logs WHERE nickname = ?", conn, params=(user_nickname,))
if not df.empty:
    df['date'] = pd.to_datetime(df['date'])
    df['total_rev'] = df['meso_man'] + (df['frags'] * df['f_price']) + (df['gems'] * df['g_price'])
    df['month'] = df['date'].dt.strftime('%Y-%m')
    df['week_val'] = df['date'].apply(get_week_of_month)

    # 1. 상단 요약 카드
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

    # 2. 상세 사냥 기록 (위로 올림)
    st.divider()
    st.subheader("📝 상세 사냥 기록")
    display_df = df.sort_values(by='date', ascending=False).copy()
    display_df['날짜'] = display_df['date'].dt.strftime('%Y-%m-%d')
    display_df['수익'] = display_df['total_rev'].apply(format_korean_currency)
    log_table = display_df[['날짜', 'stuff', '수익', 'meso_man', 'frags', 'gems']]
    log_table.columns = ['날짜', '소재', '총 수익', '순수 메소', '조각', '코잼']
    st.dataframe(log_table, use_container_width=True, hide_index=True)

    # 3. 주간별 상세 분석 (아래로 내림)
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
                    st.write(f"**[재획당 평균]**")
                    st.write(f"💰 메소: {format_korean_currency(row['평균메소'])}")
                    st.write(f"💎 조각: {row['평균조각']:.1f}개")
                else:
                    st.info("기록이 없습니다.")

    # 삭제 기능
    with st.expander("🗑️ 기록 삭제하기"):
        delete_date = st.selectbox("날짜 선택", display_df['날짜'].unique())
        if st.button("삭제 실행", type="primary"):
            cur.execute("DELETE FROM logs WHERE nickname = ? AND date = ?", (user_nickname, delete_date))
            conn.commit();
            st.rerun()
else:
    st.info("아직 저장된 사냥 기록이 없습니다. 왼쪽 사이드바에서 첫 기록을 남겨보세요!")