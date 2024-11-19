from typing import Literal, Callable, Any, Generator, Iterable, TypedDict

import streamlit as st
from openai import OpenAI

from src.shared_state import se_llm

# === state
MSG_STATUS = Literal['pending', 'error', 'complete', 'editing']
ROLE_TP = Literal['user', 'assistant', 'system']


class Msg(TypedDict):
    role: ROLE_TP
    content: str
    status: MSG_STATUS  # pending只在stream模式下出现


def s_messages(messages=None, append: Msg = None) -> list[Msg]:
    """msg状态 的数据结构为 list[Msg]"""
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
def s_msg_pop_chat(idx: int):
    st.session_state.messages.pop(idx)


def s_msg_edit_chat(idx: int, n_content: str = None, n_status: MSG_STATUS = None):
    """将某条消息标记为 编辑 状态"""
    cp = []
    for i, msg in enumerate(s_messages()):
        msg: Msg
        if i == idx:
            if n_content is None:
                msg['status']: MSG_STATUS = n_status if n_status else "editing"  # noqa
            else:
                msg['content'] = n_content
                msg['status']: MSG_STATUS = n_status if n_status else "complete"  # noqa
        cp.append(msg)


def s_msg_regen(idx: int, updating: str = None):
    """重新生成"""
    if updating is not None:
        s_msg_edit_chat(idx, updating)

    cp = []
    for i, msg in enumerate(s_messages()):
        if i <= idx:
            cp.append(msg)
    s_messages(cp)
    s_llm_gen(gen=True)


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


def on_chat_submit():
    k = 'chat_input'
    prompt = st.session_state[k]
    s_messages(append=Msg(
        role="user",
        content=prompt,
        status='complete'
    ))  # 将刷新UI
    s_llm_gen(gen=True)


# ==== GUI
def build_avatar_by_role(role: str):
    if role == "user":
        return "👨‍💻"
    elif role == "assistant":
        return "🤖"
    elif role == "system":
        return "🤖"


def build_chat_msg(role: ROLE_TP, avatar: str, content: str, status: MSG_STATUS, idx: int):
    with st.chat_message(role, avatar=avatar):
        _content = st.empty()
        col = st.columns([10, 1, 1, 1])
        if status == 'complete':
            _content.markdown(content)
            col[1].button(":material/edit:", key=f'btn_edit#{idx}', on_click=lambda: s_msg_edit_chat(idx, ))
            col[2].button(":material/refresh:", key=f'btn_refresh#{idx}', on_click=lambda: s_msg_regen(idx))
            # 删除消息
            col[3].button(':material/delete:', key=f'btn_delete#{idx}', on_click=lambda: s_msg_pop_chat(idx))
        elif status == 'editing':
            updating = _content.text_area(f'{role}', value=content)
            col[1].button(":material/check:", key=f'btn_edit#{idx}', on_click=lambda: s_msg_edit_chat(idx, updating))
            col[2].button(":material/refresh:", key=f'btn_refresh#{idx}', on_click=lambda: s_msg_regen(idx, updating))
            # 取消编辑
            col[3].button(':material/close:', key=f'btn_delete#{idx}',
                          on_click=lambda: s_msg_edit_chat(idx, n_status='complete'))

            pass


def build_stream_chat_msg(role: Literal['user', 'assistant'], avatar: str,
                          st_content: Callable[..., Any] | Generator[Any, Any, Any] | Iterable[Any], idx: int | None):
    with st.chat_message(role, avatar=avatar):
        col = st.columns([10, 1])
        rsp = col[0].write_stream(st_content)  # 阻塞 # todo 动态刷新,可以不用write_stream
        s_messages(append=Msg(role=role, content=rsp, status='complete'))
    pass


def page():
    s_messages()
    # ===
    st.title("FridayAI Chat")

    with st.sidebar:
        st.toggle('国内', key='use_cn', value=False)

        st.selectbox("LLM", ["friday_0", "friday_1"], key="llm_api", index=1)
        # gpt-4o-mini               (0.0000135, 0.000054) # Azure(0.0000675, 0.00027)
        # gpt-4o                    (0.000225 , 0.000900) # Azure(0.0011250, 0.004500)
        # claude-3-haiku-20240307   (0.000198, 0.00099)   #
        # claude-3-5-sonnet-20241022(0.002376, 0.01188)
        # claude-3-opus-20240229    (0.011880, 0.05940)
        st.selectbox(key="llm_model", index=0, label="Model", options=[
            "gpt-4o-mini", "gpt-4o",
            "claude-3-haiku-20240307", "claude-3-5-sonnet-20241022", "claude-3-opus-20240229", ], )

        # st.write(st.session_state) # debug

    for i, msg in enumerate(s_messages()):
        msg: Msg
        build_chat_msg(
            role=msg["role"],
            avatar=build_avatar_by_role(msg["role"]),
            content=msg["content"],
            status=msg.get('status', 'complete'),
            idx=i)

    # 用户输入
    st.chat_input("What is up?", key="chat_input", on_submit=on_chat_submit)

    # 重新生成
    if s_llm_gen(consume=True):
        build_stream_chat_msg(
            role="assistant",
            avatar=build_avatar_by_role('assistant'),
            st_content=get_llm_rsp(),
            idx=None)


if __name__ == '__main__':
    page()
