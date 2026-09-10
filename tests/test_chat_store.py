import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
import chat_store

class ChatStore(unittest.TestCase):
    def test_save_restore_clear(self):
        with tempfile.TemporaryDirectory() as folder,patch.object(chat_store,'CHAT_FILE',Path(folder)/'history.json'):
            self.assertEqual(chat_store.load_chat(),[])
            messages = [dict(role='user',content=str(i)) for i in range(45)]
            chat_store.save_chat(messages)
            self.assertEqual(chat_store.load_chat(),messages[-40:])
            chat_store.save_chat([])
            self.assertEqual(chat_store.load_chat(),[])
    def test_corrupt_preserved(self):
        with tempfile.TemporaryDirectory() as folder,patch.object(chat_store,'CHAT_FILE',Path(folder)/'history.json'):
            chat_store.CHAT_FILE.write_text('{broken')
            with self.assertRaises(ValueError):
                chat_store.load_chat()
            self.assertEqual(chat_store.CHAT_FILE.read_text(),'{broken')

