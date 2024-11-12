from typing import Literal, Callable, Any, Generator, Iterable, TypedDict

import streamlit as st
from openai import OpenAI

from src.shared_state import se_llm


# === state
class Msg(TypedDict):
    role: Literal['user', 'assistant', 'system']
    content: str
    # status: Literal['pending', 'error', 'complete', ‘editing’]  # pending只在stream模式下出现


def s_messages(messages=None, append: Msg = None) -> list[Msg]:
    if 'messages' not in st.session_state:
        st.session_state['messages']: list[Msg] = []
    if messages is not None:
        st.session_state["messages"] = messages
    if append is not None:
        st.session_state["messages"].append(append)
    return st.session_state["messages"]


def s_llm_gen(gen=None, consume=False):  # 是否重新生成回答
    k = 'k_llm_gen'
    if k not in st.session_state:
        st.session_state[k] = False
    if gen is not None:
        st.session_state[k] = gen
    rst = st.session_state[k]
    if consume:  # 消费 标志
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
                s_llm_gen(gen=True)
                pass
            st.session_state[k] = ''


def get_llm() -> OpenAI:
    return se_llm(st.session_state["llm_api"], st.session_state['use_cn'])


def get_llm_rsp(llm=None, model=None, msg_ls=None, stream=True):
    if llm is None:
        llm = get_llm()
    if model is None:
        model = st.session_state["llm_model"]
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


def on_chat_submit():
    k = 'chat_input'
    prompt = st.session_state[k]
    s_messages(append=Msg(role="user", content=prompt))  # 将刷新UI
    s_llm_gen(gen=True)


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
        msg_len = len(s_messages(append=Msg(role=role, content=rsp)))  # noqa todo 动态刷新,可以不用write_stream
        if idx is None:
            idx = msg_len - 1
        col[1].selectbox(key=f'chat_msg_menu#{idx}', label='Menu', options=['', '❌', '📝', '🔄'],
                         label_visibility='collapsed', on_change=on_chat_msg_menu_change)
    pass


def page():
    s_messages()
    # ===
    st.title("FridayAI Chat")

    with st.sidebar:
        st.toggle('国内', key='use_cn', value=True)

        st.selectbox("LLM", ["friday_0", "friday_1"], key="llm_api", index=0)
        # gpt-4o-mini               (0.0000135, 0.000054) # Azure(0.0000675, 0.00027)
        # gpt-4o                    (0.000225 , 0.000900) # Azure(0.0011250, 0.004500)
        # claude-3-haiku-20240307   (0.000198, 0.00099)   #
        # claude-3-5-sonnet-20241022(0.002376, 0.01188)
        # claude-3-opus-20240229    (0.011880, 0.05940)
        st.selectbox(key="llm_model", index=0, label="Model", options=[
            "gpt-4o-mini", "gpt-4o",
            "claude-3-haiku-20240307", "claude-3-5-sonnet-20241022", "claude-3-opus-20240229", ], )

    for i, message in enumerate(st.session_state.messages):
        build_chat_msg(
            role=message["role"],
            avatar=get_avatar_by_role(message["role"]),
            content=message["content"],
            idx=i)

    # 用户输入
    st.chat_input("What is up?", key="chat_input", on_submit=on_chat_submit)

    # 重新生成
    if s_llm_gen(consume=True):
        build_stream_chat_msg(
            role="assistant",
            avatar=get_avatar_by_role('assistant'),
            st_content=get_llm_rsp(),
            idx=None)


if __name__ == '__main__':
    page()
