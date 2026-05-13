import streamlit as st
from supabase import create_client, Client

class DBManager:
    def __init__(self):
        # 스트림릿 secrets에서 URL과 KEY를 가져와 Supabase 클라이언트를 생성합니다.
        self.client: Client = create_client(
            st.secrets["SUPABASE_URL"],
            st.secrets["SUPABASE_KEY"]
        )

    # ==========================================
    # 1. 사냥 로그 관련 (기존 기능)
    # ==========================================
    def fetch_logs(self, nickname):
        """특정 사용자의 사냥 로그 전체를 가져옵니다."""
        res = self.client.table("logs").select("*").eq("nickname", nickname).execute()
        return res.data if res.data else []

    def upsert_log(self, data):
        """사냥 로그를 저장하거나 업데이트합니다."""
        return self.client.table("logs").upsert(data).execute()

    def delete_log(self, nickname, date_str):
        """특정 날짜의 사냥 로그를 삭제합니다."""
        return self.client.table("logs").delete().eq("nickname", nickname).eq("date", date_str).execute()

    # ==========================================
    # 2. 보스 로그 관련 (새로 추가된 기능)
    # ==========================================
    def fetch_boss_logs(self, nickname, start_date):
        """이번 주(start_date 이후)의 보스 처치 기록만 가져옵니다."""
        res = self.client.table("boss_logs")\
            .select("*")\
            .eq("nickname", nickname)\
            .gte("clear_date", start_date)\
            .execute()
        return res.data if res.data else []

    def fetch_all_boss_logs(self, nickname):
        """월간 통계를 위해 사용자의 전체 보스 기록을 가져옵니다."""
        res = self.client.table("boss_logs")\
            .select("*")\
            .eq("nickname", nickname)\
            .order("clear_date", desc=True)\
            .execute()
        return res.data if res.data else []

    def insert_boss_log(self, data):
        """새로운 보스 처치 기록을 저장합니다."""
        return self.client.table("boss_logs").insert(data).execute()

    def delete_boss_log(self, log_id):
        """보스 처치 기록을 삭제합니다 (ID 기준)."""
        return self.client.table("boss_logs").delete().eq("id", log_id).execute()