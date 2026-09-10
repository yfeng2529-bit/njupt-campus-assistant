"""当前对话只保存在这台电脑，不提交到 GitHub。"""
import json
import os
from knowledge_base import ROOT

CHAT_FILE = ROOT/'chat_history.json'

def load_chat():
    if not CHAT_FILE.exists():
        return []
    try:
        messages = json.loads(CHAT_FILE.read_text(encoding='utf-8'))
        if not isinstance(messages,list):
            raise ValueError()
        for m in messages:
            if not isinstance(m,dict) or m.get('role') not in ('user','assistant') or not isinstance(m.get('content'),str):
                raise ValueError()
            for s in m.get('sources',[]):
                if not all(k in s for k in ('document','article','start_page','end_page','text','score')):
                    raise ValueError()
        return messages[-40:]
    except (ValueError,TypeError,OSError):
        raise ValueError('本地聊天记录无法读取，请备份 chat_history.json 后移走该文件再打开应用。') from None

def save_chat(messages):
    temporary = CHAT_FILE.with_suffix('.tmp')
    temporary.write_text(json.dumps(messages[-40:],ensure_ascii=False,indent=2),encoding='utf-8')
    os.replace(temporary,CHAT_FILE)

