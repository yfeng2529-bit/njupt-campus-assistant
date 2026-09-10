"""本地配置与 API 操作。错误信息不包含服务器原文或密钥。"""
import json
import os
from uuid import UUID, uuid4
from urllib.parse import urlparse
from openai import OpenAI
from knowledge_base import ROOT

CONFIG_FILE = ROOT/'api_connections.json'

def normalize(connections):
    seen = set()
    default = next((i for i,c in enumerate(connections) if c.get('default')),0)
    for i,c in enumerate(connections):
        try:
            identifier = str(UUID(str(c.get('id'))))
        except (ValueError,TypeError):
            identifier = str(uuid4())
        if identifier in seen:
            identifier = str(uuid4())
        seen.add(identifier)
        c.update(id=identifier,default=(i == default))
    return connections

def load_connections():
    if not CONFIG_FILE.exists():
        return []
    try:
        connections = json.loads(CONFIG_FILE.read_text(encoding='utf-8'))
        if not isinstance(connections,list) or any(not isinstance(c,dict) or
            not all(isinstance(c.get(k),str) for k in ('name','base_url','api_key','model')) for c in connections):
            raise ValueError()
        old = json.dumps(connections)
        normalize(connections)
        if json.dumps(connections) != old:
            save_connections(connections)
        return connections
    except (ValueError,OSError):
        raise ValueError('无法读取本地 API 配置，请检查文件格式和访问权限。') from None

def save_connections(connections):
    normalize(connections)
    temporary = CONFIG_FILE.with_suffix('.tmp')
    temporary.write_text(json.dumps(connections,ensure_ascii=False,indent=2),encoding='utf-8')
    os.replace(temporary,CONFIG_FILE)

def client_for(c):
    if urlparse(c.get('base_url','')).scheme not in ('http','https'):
        raise ValueError('Base URL 必须是 HTTP(S) 地址。')
    if not c.get('api_key') or not c.get('model'):
        raise ValueError('请填写密钥和模型。')
    return OpenAI(api_key=c['api_key'],base_url=c['base_url'],timeout=45,max_retries=0)

def test_connection(c):
    with client_for(c) as client:
        client.chat.completions.create(model=c['model'],messages=[dict(role='user',content='只回复连接成功')],max_tokens=20)

def get_models(c):
    with client_for(dict(c,model=c.get('model') or 'placeholder')) as client:
        return sorted(m.id for m in client.models.list().data)


