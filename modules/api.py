import streamlit as st
import requests

@st.cache_data(ttl=600)
def get_character_info(nickname):
    api_key = st.secrets["MAPLE_API_KEY"]
    headers = {"x-nxopen-api-key": api_key}
    try:
        id_url = f"https://open.api.nexon.com/maplestory/v1/id?character_name={nickname}"
        res = requests.get(id_url, headers=headers).json()
        ocid = res.get('ocid')
        if not ocid: return None
        info_url = f"https://open.api.nexon.com/maplestory/v1/character/basic?ocid={ocid}"
        return requests.get(info_url, headers=headers).json()
    except:
        return None