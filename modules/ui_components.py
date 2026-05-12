import streamlit as st


def inject_custom_css():
    st.markdown("""
        <style>
        .block-container { padding-top: 2rem; padding-bottom: 2rem; }
        [data-testid="stSidebarNav"] {display: none !important;}
        [data-testid="stMetricValue"] { font-size: 1.6rem !important; font-weight: 800 !important; color: #f1c40f !important; }
        [data-testid="stMetricLabel"] { font-size: 0.9rem !important; color: #888 !important; }
        </style>
    """, unsafe_allow_html=True)


def render_character_card(char_data):
    c_img = char_data['character_image']
    c_name = char_data['character_name']
    c_lv = char_data['character_level']
    c_class = char_data['character_class']
    c_exp = char_data['character_exp_rate']
    world = char_data['world_name']

    st.markdown(f'''
    <div style="display:flex;justify-content:center;margin-bottom:30px;">
        <div style="width:95%;max-width:800px;background:linear-gradient(135deg,#16171b 0%,#0b0c0f 100%);border-radius:20px;border:2px solid #3c3d42;padding:20px 40px;box-shadow:0 15px 40px rgba(0,0,0,0.7);display:flex;align-items:center;gap:30px;">
            <img src="{c_img}" style="width:120px;filter:drop-shadow(0 10px 20px rgba(0,0,0,0.9));">
            <div style="flex:1;">
                <h1 style="margin:0;color:#f1c40f;font-size:2rem;font-weight:900;">{c_name}</h1>
                <div style="color:#d1d1d1;font-size:0.9rem;margin-top:5px;">
                    <span style="background:rgba(255,255,255,0.1);padding:2px 8px;border-radius:4px;margin-right:10px;">{world}</span>
                    <span>Lv.{c_lv} | {c_class}</span>
                </div>
                <div style="margin-top:15px;">
                    <div style="display:flex;justify-content:space-between;font-size:0.8rem;color:#555;margin-bottom:5px;"><span>EXP</span><span>{c_exp}%</span></div>
                    <div style="width:100%;background:#000;border-radius:10px;height:10px;border:1px solid #2d2e34;padding:2px;">
                        <div style="width:{c_exp}%;background:linear-gradient(90deg,#8e8e93,#f1c40f);height:100%;border-radius:10px;"></div>
                    </div>
                </div>
            </div>
        </div>
    </div>
    ''', unsafe_allow_html=True)