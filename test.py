import streamlit as st
import pandas as pd
from supabase import create_client, Client
import requests
import calendar
from datetime import datetime, timedelta

# --- 1. 설정 및 Supabase 연결 ---
# Streamlit Secrets에 저장된 정보를 불러옵니다.
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

if not st.session_state.logged_in:
    st.title("🍁 이성호 바보 멍충이 (Cloud)")
    login_nickname = st.text_input("캐릭터 닉네임")
    access_password = st.text_input("접속 암호")
    if st.button("입장하기"):
        if access_password == "도류도":
            # 유저 확인 및 등록 (Supabase)
            supabase.table("users").upsert({"nickname": login_nickname}).execute()
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

    # 2. 상세 사냥 기록
    st.divider()
    st.subheader("📝 상세 사냥 기록")
    display_df = df.sort_values(by='date', ascending=False).copy()
    display_df['날짜'] = display_df['date'].dt.strftime('%Y-%m-%d')
    display_df['수익'] = display_df['total_rev'].apply(format_korean_currency)
    log_table = display_df[['날짜', 'stuff', '수익', 'meso_man', 'frags', 'gems']]
    log_table.columns = ['날짜', '소재', '총 수익', '순수 메소', '조각', '코잼']
    st.dataframe(log_table, use_container_width=True, hide_index=True)

    # 3. 주간별 상세 분석
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
                    st.write(f"**[평균]** 메소: {format_korean_currency(row['평균메소'])} / 조각: {row['평균조각']:.1f}개")
                else:
                    st.info("기록이 없습니다.")

    # 삭제 기능
    with st.expander("🗑️ 기록 삭제하기"):
        delete_date = st.selectbox("날짜 선택", display_df['날짜'].unique())
        if st.button("삭제 실행", type="primary"):
            supabase.table("logs").delete().eq("nickname", user_nickname).eq("date", delete_date).execute()
            st.success(f"{delete_date} 기록 삭제됨")
            st.rerun()
else:
    st.info("기록이 없습니다. 사이드바에서 기록을 남겨보세요!")