import streamlit as st
from openai import OpenAI


@st.cache_resource
def se_llm(name: str = 'friday_0', use_cn_base=True) -> OpenAI:
    return OpenAI(
        api_key=st.secrets['llm'][name]['API_KEY'],
        base_url=st.secrets['llm'][name]['API_BASE_CN'] if use_cn_base else st.secrets['llm'][name]['API_BASE'])
