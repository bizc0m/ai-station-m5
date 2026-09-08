import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
import local_conversation as chat

class LocalConversationTest(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.root=patch.object(chat,'ROOT',Path(self.tmp.name));self.root.start()
    def tearDown(self):
        self.root.stop();self.tmp.cleanup()
    def test_duplicate_send_keeps_single_message(self):
        s=chat.create('model-a','project-a')['session']['session_id']
        with patch.object(chat.threading,'Thread') as thread:
            chat.send(s,'bonjour','turn-1',{})
            chat.send(s,'bonjour','turn-1',{})
            self.assertEqual(thread.call_count,1)
            self.assertEqual(len(chat.load(s)['messages']),1)
            with self.assertRaises(ValueError):chat.send(s,'autre','turn-2',{})
    def test_restart_preserves_message_and_marks_interruption(self):
        s=chat.create('model-a','project-a')['session']['session_id']
        with patch.object(chat.threading,'Thread'):chat.send(s,'à conserver','turn-1',{})
        chat.recover();d=chat.load(s)
        self.assertEqual(d['messages'][0]['text'],'à conserver')
        self.assertEqual(d['messages'][1]['role'],'error')
        self.assertIsNone(d['session']['active_turn_id'])
    def test_sessions_keep_separate_models(self):
        a=chat.create('model-a','a');b=chat.create('model-b','b')
        self.assertNotEqual(a['session']['session_id'],b['session']['session_id'])
        self.assertEqual(chat.load(a['session']['session_id'])['session']['model'],'model-a')
    def test_path_traversal_rejected(self):
        with self.assertRaises(ValueError):chat.load('../notes')

if __name__=='__main__':unittest.main()
