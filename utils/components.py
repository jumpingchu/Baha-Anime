import streamlit as st

def multiselect_yyyymm(df):
    yyyymm_options = sorted(list(df["上映時間"].unique()), reverse=True)
    default_yyyymm = yyyymm_options[:2]
    return st.multiselect("選擇上映時間", options=yyyymm_options, default=default_yyyymm)

def multiselect_score(df):
    score_options = sorted(list(df["評分"].unique()), reverse=True)
    default_score = score_options[:2]
    return st.multiselect("篩選評分", options=score_options, default=default_score)
