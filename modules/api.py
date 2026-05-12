import streamlit as st
import requests


@st.cache_data(ttl=600)
def get_character_info(nickname):
    api_key = st.secrets["MAPLE_API_KEY"]
    headers = {"x-nxopen-api-key": api_key}
    try:
        # OCID 조회
        id_url = f"https://open.api.nexon.com/maplestory/v1/id?character_name={nickname}"
        res = requests.get(id_url, headers=headers).json()
        ocid = res.get('ocid')
        if not ocid: return None

        # 각 항목별 API 호출 (보스 세팅 확인용)
        urls = {
            "basic": f"https://open.api.nexon.com/maplestory/v1/character/basic?ocid={ocid}",
            "stat": f"https://open.api.nexon.com/maplestory/v1/character/stat?ocid={ocid}",
            "ability": f"https://open.api.nexon.com/maplestory/v1/character/ability?ocid={ocid}",
            "union": f"https://open.api.nexon.com/maplestory/v1/user/union?ocid={ocid}"
        }

        combined_data = {}
        for key, url in urls.items():
            response = requests.get(url, headers=headers).json()
            combined_data.update(response)

        return combined_data
    except Exception as e:
        # 에러 확인이 필요할 경우 st.error(e)를 임시로 사용할 수 있습니다.
        return None