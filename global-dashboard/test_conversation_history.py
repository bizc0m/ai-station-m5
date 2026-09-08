import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
import conversation_history as h

class HistoryTest(unittest.TestCase):
    def test_merges_and_sorts_without_creating_sessions(self):
        with TemporaryDirectory() as folder:
            sid = 'b' * 32
            (Path(folder) / (sid + '.json')).write_text('{}')
            local = {'session': {'destination': 'm2', 'model': 'model'}, 'messages': [{'role': 'user', 'text': 'Ma question', 'created_at': '2026-09-08T10:00:00Z'}]}
            with patch.object(h.local_conversation, 'ROOT', Path(folder)), patch.object(h.local_conversation, 'load', return_value=local), patch.object(h.task_bridge, 'goals', return_value=[{'id':'goal','title':'Projet'}]), patch.object(h.task_bridge, 'remote', return_value={'sessions':[{'session_id':'a'*32,'goal_id':'goal','agent_id':'codex','updated_at':'2026-09-07T10:00:00Z'}]}) as remote:
                result = h.history()
                self.assertEqual([x['id'] for x in result['items']], [sid, 'a'*32])
                self.assertEqual(result['items'][0]['title'], 'Ma question')
                remote.assert_called_once_with('/api/chat/sessions')
    def test_remote_failure_is_visible_and_local_history_remains(self):
        with TemporaryDirectory() as folder:
            with patch.object(h.local_conversation,'ROOT',Path(folder)), patch.object(h.task_bridge,'goals',return_value=[]), patch.object(h.task_bridge,'remote',side_effect=OSError('offline')):
                result=h.history()
                self.assertEqual(result['items'],[])
                self.assertTrue(result['errors'])
if __name__ == '__main__': unittest.main()
