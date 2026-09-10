import streamlit as st
from api_manager import load_connections, save_connections, get_models, test_connection

st.title('API 管理')
st.caption('配置仅适合本地个人使用。已保存的密钥不会回填到页面。')
try:
    connections = load_connections()
except ValueError as exc:
    st.error(str(exc))
    st.stop()

def editor(original=None):
    c = original or {}
    key = c.get('id','new')
    name = st.text_input('名称',value=c.get('name',''),key=key+'name')
    url = st.text_input('Base URL',value=c.get('base_url',''),key=key+'url',placeholder='https://example.com/v1')
    if c:
        st.write('已保存 API Key：********')
    secret = st.text_input('API Key（编辑时留空保留原密钥）',type='password',key=key+'secret')
    model = st.text_input('模型名称（可手动填写）',value=c.get('model',''),key=key+'model')
    updated = dict(c,name=name.strip(),base_url=url.strip(),
                   api_key=secret.strip() or c.get('api_key',''),model=model.strip())
    if st.button('获取模型列表',key=key+'models'):
        try:
            st.session_state[key+'options'] = get_models(updated)
        except Exception:
            st.error('获取失败：检查地址和密钥；服务也可能不支持模型列表，可手动填写。')
    options = st.session_state.get(key+'options',[])
    if options:
        selected = st.selectbox('可用模型',options,key=key+'select')
        if st.checkbox('使用所选模型',key=key+'use'):
            updated['model'] = selected
    if st.button('测试连接',key=key+'test'):
        try:
            test_connection(updated)
            st.success('连接成功')
        except Exception:
            st.error('连接失败，请检查地址、密钥、模型权限和服务余额。')
    if st.button('保存连接',key=key+'save'):
        if not all(updated.get(k) for k in ('name','base_url','api_key','model')) or not updated['base_url'].startswith(('http://','https://')):
            st.warning('请完整填写名称、有效的 HTTP(S) 地址、密钥和模型。')
        else:
            try:
                if c:
                    connections[:] = [updated if x['id'] == key else x for x in connections]
                else:
                    connections.append(updated)
                save_connections(connections)
                # 下一次页面运行前清理控件；不能在实例化后修改同名 widget。
                st.session_state['clear_editor'] = key
                st.rerun()
            except OSError:
                st.error('保存失败，请检查文件写入权限。')

pending = st.session_state.pop('clear_editor',None)
if pending:
    for field in list(st.session_state):
        if field.startswith(pending):
            del st.session_state[field]
with st.expander('＋ 新建 API 连接',expanded=not connections):
    editor()
for c in connections:
    with st.expander(c['name']+(' · 默认' if c['default'] else '')):
        editor(c)
        if st.button('设为默认',key=c['id']+'default',disabled=c['default']):
            for item in connections:
                item['default'] = item['id'] == c['id']
            try:
                save_connections(connections)
                st.rerun()
            except OSError:
                st.error('无法保存配置，请检查写入权限。')
        if st.button('删除连接',key=c['id']+'delete'):
            try:
                save_connections([x for x in connections if x['id'] != c['id']])
                st.rerun()
            except OSError:
                st.error('无法删除连接，请检查写入权限。')


