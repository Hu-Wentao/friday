from typing import Literal, Callable, Any, Generator, Iterable, TypedDict

import streamlit as st
from openai import OpenAI

from src.shared_state import se_llm


# === state
class Msg(TypedDict):
    role: Literal['user', 'assistant', 'system']
    content: str
    # status: Literal['pending', 'error', 'complete', ‘editing’]  # pending只在stream模式下出现


def s_messages(messages=None, append: Msg = None):
    if 'messages' not in st.session_state:
        st.session_state['messages']: list[Msg] = []
    if messages is not None:
        st.session_state["messages"] = messages
    if append is not None:
        st.session_state["messages"].append(append)
    return st.session_state["messages"]


def s_regen_flag(regen=None, consume=False):  # 是否重新生成回答
    k = 'k_regen'
    if k not in st.session_state:
        st.session_state[k] = False
    if regen is not None:
        st.session_state[k] = regen
    rst = st.session_state[k]
    if consume:  # 消费regen 标志
        st.session_state[k] = False
    return rst


# === 前端方法
def on_chat_msg_menu_change():
    for k, v in st.session_state.items():
        if k.startswith("chat_msg_menu#") and v != '':
            # '❌', '📝', '🔄'
            if v == '❌':
                k_id = int(k.split('#')[1])
                st.session_state.messages.pop(k_id)
            elif v == '📝':
                pass  # todo
                # st.session_state.messages[int(s[1:])] = {"role": "user", "content": st.session_state.messages[int(s[1:])]["content"]}
            elif v == '🔄':
                s_regen_flag(regen=True)
                pass
            st.session_state[k] = ''


def get_llm() -> OpenAI:
    return se_llm(st.session_state["llm_api"])


def get_llm_rsp(llm=None, model=None, msg_ls=None, stream=True):
    if llm is None:
        llm = get_llm()
    if model is None:
        model = st.session_state["openai_model"]
    if msg_ls is None:
        msg_ls = [{
            "role": m["role"],
            "content": m["content"],
            # "name": m.get("name")
        } for m in st.session_state.messages]
    return llm.chat.completions.create(
        model=model,
        messages=msg_ls,
        stream=stream,
    )


def get_avatar_by_role(role: str):
    if role == "user":
        return "👨‍💻"
    elif role == "assistant":
        return "🤖"
    elif role == "system":
        return "🤖"


# ==== GUI

def build_chat_msg(role: Literal['user', 'assistant'], avatar: str, content: str, idx: int):
    with st.chat_message(role, avatar=avatar):
        col = st.columns([14, 1])
        col[0].markdown(content)
        col[1].selectbox(key=f'chat_msg_menu#{idx}', label='Menu', options=['', '❌', '📝', '🔄'],
                         label_visibility='collapsed', on_change=on_chat_msg_menu_change)
    pass


def build_stream_chat_msg(role: Literal['user', 'assistant'], avatar: str,
                          st_content: Callable[..., Any] | Generator[Any, Any, Any] | Iterable[Any], idx: int | None):
    with st.chat_message(role, avatar=avatar):
        col = st.columns([14, 1])
        rsp = col[0].write_stream(st_content)
        s_messages(append=Msg(role=role, content=rsp, ))
        if idx is None:
            idx = len(st.session_state.messages) - 1
        col[1].selectbox(key=f'chat_msg_menu#{idx}', label='Menu', options=['', '❌', '📝', '🔄'],
                         label_visibility='collapsed', on_change=on_chat_msg_menu_change)
    pass


def main():
    st.set_page_config(layout='wide')

    st.title("Friday Chat")

    with st.sidebar:
        st.selectbox("LLM", ["friday_0", "friday_1"], key="llm_api", index=0)
        # gpt-4o-mini               (0.0000135, 0.000054) # Azure(0.0000675, 0.00027)
        # gpt-4o                    (0.000225 , 0.000900) # Azure(0.0011250, 0.004500)
        # claude-3-haiku-20240307   (0.000198, 0.00099)   #
        # claude-3-5-sonnet-20241022(0.002376, 0.01188)
        # claude-3-opus-20240229    (0.011880, 0.05940)
        st.selectbox(key="openai_model", index=0, label="Model", options=[
            "gpt-4o-mini", "gpt-4o",
            "claude-3-haiku-20240307", "claude-3-5-sonnet-20241022", "claude-3-opus-20240229", ], )

    for i, message in enumerate(st.session_state.messages):
        build_chat_msg(
            role=message["role"],
            avatar=get_avatar_by_role(message["role"]),
            content=message["content"],
            idx=i)

    # 用户输入
    if prompt := st.chat_input("What is up?", key="chat_input"):
        s_messages(append={"role": "user", "content": prompt})
        build_chat_msg(
            role="user",
            avatar=get_avatar_by_role('user'),
            content=prompt,
            idx=len(st.session_state.messages) - 1)
        build_stream_chat_msg(
            role="assistant",
            avatar=get_avatar_by_role('assistant'),
            st_content=get_llm_rsp(),
            idx=None)

    # 重新生成
    if s_regen_flag(consume=True):
        build_stream_chat_msg(
            role="assistant",
            avatar=get_avatar_by_role('assistant'),
            st_content=get_llm_rsp(),
            idx=None)


if __name__ == '__main__':
    s_messages()
    # ===
    main()
