import streamlit as st
from openai import OpenAI

from src.shared_state import se_llm

# === state
if "messages" not in st.session_state:
    st.session_state.messages = []


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


def get_avatar_by_role(role: str):
    if role == "user":
        return "👨‍💻"
    elif role == "assistant":
        return "🤖"
    elif role == "system":
        return "🤖"


def on_chat_submit():
    k = 'chat_input'
    msg = st.session_state[k]
    # todo


# ==== GUI
st.set_page_config(layout='wide')

st.title("ChatGPT-like")

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
    with st.chat_message(message["role"], avatar=get_avatar_by_role(message["role"])):
        col = st.columns([14, 1])
        col[0].markdown(message["content"])
        col[1].selectbox(key=f'chat_msg_menu#{i}', label='Menu', options=['', '❌', '📝', '🔄'],
                         label_visibility='collapsed', on_change=on_chat_msg_menu_change)

if prompt := st.chat_input("What is up?", key="chat_input", on_submit=on_chat_submit):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    # Display user message in chat message container
    with st.chat_message("user", avatar=get_avatar_by_role('user')):
        st.markdown(prompt)

    with st.chat_message("assistant", avatar=get_avatar_by_role('assistant')):
        stream = get_llm().chat.completions.create(
            model=st.session_state["openai_model"],
            messages=[{
                "role": m["role"],
                "content": m["content"],
                # "name": m.get("name")
            } for m in st.session_state.messages],
            stream=True,
        )
        response = st.write_stream(stream)
    st.session_state.messages.append({"role": "assistant", "content": response})

if s_regen_flag(consume=True):
    with st.chat_message("assistant", avatar=get_avatar_by_role('assistant')):
        stream = get_llm().chat.completions.create(
            model=st.session_state["openai_model"],
            messages=[{
                "role": m["role"],
                "content": m["content"],
                # "name": m.get("name")
            } for m in st.session_state.messages],
            stream=True,
        )
        response = st.write_stream(stream)
    st.session_state.messages.append({"role": "assistant", "content": response})
