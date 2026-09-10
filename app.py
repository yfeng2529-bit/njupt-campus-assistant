import streamlit as st

st.set_page_config(page_title='南京邮电大学校园知识助手',page_icon='🎓',layout='centered')
st.navigation([
    st.Page('pages/campus_assistant.py',title='校园知识助手',icon='🎓',default=True),
    st.Page('pages/api_settings.py',title='API 管理',icon='🔗'),
]).run()

