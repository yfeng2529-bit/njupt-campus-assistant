"""实际页面回归：所有网络响应使用替身，配置只写临时目录。"""
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from streamlit.testing.v1 import AppTest
import api_manager
import chat_store

class Pages(unittest.TestCase):
    def test_local_editor_and_chat(self):
        with tempfile.TemporaryDirectory() as folder, patch.dict(os.environ,{'PUBLIC_MODE':'false'}), patch.object(api_manager,'CONFIG_FILE',Path(folder)/'api.json'), patch.object(chat_store,'CHAT_FILE',Path(folder)/'chat.json'):
            at = AppTest.from_file('../pages/api_settings.py').run()
            self.assertFalse(at.exception)
            at.text_input[0].set_value('测试')
            at.text_input[1].set_value('https://example.com/v1')
            at.text_input[2].set_value('dummy-secret')
            at.text_input[3].set_value('model')
            next(b for b in at.button if b.label == '保存连接').click().run()
            self.assertFalse(at.exception)
            self.assertEqual(len(api_manager.load_connections()),1)
            self.assertFalse(any(t.value == 'dummy-secret' for t in at.text_input))
            # 已保存密钥不进入控件值，编辑不会丢失密钥。
            edits = [t for t in at.text_input if t.label == '名称']
            edits[-1].set_value('编辑后')
            [b for b in at.button if b.label == '保存连接'][-1].click().run()
            self.assertFalse(at.exception)
            self.assertEqual(api_manager.load_connections()[0]['name'],'编辑后')
            sources = [dict(document='考试纪律',article='第十二条',start_page=282,end_page=283,text='严重作弊原文',score=.8)]
            with patch('rag.retrieve',return_value=sources),patch('rag.answer_question',return_value='测试回答'):
                chat = AppTest.from_file('../pages/campus_assistant.py').run()
                self.assertFalse(chat.exception)
                chat.chat_input[0].set_value('考试作弊会怎么样？').run()
                self.assertFalse(chat.exception)
                self.assertEqual(len(chat.chat_message),2)
                self.assertEqual(len(chat.expander),1)
                chat.run()
                self.assertEqual(len(chat.expander),1)
                next(b for b in chat.button if '清空' in b.label).click().run()
                self.assertEqual(len(chat.chat_message),0)

    def test_no_shared_api_even_with_old_environment(self):
        with tempfile.TemporaryDirectory() as folder, patch.dict(os.environ,{'PUBLIC_MODE':'true','OPENAI_API_KEY':'old-shared-secret','OPENAI_MODEL':'shared'}),patch.object(api_manager,'CONFIG_FILE',Path(folder)/'api.json'),patch.object(chat_store,'CHAT_FILE',Path(folder)/'chat.json'):
            at = AppTest.from_file('../app.py').run()
            self.assertFalse(at.exception)
            self.assertEqual(len(at.chat_input),0)
            at = AppTest.from_file('../pages/api_settings.py').run()
            self.assertFalse(at.exception)
            self.assertEqual(len(at.text_input),4)
if __name__ == '__main__':
    unittest.main()



