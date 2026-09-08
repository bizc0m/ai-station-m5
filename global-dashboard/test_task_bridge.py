import importlib.util
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase, main, mock

spec = importlib.util.spec_from_file_location('bridge', Path(__file__).with_name('task_bridge.py'))
bridge = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bridge)

class TaskBridgeTests(TestCase):
    def setUp(self):
        self.temp = TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.patch = mock.patch.object(bridge, 'DATA', self.root / 'jobs')
        self.patch.start()
        self.addCleanup(self.patch.stop)

    def test_duplicate_preview_does_not_create_second_task(self):
        body = {'id': 'abc', 'text': 'Test', 'goal_id': 'station'}
        with mock.patch.object(bridge, 'goals', return_value=[{'id':'station','project':'fixture'}]), mock.patch.object(bridge, 'remote', return_value={'proposal':{'proposal_id':'proposal-abc'}}) as remote:
            self.assertEqual(bridge.preview(body)['id'], bridge.preview(body)['id'])
            self.assertEqual(remote.call_count, 1)

    def test_prefix_is_sent_once_and_retry_is_idempotent(self):
        body = {'id':'prefix', 'text':'Corriger le chat', 'goal_id':'station'}
        with mock.patch.object(bridge,'goals',return_value=[{'id':'station','project':'fixture'}]), mock.patch.object(bridge,'remote',return_value={'proposal':{'proposal_id':'p'}}) as remote:
            job = bridge.preview(body)
            self.assertEqual(job['text'], '##STAI5 — Corriger le chat')
            self.assertEqual(remote.call_args.args[1]['normalized_parameters']['text'], job['text'])
            bridge.preview(body)
            bridge.preview(dict(body, text=job['text']))
            self.assertEqual(remote.call_count, 1)

    def test_uncertain_apply_is_not_replayed(self):
        bridge.save({'id':'abc','status':'preview','proposal_id':'proposal-abc'})
        with mock.patch.object(bridge, 'remote', side_effect=TimeoutError('timeout')) as remote:
            self.assertEqual(bridge.apply('abc')['status'], 'uncertain')
            bridge.apply('abc')
            self.assertEqual(remote.call_count, 1)

    def test_other_turn_reply_cannot_complete_this_task(self):
        job = {'id':'abc','status':'running','session_id':'session-abc','turn_id':'turn-abc'}
        with mock.patch.object(bridge, 'remote', return_value={'session':{},'messages':[{'role':'agent','turn_id':'other','text':'OK'}]}):
            bridge.reconcile(job)
        self.assertEqual(job['status'], 'running')

    def test_agent_reply_is_not_labelled_verified(self):
        job = {'id':'abc','status':'running','session_id':'session-abc','turn_id':'turn-abc'}
        with mock.patch.object(bridge, 'remote', return_value={'session':{},'messages':[{'role':'agent','turn_id':'turn-abc','text':'OK'}]}), mock.patch.object(bridge,'archive'):
            bridge.reconcile(job)
        self.assertEqual(job['status'], 'response_received')

    def test_noteplan_read_preserves_files_and_skips_done(self):
        folder = self.root / 'Notes';folder.mkdir()
        path=folder/'sample.MD';content='Title\n- [ ] Real task\n- [x] Done task\n';path.write_text(content)
        with mock.patch.object(bridge, 'NOTEPLAN', self.root):
            self.assertEqual([x['text'] for x in bridge.notes()['items']], ['Real task'])
        self.assertEqual(path.read_text(), content)

    def test_path_traversal_rejected(self):
        with self.assertRaises(ValueError):bridge.load('../secret')

if __name__ == '__main__':main()
