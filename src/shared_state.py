from typing import Literal

import streamlit as st
from openai import OpenAI

@st.cache_resource
def se_llm(name: str = 'friday_0') -> OpenAI:
    return OpenAI(api_key=st.secrets['llm'][name]['API_KEY'], base_url=st.secrets['llm'][name]['API_BASE'])
