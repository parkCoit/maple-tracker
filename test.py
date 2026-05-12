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

st.markdown("""
    <style>
    /* 기본 앱 컨테이너 여백 최적화 */
    .block-container { padding-top: 2rem; padding-bottom: 2rem; }

    /* 메트릭(수익 현황) 텍스트 크기 조절 */
    [data-testid="stMetricValue"] { font-size: 1.5rem !important; }
    [data-testid="stMetricLabel"] { font-size: 0.8rem !important; }

    /* 캐릭터 정보 박스 반응형 (모바일에서 세로로) */
    .char-card {
        background: linear-gradient(135deg, #1e272e, #2d3436);
        padding: 20px;
        border-radius: 20px;
        display: flex;
        align-items: center;
        color: white;
        border: 1px solid #444;
        margin-bottom: 20px;
    }

    /* 달력 카드 크기 조절 */
    .calendar-box {
        height: 120px !important;
    }

    /* 화면 폭이 768px 이하일 때 (모바일 전용 스타일) */
    @media (max-width: 768px) {
        .char-card { flex-direction: column; text-align: center; }
        .char-card img { margin-right: 0 !important; margin-bottom: 15px; width: 100px !important; }
        .calendar-box { height: 100px !important; padding: 5px !important; }
        .cal-text-main { font-size: 0.7rem !important; }
        .cal-text-sub { font-size: 0.5rem !important; }
        .cal-grade { font-size: 0.45rem !important; }
    }
    </style>
""", unsafe_allow_html=True)


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
    c_img = char_data['character_image']
    c_name = char_data['character_name']
    c_lv = char_data['character_level']
    c_class = char_data['character_class']
    c_exp = char_data['character_exp_rate']
    world = char_data['world_name']

    html_code = f'<div style="display:flex;justify-content:center;margin-bottom:30px;width:100%;"><div style="width:95%;max-width:800px;background:linear-gradient(135deg,#16171b 0%,#0b0c0f 100%);border-radius:28px;border:2px solid #3c3d42;padding:30px 40px;box-shadow:0 20px 50px rgba(0,0,0,0.7);display:flex;flex-wrap:nowrap;align-items:center;gap:40px;position:relative;overflow:hidden;"><div style="flex-shrink:0;position:relative;z-index:2;"><div style="position:absolute;top:50%;left:50%;transform:translate(-50%,-50%);width:200px;height:200px;background:radial-gradient(circle,rgba(241,196,15,0.1) 0%,transparent 70%);z-index:-1;"></div><img src="{c_img}" style="width:160px;filter:drop-shadow(0:15px:25px:rgba(0,0,0,0.9));display:block;"></div><div style="flex:1;z-index:2;min-width:0;"><div style="margin-bottom:20px;"><h1 style="margin:0;color:#f1c40f;font-size:36px;font-weight:900;letter-spacing:-1.5px;text-shadow:0 4px 8px rgba(0,0,0,0.8);line-height:1.1;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">{c_name}</h1><div style="margin-top:10px;display:flex;align-items:center;gap:12px;color:#d1d1d1;white-space:nowrap;"><span style="font-size:16px;font-weight:700;background:rgba(255,255,255,0.05);padding:2px:12px;border-radius:6px;">{world}</span><span style="font-size:15px;color:#888;">Lv.{c_lv}</span><span style="color:#444;">|</span><span style="font-size:15px;color:#888;">{c_class}</span></div></div><div style="margin-top:25px;"><div style="display:flex;justify-content:space-between;margin-bottom:8px;align-items:flex-end;"><span style="font-size:12px;color:#555;font-weight:900;letter-spacing:2px;">EXP PROGRESS</span><span style="font-size:16px;color:#f1c40f;font-weight:900;font-family:monospace;">{c_exp}%</span></div><div style="width:100%;background:#000;border-radius:20px;height:10px;overflow:hidden;border:1px solid #2d2e34;padding:2px;"><div style="width:{c_exp}%;background:linear-gradient(90deg,#8e8e93 0%,#f1c40f 100%);height:100%;border-radius:20px;box-shadow:0 0 15px rgba(241,196,15,0.5);"></div></div></div></div></div></div>'

    st.markdown(html_code, unsafe_allow_html=True)

# --- 사이드바 ---
with st.sidebar:
    st.header(f"✨ {user_nickname}님")
    if st.button("로그아웃"):
        placeholder = st.empty()

        with placeholder.container():
            st.warning("로그아웃 중입니다... 잠시만 기다려주세요.")

            st_javascript("localStorage.removeItem('maple_user_token');")

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

        header_html = '<div style="display: flex; justify-content: space-between; margin-bottom: 10px; width: 100%; border-bottom: 1px solid #444; padding-bottom: 5px;">'
        for d in days:
            header_html += f'<div style="width: 14.2%; text-align: center; color: #888; font-size: 10px; font-weight: bold;">{d}</div>'
        header_html += '</div>'

        st.markdown(header_html, unsafe_allow_html=True)

        display_df = df.sort_values(by='date', ascending=False).copy()

        for week in cal:
            week_html = '<div style="display: flex; justify-content: space-between; gap: 4px; margin-bottom: 8px; width: 100%;">'

            for day in week:
                if day == 0:
                    week_html += '<div style="width: 14.2%; height: 110px;"></div>'
                else:
                    date_str = f"{year}-{month_num:02d}-{day:02d}"
                    target_row = display_df[display_df['date'].dt.strftime('%Y-%m-%d') == date_str]

                    if not target_row.empty:
                        r = target_row.iloc[0]
                        p_meso = r['meso_man']
                        t_frag = r['frags']
                        d_sum = r['total_rev']

                        # 등급 판정 로직
                        if d_sum >= 100000:
                            acc, gnt = "#c5ff00", "LEGENDARY"
                        elif d_sum >= 75000:
                            acc, gnt = "#ffc600", "UNIQUE"
                        elif d_sum >= 50000:
                            acc, gnt = "#a55eea", "EPIC"
                        elif d_sum >= 25000:
                            acc, gnt = "#3498db", "RARE"
                        else:
                            acc, gnt = "#7f8c8d", "NORMAL"

                        # 금액 포맷팅 (함수 호출)
                        m_str = format_korean_currency(p_meso)
                        s_str = format_korean_currency(d_sum)

                        # 카드 HTML 조립
                        week_html += f'<div style="width: 14.2%; background: linear-gradient(135deg, #232328, #19191e); border: 1px solid {acc}44; border-left: 3px solid {acc}; border-radius: 4px; padding: 4px 1px; height: 110px; display: flex; flex-direction: column; justify-content: space-between; box-sizing: border-box; position: relative;">'
                        week_html += f'<div style="position: absolute; top: 2px; right: 4px; font-size: 0.5rem; color: #777;">{day}</div>'
                        week_html += f'<div style="margin-top: 12px; text-align: center;">'
                        week_html += f'<div style="font-size: 0.5rem; color: #ddd; white-space: nowrap;">💰{m_str}</div>'
                        week_html += f'<div style="font-size: 0.55rem; color: #00d2ff;">💎{int(t_frag)}</div>'
                        week_html += '</div>'
                        week_html += f'<div style="background: rgba(0,0,0,0.4); border-radius: 2px; padding: 2px 0; text-align: center;">'
                        week_html += f'<div style="font-size: 0.4rem; color: {acc}; font-weight: bold;">{gnt}</div>'
                        week_html += f'<div style="font-size: 0.6rem; color: #fff; font-weight: 900;">{s_str}</div>'
                        week_html += '</div></div>'
                    else:
                        week_html += f'<div style="width: 14.2%; background: rgba(255,255,255,0.02); border: 1px dashed rgba(255,255,255,0.05); border-radius: 4px; height: 110px; display: flex; align-items: center; justify-content: center; position: relative; box-sizing: border-box;">'
                        week_html += f'<div style="position: absolute; top: 2px; right: 4px; font-size: 0.5rem; color: #333;">{day}</div>'
                        week_html += '<div style="font-size: 0.6rem; color: #222;">-</div>'
                        week_html += '</div>'

            week_html += '</div>'

            st.markdown(week_html, unsafe_allow_html=True)

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