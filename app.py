"""Friday 个人AI助理"""
import streamlit as st
from langchain.chat_models import AzureChatOpenAI
from langchain.chat_models.base import BaseChatModel
from langchain.schema import BaseMessage, AIMessage, SystemMessage, HumanMessage


@st.cache_resource
def get_llm(deploy: str) -> BaseChatModel:
    __llm = st.secrets.get("llm")
    llm = AzureChatOpenAI(
        openai_api_base=__llm.get("OPENAI_API_BASE"),
        openai_api_key=__llm.get("OPENAI_API_KEY"),
        openai_api_version=__llm.get("OPENAI_API_VERSION"),
        deployment_name=deploy,
        openai_api_type="azure",
    )
    return llm


# === State
if "msg" not in st.session_state:
    st.session_state.msg = [{"role": "ai", "content": "欢迎使用Friday个人助理"}]

# === UI

"""Friday"""

for m in st.session_state.msg:
    with st.chat_message(m['role']):
        f"""{m['content']}"""

if say := st.chat_input():
    with st.chat_message("user"):
        f"""{say}"""
    with st.chat_message("ai"):
        with st.spinner("..."):
            st.session_state.msg.append({
                "role": "user",
                "content": say
            })
            rsp: BaseMessage = get_llm('gpt4').invoke(
                [
                    SystemMessage(content=m['content']) if m['role'] == 'system' else (
                        AIMessage(content=m['content']) if (m['role'] == 'user' or m['role'] == 'human') else
                        HumanMessage(content=m['content'])
                    )
                    for m in st.session_state.msg
                ]
            )
            st.session_state.msg.append({
                "role": "ai",
                "content": rsp.content
            })
        f"""{rsp.content}"""

