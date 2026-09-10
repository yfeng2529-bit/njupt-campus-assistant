import time
import streamlit as st
from api_manager import load_connections
from chat_store import load_chat, save_chat
from knowledge_base import DOCUMENT
from rag import retrieve, answer_question

st.title('南京邮电大学校园知识助手')
st.caption('基于《南京邮电大学学生手册（2025版）》的 RAG 校园问答系统')
st.info('本地应用：使用你自己的 API。连接配置和聊天记录保存在这台电脑。')
st.caption('学生个人项目，非学校官方服务。答案辅助查阅，以学校现行规定为准。请勿输入学号、电话等个人信息。')
try:
    connections = load_connections()
    connection = next((c for c in connections if c.get('default')),None)
    if 'messages' not in st.session_state:
        st.session_state.messages = load_chat()
except ValueError as exc:
    st.error(str(exc))
    st.stop()

with st.sidebar:
    st.write('当前知识库：',DOCUMENT)
    st.write('当前模型：',connection.get('model') if connection else '尚未配置')
    if st.button('新建对话 / 清空聊天',use_container_width=True):
        try:
            save_chat([])
        except OSError:
            st.error('无法清空本地记录，请检查文件写入权限。')
            st.stop()
        st.session_state.messages = []
        st.rerun()
    st.caption('支持学籍、考试、处分、奖学金等手册问题；不包含实时校园通知。')

if not connection or not connection.get('api_key') or not connection.get('model'):
    st.warning('首次使用：请到侧边栏「API 管理」添加你自己的 API 连接，保存后即可提问。')
    st.stop()

def show_sources(sources):
    st.markdown('**参考来源**')
    if not sources:
        st.caption('未检索到足够相关的手册原文。')
    for i,s in enumerate(sources,1):
        pages = str(s['start_page']) if s['start_page'] == s['end_page'] else f"{s['start_page']}-{s['end_page']}"
        with st.expander(f"来源 {i}：{s['article']} · PDF {pages} 页"):
            st.write(f"《{s.get('document') or DOCUMENT}》")
            st.caption(f"{s['article']} · PDF 第 {pages} 页 · 相似度 {s['score']:.3f}（不是答案可信概率）")
            st.text(s['text'])

st.session_state.setdefault('messages',[])
for m in st.session_state.messages:
    with st.chat_message(m['role']):
        st.markdown(m['content'])
        if m['role'] == 'assistant':
            show_sources(m.get('sources',[]))

question = st.chat_input('例如：考试作弊会受到什么处分？',max_chars=600)
if question and question.strip():
    if time.time()-st.session_state.get('last_request',0) < 5:
        st.warning('请稍等几秒再提问。')
        st.stop()
    st.session_state.last_request = time.time()
    with st.chat_message('user'):
        st.write(question)
    with st.chat_message('assistant'):
        try:
            with st.spinner('正在查阅学生手册…首次加载模型可能需要几分钟。'):
                sources = retrieve(question,st.session_state.messages)
                answer = answer_question(question,st.session_state.messages,sources,connection)
            st.markdown(answer)
            show_sources(sources)
            st.session_state.messages.extend([dict(role='user',content=question),
                dict(role='assistant',content=answer,sources=sources)])
            st.session_state.messages = st.session_state.messages[-40:]
            try:
                save_chat(st.session_state.messages)
            except OSError:
                st.warning('回答已生成，但未能保存到本地。请检查文件写入权限。')
        except Exception:
            st.error('暂时无法完成回答。请检查知识库是否已构建、模型能否下载，以及 API 余额、网络和模型名称，然后重新提问。')

