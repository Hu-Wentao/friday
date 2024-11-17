from typing import Callable, Any


def tool_s_state(update, k: str, init: Callable[[], Any] | Any = None, ):
    """
    :param update: update state value
    :param k: st.state_session state key
    :param init: init state value or init function
    :return: state
    """
    import streamlit as st
    if update is not None:  # 有新值
        st.session_state[k] = update
    elif k not in st.session_state:  # 无值,且未注册key
        if isinstance(init, Callable):
            _value = init()
        else:
            _value = init
        st.session_state[k] = _value
    return st.session_state[k]


def adp_data_editor_height(df_len: int, reserve=1, least_len=2, max_len: int = None) -> int:
    if df_len < least_len:
        df_len = least_len
    if max_len is not None and df_len > max_len:
        df_len = max_len
    return 2 + (df_len + 1 + reserve) * 35


def dev_ui_session_state(show_on: tuple[str] = ('dev', 'test')):
    import streamlit as st
    if st.secrets['env'] not in show_on:
        return
    with st.expander("DEV_STATE"):
        st.json(st.session_state)