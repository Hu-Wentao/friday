import streamlit as st

from src.pages import stream_chat


def welcome_page():
    st.title("欢迎使用 FridayAI")


# ===

def entrance():
    # 配置
    st.set_page_config(
        # page_title: str | None = None,
        # page_icon: PageIcon | None = None,
        layout="wide",
        # initial_sidebar_state="collapsed",
        menu_items={
            # 'Get Help': 'https://eample.com',
            # 'Report a bug': "https://www.extremelycoolapp.com/bug",
            'About': """欢迎使用 Friday"""
        }
        # initial_sidebar_state: InitialSideBarState = "auto",
    )
    # Set page config before any other Streamlit commands
    # # 消费toast
    # if (m := s_toast(consume=True)) is not None:
    #     st.toast(m)

    # 检查登陆状态
    if 'token' not in st.query_params and st.secrets['env']['ACCESS_TOKEN'] != '':
        welcome_page()
    # else:
    #     with st.sidebar:
    #         ui_logged_user(prefix='用户:')
    #         st.text(f'版本: v{VERSION}')

    # 启动导航
    st.navigation(
        [
            st.Page(stream_chat.page, title='Chat', icon='🏠', default=True, ),
            # st.Page(rag_page.page, title='Rag', icon='', url_path='rag'),
        ] +
        ([
             # st.Page(test_page.page, title='_DEV_', icon=None, url_path='test'),
             # st.Page(test_task_page.page, title='_DEV_TASK', icon=None, url_path='test_task'),
         ] if st.secrets['env'] == 'dev' else [])
    ).run()
    pass


if __name__ == '__main__':
    entrance()
    # st.title("💬 Chatbot")
