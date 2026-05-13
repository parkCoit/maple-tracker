import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
from modules.database import DBManager
from modules.utils import format_korean_currency, get_kst_now

# 1. 초기 설정 및 DB 연결
db = DBManager()
user_nickname = st.session_state.current_user
current_kst = get_kst_now()

# 메이플 주간 초기화(목요일) 기준 이번 주 시작일 계산
days_since_thursday = (current_kst.weekday() - 3) % 7
start_of_week = (current_kst - timedelta(days=days_since_thursday)).replace(hour=0, minute=0, second=0, microsecond=0)
start_date_str = start_of_week.strftime('%Y-%m-%d')

st.title("👹 주간 보스 정산 및 통계")
st.caption(f"이번 주 정산 기간: {start_date_str} ~ 현재")

# 2. 보스 마스터 데이터 (시세 반영)
boss_master_data = {
    "스우": {"하드": 8900, "익스트림": 145000},
    "데미안": {"하드": 8100},
    "가디언 엔젤 슬라임": {"노멀": 3100, "카오스": 13400},
    "루시드": {"노멀": 4200, "하드": 11500},
    "윌": {"노멀": 4600, "하드": 13200},
    "더스크": {"노멀": 4800, "카오스": 15400},
    "듄켈": {"노멀": 5300, "하드": 17100},
    "진 힐라": {"노멀": 9200, "하드": 18800},
    "검은 마법사": {"하드": 70000, "익스트림": 350000},
    "세렌": {"노멀": 26500, "하드": 39500},
    "칼로스": {"노멀": 65800, "카오스": 110000},
    "카링": {"노멀": 82000, "하드": 281900}
}

# 3. 데이터 로드 (이번 주 기록 및 전체 기록)
weekly_logs = db.fetch_boss_logs(user_nickname, start_date_str)
df_weekly = pd.DataFrame(weekly_logs)

all_logs = db.fetch_all_boss_logs(user_nickname)
df_all = pd.DataFrame(all_logs)

# 4. 상단 요약 대시보드
total_weekly_revenue = df_weekly['price'].sum() if not df_weekly.empty else 0
clear_count = len(df_weekly)

col1, col2 = st.columns(2)
with col1:
    st.metric("💰 이번 주 누적 수익", format_korean_currency(total_weekly_revenue))
with col2:
    color = "green" if clear_count >= 12 else "orange"
    st.markdown(f"### 처치 현황: <span style='color:{color}'>{clear_count} / 12</span>", unsafe_allow_html=True)

st.divider()

# 5. 보스 등록 영역
with st.expander("➕ 새 보스 처치 등록", expanded=clear_count < 12):
    c1, c2, c3 = st.columns([2, 1, 1])
    with c1:
        name = st.selectbox("👾 보스명", list(boss_master_data.keys()))
    with c2:
        diff = st.selectbox("⚡ 난이도", list(boss_master_data[name].keys()))
    with c3:
        size = st.number_input("👥 인원", 1, 6, 1)

    calc_price = int(boss_master_data[name][diff] / size)

    if st.button("처치 완료 및 저장", use_container_width=True):
        # 중복 체크: 이번 주에 같은 이름의 보스가 있는지 확인
        is_duplicated = False
        if not df_weekly.empty:
            if name in df_weekly['boss_name'].values:
                is_duplicated = True

        if is_duplicated:
            st.error(f"❌ '{name}'은(는) 이번 주에 이미 처치 기록이 있습니다! (난이도 상관없이 주 1회)")
        elif clear_count >= 12:
            st.warning("이미 이번 주 목표 12마리를 모두 채웠습니다!")
        else:
            db.insert_boss_log({
                "nickname": user_nickname,
                "boss_name": name,
                "difficulty": diff,
                "party_size": size,
                "price": calc_price,
                "clear_date": current_kst.strftime('%Y-%m-%d')
            })
            st.success(f"{name}({diff}) 등록 완료!")
            st.rerun()

# 6. 이번 주 처치 리스트 카드형 UI
st.subheader("📝 이번 주 처치 리스트")
if not df_weekly.empty:
    df_weekly = df_weekly.sort_values(by="boss_name")
    for _, row in df_weekly.iterrows():
        with st.container():
            st.markdown(f"""
            <div style="background: #1a1c23; padding: 15px; border-radius: 10px; border-left: 5px solid #f1c40f; margin-bottom: 5px;">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <span style="color: #fff; font-size: 18px; font-weight: bold;">{row['boss_name']} <small style="color: #888;">({row['difficulty']})</small></span>
                    <span style="color: #f1c40f; font-size: 18px; font-weight: bold;">{format_korean_currency(row['price'])}</span>
                </div>
                <div style="color: #555; font-size: 12px; margin-top: 5px;">
                    {row['party_size']}인 파티 | 처치일: {row['clear_date']}
                </div>
            </div>
            """, unsafe_allow_html=True)

            btn_col, _ = st.columns([0.15, 0.85])
            with btn_col:
                if st.button("삭제", key=f"del_{row['id']}", use_container_width=True):
                    db.delete_boss_log(row['id'])
                    st.rerun()
        st.write("")
else:
    st.info("이번 주 처치 기록이 없습니다.")

st.divider()

# 7. 월간 수익 결산 통계
st.header("📈 월간 수입 결산")
if not df_all.empty:
    df_all['clear_date'] = pd.to_datetime(df_all['clear_date'])
    df_all['month_year'] = df_all['clear_date'].dt.strftime('%Y-%m')

    # 월별 합산 데이터
    monthly_stats = df_all.groupby('month_year').agg({'price': 'sum', 'id': 'count'}).reset_index()
    monthly_stats.columns = ['month_year', 'total_price', 'clear_count']

    # 수익 그래프
    fig = px.bar(
        monthly_stats, x='month_year', y='total_price',
        title="월별 보스 수익 추이",
        labels={'month_year': '날짜', 'total_price': '수익(만 메소)'},
        text_auto='.2s'
    )
    fig.update_traces(marker_color='#f1c40f')
    fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="white")
    st.plotly_chart(fig, use_container_width=True)

    # 최근 월 요약 카드
    st.subheader("🗓️ 최근 월간 요약")
    recent = monthly_stats.sort_values(by='month_year', ascending=False).head(3)
    m_cols = st.columns(len(recent))
    for i, (_, row) in enumerate(recent.iterrows()):
        with m_cols[i]:
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, #2c3e50 0%, #000000 100%); 
                        padding: 20px; border-radius: 15px; border: 1px solid #444; text-align: center;">
                <h4 style="margin: 0; color: #888;">{row['month_year']}</h4>
                <h2 style="margin: 10px 0; color: #f1c40f;">{format_korean_currency(row['total_price'])}</h2>
                <p style="margin: 0; color: #555; font-size: 14px;">총 {row['clear_count']}회 처치</p>
            </div>
            """, unsafe_allow_html=True)
else:
    st.info("결산할 데이터가 충분하지 않습니다.")