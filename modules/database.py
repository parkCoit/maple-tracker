import streamlit as st
from supabase import create_client, Client

class DBManager:
    def __init__(self):
        self.client: Client = create_client(
            st.secrets["SUPABASE_URL"],
            st.secrets["SUPABASE_KEY"]
        )

    def fetch_logs(self, nickname):
        res = self.client.table("logs").select("*").eq("nickname", nickname).execute()
        return res.data if res.data else []

    def upsert_log(self, data):
        return self.client.table("logs").upsert(data).execute()

    def delete_log(self, nickname, date_str):
        return self.client.table("logs").delete().eq("nickname", nickname).eq("date", date_str).execute()