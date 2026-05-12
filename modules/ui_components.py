import streamlit as st
import calendar
from datetime import datetime
import plotly.graph_objects as go
import pandas as pd


def inject_custom_css():
    st.markdown("""
        <style>
        /* 기본 레이아웃 설정 */
        .block-container { padding-top: 2rem; padding-bottom: 2rem; }
        [data-testid="stSidebarNav"] {display: none !important;}
        [data-testid="stMetricValue"] { font-size: 1.4rem !important; font-weight: 800 !important; color: #f1c40f !important; }
        [data-testid="stMetricLabel"] { font-size: 0.8rem !important; color: #888 !important; }

        /* 반응형 카드 디자인 */
        .char-card {
            display: flex;
            flex-direction: row;
            align-items: center;
            gap: 20px;
            width: 100%;
            background: linear-gradient(135deg, #16171b 0%, #0b0c0f 100%);
            border-radius: 20px;
            border: 2px solid #3c3d42;
            padding: 20px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.5);
        }

        /* 반응형 달력 아이템 */
        .cal-item {
            background: linear-gradient(135deg, #232328, #19191e);
            border-radius: 4px;
            padding: 5px;
            height: 110px;
            position: relative;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
        }

        /* 모바일용 미디어 쿼리 (화면 너비 768px 이하) */
        @media (max-width: 768px) {
            .char-card {
                flex-direction: column; /* 세로 배치 */
                text-align: center;
                padding: 15px;
            }
            .char-card img {
                width: 100px !important;
            }
            .cal-item {
                height: 80px !important; /* 달력 높이 축소 */
                padding: 3px !important;
            }
            .cal-text-main {
                font-size: 0.5rem !important; /* 텍스트 크기 축소 */
            }
            .cal-text-sub {
                font-size: 0.4rem !important;
            }
            .cal-rank {
                display: none; /* 모바일에서 등급 텍스트는 숨김 (공간 확보) */
            }
            [data-testid="stMetricValue"] { font-size: 1.1rem !important; }
        }
        </style>
    """, unsafe_allow_html=True)


def render_character_card(char_data):
    c_img = char_data.get('character_image', '')
    c_name = char_data.get('character_name', '정보 없음')
    c_lv = char_data.get('character_level', '0')
    c_class = char_data.get('character_class', '-')
    c_exp = char_data.get('character_exp_rate', 0)
    world = char_data.get('world_name', '-')

    st.markdown(f'''
    <style>
        @import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard/dist/web/static/pretendard.css');

        .main-wrapper {{
            width: 1000px;
            margin: 0 auto 25px auto;
            font-family: 'Pretendard', sans-serif;
            -webkit-font-smoothing: antialiased;
        }}

        .info-container {{
            background-color: #121212;
            border-radius: 12px;
            height: 276px;
            display: flex;
            align-items: center;
            padding: 0 40px;
            gap: 30px;
            color: rgb(255, 255, 255);
            border: 1px solid rgb(38, 38, 38);
            position: relative;
            box-sizing: border-box;
        }}

        .char-box-outer {{
            width: 180px;
            height: 180px;
            background-color: #1a1a1a;
            border: 1px solid #333;
            border-radius: 20px;
            position: relative;
            overflow: hidden;
            flex-shrink: 0;
        }}

        .char-img-inner {{
            width: 144px;
            height: 144px;
            position: absolute;
            top: 0; left: 0; right: 0; bottom: 0;
            margin: auto;
            background-image: url('{c_img}');
            background-position: 50% 50%;
            background-size: cover;
            background-repeat: no-repeat;
            transform: matrix(-1, 0, 0, 1, 0, 0);
            scale: 2;
            display: block;
        }}

        .info-content {{
            flex: 1;
            display: flex;
            flex-direction: column;
            justify-content: center;
        }}

        .info-header {{
            display: flex;
            align-items: center;
            gap: 12px;
            margin-bottom: 20px;
        }}

        .nickname {{
            font-size: 2.2rem;
            font-weight: 800;
            letter-spacing: -2%;
            margin: 0;
        }}

        .world-tag {{
            background: rgba(255, 107, 0, 0.15);
            color: rgb(255, 107, 0);
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 0.9rem;
            font-weight: 600;
        }}

        .detail-grid {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 12px 40px;
            font-size: 1.1rem;
            color: #999;
            margin-bottom: 30px;
        }}

        .detail-item b {{
            color: #eee;
            margin-left: 8px;
        }}

        .exp-wrapper {{
            width: 100%;
            max-width: 600px;
        }}

        .exp-bar-bg {{
            width: 100%;
            height: 8px;
            background: #222;
            border-radius: 10px;
            overflow: hidden;
        }}

        .exp-bar-fill {{
            width: {c_exp}%;
            height: 100%;
            background: linear-gradient(90deg, #ff6b00, #ff9e00);
            box-shadow: 0 0 10px rgba(255, 107, 0, 0.4);
        }}

        @media (max-width: 1000px) {{
            .main-wrapper {{ width: 95%; }}
            .info-container {{ height: auto; padding: 40px 20px; flex-direction: column; text-align: center; }}
            .detail-grid {{ grid-template-columns: 1fr; gap: 10px; }}
            .info-header {{ justify-content: center; }}
        }}
    </style>

    <div class="main-wrapper">
        <div class="info-container">
            <div class="char-box-outer">
                <div class="char-img-inner"></div>
            </div>
            <div class="info-content">
                <div class="info-header">
                    <span class="nickname">{c_name}</span>
                    <span class="world-tag">● {world}</span>
                </div>
                <div class="detail-grid">
                    <div class="detail-item">직업 <b>{c_class}</b></div>
                    <div class="detail-item">레벨 <b>Lv.{c_lv} ({c_exp}%)</b></div>
                </div>
                <div class="exp-wrapper">
                    <div style="display:flex; justify-content:space-between; font-size:0.8rem; color:#666; margin-bottom:8px;">
                        <span style="font-weight:bold; color:#ff6b00;">EXP</span>
                        <span>{c_exp}%</span>
                    </div>
                    <div class="exp-bar-bg">
                        <div class="exp-bar-fill"></div>
                    </div>
                </div>
            </div>
        </div>
    </div>
    ''', unsafe_allow_html=True)


def render_revenue_metrics(today_v, week_v, month_v, week_num, format_func):
    st.subheader("💰 수익 현황")
    m1, m2, m3 = st.columns(3)
    m1.metric("오늘", format_func(today_v))
    m2.metric(f"{week_num}주차", format_func(week_v))
    m3.metric("이번 달", format_func(month_v))


def render_monthly_calendar(df, target_year, target_month, format_func):
    st.markdown(f"""
        <style>
            /* --- 공통 레이아웃 --- */
            .calendar-container {{ 
                background-color: #0d1117; 
                padding: 8px; 
                border-radius: 10px; 
                border: 1px solid #30363d;
                max-width: 900px;
                margin: 0 auto;
            }}

            .calendar-table {{ width: 100%; border-collapse: collapse; table-layout: fixed; }}

            /* --- 데스크탑 달력 스타일 --- */
            .day-cell {{ 
                height: 115px; border: 1px solid #21262d; vertical-align: top; padding: 4px; overflow: hidden;
            }}
            .day-num {{ font-size: 0.7rem; font-weight: 500; margin-bottom: 2px; color: #7d8590; }}
            .sun {{ color: #f85149 !important; }}
            .sat {{ color: #58a6ff !important; }}

            .grade-dot {{
                font-size: 0.55rem; font-weight: 700; margin-bottom: 3px; display: inline-block;
                padding: 0px 4px; border-radius: 10px;
            }}

            .stat-box {{ display: flex; flex-direction: column; gap: 1px; }}
            .stat-row {{ display: flex; justify-content: space-between; align-items: center; line-height: 1.2; }}
            .label-text {{ color: #7d8590; font-size: 0.62rem; }}
            .val-text {{ font-weight: 500; color: #c9d1d9; font-size: 0.62rem; }}
            .val-meso {{ color: #e3b341; font-weight: 600; font-size: 0.62rem; }}

            .val-net-group {{ 
                margin-top: 4px; padding-top: 3px; border-top: 1px solid #30363d; text-align: right;
            }}
            .val-net {{ color: #f0f6fc; font-weight: 700; font-size: 0.65rem; }}

            /* --- 모바일 리스트 스타일 --- */
            .mobile-list-container {{ display: none; width: 100%; }}
            .mobile-card {{
                background: #0d1117; border-radius: 8px; padding: 10px; margin-bottom: 6px;
                border: 1px solid #30363d; display: flex; justify-content: space-between; align-items: center;
            }}
            .m-date {{ font-size: 0.85rem; font-weight: bold; color: #c9d1d9; }}
            .m-grade {{ font-size: 0.65rem; font-weight: 800; }}
            .m-net {{ color: #f0f6fc; font-weight: bold; font-size: 0.95rem; }}
            .m-sub {{ color: #7d8590; font-size: 0.7rem; }}

            /* --- 반응형 스위칭 (700px 기준) --- */
            @media (max-width: 700px) {{
                .calendar-container {{ display: none !important; }}
                .mobile-list-container {{ display: block !important; }}
            }}
        </style>
    """, unsafe_allow_html=True)

    def get_grade_info(meso):
        if meso >= 50000: return "#3fb950", "메제 나이쨔!"  # 초록
        if meso >= 30000: return "#d29922", "도류도급 에바야~"  # 노랑
        if meso >= 15000: return "#8b949e", "빵미농급 기모띠~"  # 회색
        return "#484f58", "일안하냐?"

    st.subheader(f"📅 {target_year}년 {target_month}월 현황")

    cal = calendar.Calendar(firstweekday=6)
    month_days = cal.monthdayscalendar(target_year, target_month)

    # --- 1. 데스크탑 달력 렌더링 ---
    html_cal = '<div class="calendar-container"><table class="calendar-table"><tr>'
    for i, day_name in enumerate(['일', '월', '화', '수', '목', '금', '토']):
        cls = 'sun' if i == 0 else ('sat' if i == 6 else '')
        html_cal += f'<th style="color:#7d8590; padding:4px; font-size:0.7rem; font-weight:normal;" class="{cls}">{day_name}</th>'
    html_cal += '</tr>'

    for week in month_days:
        html_cal += '<tr>'
        for i, day in enumerate(week):
            if day == 0:
                html_cal += '<td class="day-cell"></td>'
            else:
                curr_str = f"{target_year}-{target_month:02d}-{day:02d}"
                day_data = df[df['date'].dt.strftime('%Y-%m-%d') == curr_str]
                day_cls = 'sun' if i == 0 else ('sat' if i == 6 else '')
                html_cal += f'<td class="day-cell"><div class="day-num {day_cls}">{day}</div>'

                if not day_data.empty:
                    total_meso = day_data['meso_man'].sum()
                    total_frags = int(day_data['frags'].sum())
                    total_stuff = int(day_data['stuff'].sum())
                    net_revenue = day_data['total_rev'].sum()
                    g_color, g_msg = get_grade_info(total_meso)

                    html_cal += f'''
                        <div class="grade-dot" style="background: {g_color}22; color: {g_color}; border: 1px solid {g_color}44;">{g_msg}</div>
                        <div class="stat-box">
                            <div class="stat-row">
                                <span class="label-text">🎮 {total_stuff}소재</span>
                                <span class="val-text">💎 {total_frags}</span>
                            </div>
                            <div class="stat-row"><span class="label-text">💰</span><span class="val-meso">{format_func(total_meso)}</span></div>
                            <div class="val-net-group"><span class="val-net">✨ {format_func(net_revenue)}</span></div>
                        </div>'''
                html_cal += '</td>'
        html_cal += '</tr>'
    html_cal += '</table></div>'

    # --- 2. 모바일 리스트 렌더링 ---
    html_list = '<div class="mobile-list-container">'
    month_data = df[(df['date'].dt.year == target_year) & (df['date'].dt.month == target_month)].sort_values('date',
                                                                                                             ascending=False)

    if month_data.empty:
        html_list += '<div style="color:#7d8590; text-align:center; padding:20px; font-size:0.8rem;">사냥 기록이 없습니다.</div>'
    else:
        for _, row in month_data.iterrows():
            g_color, g_msg = get_grade_info(row['meso_man'])
            html_list += f'''
                <div class="mobile-card" style="border-left: 3px solid {g_color};">
                    <div>
                        <div class="m-date">{row['date'].strftime('%m.%d')} ({row['day_name'][0]})</div>
                        <div class="m-grade" style="color:{g_color};">{g_msg}</div>
                    </div>
                    <div style="text-align:right;">
                        <div class="m-net">✨ {format_func(row['total_rev'])}</div>
                        <div class="m-sub">🎮 {int(row['stuff'])}회 | 💎 {int(row['frags'])}개</div>
                    </div>
                </div>'''
    html_list += '</div>'

    st.markdown(html_cal + html_list, unsafe_allow_html=True)


def render_weekly_analysis(df, w_final, format_func):
    # 1. 스타일 정의
    st.markdown("""
        <style>
            .stat-card {
                background: #111418; border: 1px solid #2d3139;
                border-radius: 10px; padding: 18px; text-align: center;
            }
            .stat-label { color: #848d97; font-size: 0.85rem; margin-bottom: 5px; }
            .stat-value { color: #ffffff; font-size: 1.3rem; font-weight: 800; }
            .detail-container {
                background: #0d1117; border: 1px solid #30363d; 
                border-radius: 8px; padding: 12px; margin-top: 5px;
            }
            .detail-row { display: flex; justify-content: space-between; margin-bottom: 6px; }
            .label-text { color: #848d97; font-size: 0.85rem; }
            .val-meso { color: #f1c40f; font-weight: bold; }
            .val-frag { color: #58a6ff; font-weight: bold; }
            .time-highlight { color: #ffffff; font-weight: bold; background: #21262d; padding: 2px 6px; border-radius: 4px; }
        </style>
    """, unsafe_allow_html=True)

    st.title("📊 주간별 분석")

    # --- 데이터 전처리 (NaN 및 타입 해결) ---
    df['date'] = pd.to_datetime(df['date'])
    # NaN 값이 있는 행은 제외하고 월을 정수로 변환
    df = df.dropna(subset=['date']).copy()
    df['month'] = df['date'].dt.month.astype(int)

    if 'month' not in w_final.columns:
        week_month_map = df.groupby('week_val')['month'].first().reset_index()
        w_final = pd.merge(w_final, week_month_map, on='week_val', how='left')

    w_final = w_final.dropna(subset=['month']).copy()
    w_final['month'] = w_final['month'].astype(int)

    # 2. 월 선택 (오늘 날짜 기준)
    now = datetime.now()
    current_month = now.month
    month_list = sorted(w_final['month'].unique())

    try:
        default_month_idx = month_list.index(current_month)
    except ValueError:
        default_month_idx = len(month_list) - 1 if month_list else 0

    selected_month = st.selectbox("📅 월 선택", month_list, index=default_month_idx, format_func=lambda x: f"{int(x)}월")

    # 3. 주차 필터링 및 정렬 (ascending=True로 설정하여 1->2->3주차 순서로)
    filtered_w_final = w_final[w_final['month'] == selected_month].sort_values(by='week_val',
                                                                               ascending=True).reset_index(drop=True)

    if filtered_w_final.empty:
        st.info(f"{selected_month}월에 기록된 데이터가 없습니다.")
        return

    # 4. 탭 생성
    tab_titles = [f"{row['주차']}" for _, row in filtered_w_final.iterrows()]
    tabs = st.tabs(tab_titles)

    for i, tab in enumerate(tabs):
        with tab:
            week_row = filtered_w_final.iloc[i]
            current_week_num = week_row['week_val']
            weekly_raw_data = df[df['week_val'] == current_week_num].copy()

            # 상단 요약 카드
            c1, c2, c3, c4 = st.columns(4)
            metrics = [
                ("총 메소", format_func(week_row["총메소"]), "white"),
                ("총 조각", f"{int(week_row['총조각'])}개", "white"),
                ("1소재 평균 메소", format_func(week_row["평균메소"]), "#f1c40f"),
                ("1소재 평균 조각", f"{week_row['평균조각']:.1f}개", "#58a6ff")
            ]
            for col, (label, val, color) in zip([c1, c2, c3, c4], metrics):
                col.markdown(
                    f'<div class="stat-card"><div class="stat-label">{label}</div><div class="stat-value" style="color:{color};">{val}</div></div>',
                    unsafe_allow_html=True)

            st.write("")
            col_left, col_right = st.columns([7, 3])
            day_order = ["월요일", "화요일", "수요일", "목요일", "금요일", "토요일", "일요일"]
            short_days = ["월", "화", "수", "목", "금", "토", "일"]

            with col_left:
                st.subheader("주간별 수익 그래프")
                daily_stats = weekly_raw_data.groupby('day_name').agg(
                    {'meso_man': 'sum', 'frags': 'sum', 'stuff': 'sum'}).reindex(day_order, fill_value=0)

                hover_text = []
                for day, row in daily_stats.iterrows():
                    total_min = int(row['stuff']) * 30
                    h, m = divmod(total_min, 60)
                    time_str = f"{h}시간 {m}분" if h > 0 else f"{m}분"
                    hover_text.append(
                        f"<b>{day}</b><br><br>💰 메소: {format_func(row['meso_man'])}<br>💎 조각: {int(row['frags'])}개<br>⏱ 시간: {time_str}")

                fig = go.Figure()
                fig.add_trace(go.Bar(x=short_days, y=daily_stats['meso_man'], marker_color='#f1c40f', hoverinfo="text",
                                     hovertext=hover_text))
                fig.update_layout(template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                                  height=480, margin=dict(t=30, b=50, l=0, r=0),
                                  yaxis=dict(title="메소", gridcolor='#2d3139'), xaxis=dict(showgrid=False))
                st.plotly_chart(fig, use_container_width=True, key=f"chart_{current_week_num}")

            with col_right:
                st.subheader("상세 데이터")
                for d_full in day_order:
                    day_data = weekly_raw_data[weekly_raw_data['day_name'] == d_full]
                    has_data = not day_data.empty
                    with st.expander(f"**{d_full}**", expanded=has_data):
                        if has_data:
                            m_total = day_data['meso_man'].sum()
                            f_total = day_data['frags'].sum()
                            s_total = int(day_data['stuff'].sum())
                            total_min = s_total * 30
                            hours, mins = divmod(total_min, 60)
                            time_display = f"{hours}시간 {mins}분" if hours > 0 else f"{mins}분"
                            m_per_stuff = m_total / s_total if s_total > 0 else 0
                            f_per_stuff = f_total / s_total if s_total > 0 else 0

                            st.markdown(f"""
                                <div class="detail-container">
                                    <div class="detail-row"><span class="label-text">⏱ 총 사냥 시간</span><span class="time-highlight">{time_display}</span></div>
                                    <div class="detail-row" style="margin-top:4px;"><span class="label-text">📦 사용 소재</span><span style="color:#cfcfcf; font-size:0.85rem;">{s_total}개 소모</span></div>
                                    <hr style="border:0; border-top:1px solid #30363d; margin:10px 0;">
                                    <div class="detail-row"><span class="label-text">💰 총 메소</span><span class="val-meso">{format_func(m_total)}</span></div>
                                    <div class="detail-row"><span class="label-text">💎 총 조각</span><span class="val-frag">{int(f_total)}개</span></div>
                                    <hr style="border:0; border-top:1px solid #30363d; margin:10px 0;">
                                    <div class="detail-row"><span class="label-text">📊 1소재 평균 메소</span><span style="color:#f1c40f; font-size:0.85rem;">{format_func(m_per_stuff)}</span></div>
                                    <div class="detail-row"><span class="label-text">📈 1소재 평균 조각</span><span style="color:#58a6ff; font-size:0.85rem;">{f_per_stuff:.1f}개</span></div>
                                </div>
                            """, unsafe_allow_html=True)
                        else:
                            st.caption("사냥 기록이 없습니다.")