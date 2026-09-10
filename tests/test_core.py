import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch, MagicMock
import numpy as np
import api_manager as api
import knowledge_base as kb
import rag

class Connections(unittest.TestCase):
    def test_migration_edit_delete_default(self):
        with tempfile.TemporaryDirectory() as folder:
            with patch.object(api,'CONFIG_FILE',Path(folder)/'connections.json'):
                self.assertEqual(api.load_connections(),[])
                data = [dict(name='A',base_url='https://example.com/v1',api_key='dummy',model='test'),
                        dict(name='B',base_url='https://example.com/v1',api_key='dummy',model='test')]
                api.save_connections(data)
                loaded = api.load_connections()
                self.assertEqual(sum(c['default'] for c in loaded),1)
                identifier = loaded[0]['id']
                loaded[0]['name'] = 'edited'
                api.save_connections(loaded)
                self.assertEqual(api.load_connections()[0]['id'],identifier)
                api.save_connections(loaded[1:])
                self.assertTrue(api.load_connections()[0]['default'])
                api.CONFIG_FILE.write_text('{broken',encoding='utf-8')
                with self.assertRaises(ValueError):
                    api.load_connections()

class Retrieval(unittest.TestCase):
    def test_followup(self):
        history = [dict(role='user',content='考试作弊会怎么样？')]
        self.assertIn('考试作弊',rag.retrieval_query('那严重作弊呢？',history))
        self.assertEqual(rag.retrieval_query('奖学金有哪些？',history),'奖学金有哪些？')

    def test_dedup_and_irrelevance(self):
        c = dict(document='考试纪律',article='第十一条',start_page=1,end_page=1,text='考试作弊处分')
        chunks = [c,dict(c),dict(c,article='第二条',text='天气')]
        model = MagicMock()
        model.encode.return_value = np.array([[1.,0.]])
        with patch.object(rag,'load_knowledge_base',return_value=(chunks,np.array([[1.,0.],[1.,0.],[0.,1.]]))),patch.object(rag,'load_embedding_model',return_value=model):
            result = rag.retrieve('考试作弊')
        self.assertEqual(len(result),1)
        self.assertEqual(result[0]['text'],c['text'])

    def test_empty_sources_no_api(self):
        with patch.object(rag,'client_for') as client:
            self.assertEqual(rag.answer_question('问题',[],[],{}),rag.UNKNOWN)
            client.assert_not_called()

    def test_history_limit(self):
        history = [dict(role='user' if i%2==0 else 'assistant',content=str(i)) for i in range(12)]
        c = dict(document='规则',article='第一条',text='正文',start_page=1,end_page=1)
        client = MagicMock()
        client.__enter__.return_value = client
        client.chat.completions.create.return_value.choices[0].message.content = '答案'
        with patch.object(rag,'client_for',return_value=client):
            rag.answer_question('问题',history,[c],dict(model='test'))
        messages = client.chat.completions.create.call_args.kwargs['messages']
        self.assertEqual(len(messages),8)
        self.assertEqual(messages[1]['content'],'6')

class Knowledge(unittest.TestCase):
    def test_mismatch_and_missing(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            with patch.object(kb,'ROOT',root):
                kb._load.clear()
                with self.assertRaises(ValueError):
                    kb.load_knowledge_base()
                (root/'chunks.json').write_text(json.dumps([dict(document='规则',article='第一条',start_page=1,end_page=1,text='正文')]),encoding='utf-8')
                np.save(root/'vectors.npy',np.ones((2,512)))
                with self.assertRaises(ValueError):
                    kb.load_knowledge_base()
                kb._load.clear()

if __name__ == '__main__':
    unittest.main()

