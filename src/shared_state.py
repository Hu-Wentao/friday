import streamlit as st
from openai import OpenAI


@st.cache_data
def se_llm_key_base(name: str = 'friday_0', use_cn_base=True) -> tuple[str, str]:
    return (st.secrets['llm'][name]['API_KEY'],
            st.secrets['llm'][name]['API_BASE_CN'] if use_cn_base else st.secrets['llm'][name]['API_BASE'])


@st.cache_resource
def se_llm(name: str = 'friday_0', use_cn_base=True) -> OpenAI:
    return OpenAI(
        api_key=st.secrets['llm'][name]['API_KEY'],
        base_url=st.secrets['llm'][name]['API_BASE_CN'] if use_cn_base else st.secrets['llm'][name]['API_BASE'])
