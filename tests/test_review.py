"""Independent supported-use regressions, isolated from user state."""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
from test_local import inbox, installer, ROOT, INBOX


class IndependentRuntimeReview(unittest.TestCase):
    def test_cli_stale_decision_fails_without_consuming_updated_note(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            export = root/'notes.json'
            note = dict(source='export', id='stable-id', title='handoff', url='', content='Check recipient access', complete=True)
            cmd = [sys.executable, str(INBOX), '--data-dir', str(root/'state')]
            def run(*args):
                return subprocess.run(cmd+list(args), capture_output=True, text=True, timeout=10)
            export.write_text(json.dumps([note]))
            self.assertEqual(run('ingest',str(export)).returncode,0)
            self.assertEqual(run('assess','export','stable-id','--revision','1','--decision','candidate','--reason','Repeated failed handoffs').returncode,0)
            note['content'] += '; verify recipient permissions'
            export.write_text(json.dumps([note]))
            self.assertEqual(run('ingest',str(export)).returncode,0)
            stale = run('assess','export','stable-id','--revision','1','--decision','skip','--reason','Old judgment')
            self.assertEqual(stale.returncode,2)
            self.assertIn('revised',stale.stderr)
            pending=json.loads(run('pending').stdout)
            self.assertEqual(len(pending),1)
            self.assertEqual(pending[0]['revision'],2)
            self.assertEqual(pending[0]['content'],note['content'])

    def test_rejected_import_creates_no_state_or_partial_records(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp); export=root/'bad.json'
            note=dict(source='export',id='1',title='title',url='',content='text',complete=True)
            export.write_text(json.dumps([note,dict(note,id='2',complete='false')]))
            result=subprocess.run([sys.executable,str(INBOX),'--data-dir',str(root/'state'),'ingest',str(export)],capture_output=True,text=True,timeout=10)
            self.assertEqual(result.returncode,2)
            self.assertFalse((root/'state').exists())

    def test_failed_install_restores_previous_discoverable_version(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp); target=root/'skills/xhs-favorites-distiller'
            target.mkdir(parents=True); (target/'SKILL.md').write_text('previous skill')
            real_move=installer.shutil.move
            def fail_new_install(src,dst,*args,**kwargs):
                if Path(src).name=='skill':
                    raise OSError('Simulated failed installation write')
                return real_move(src,dst,*args,**kwargs)
            with patch.dict(os.environ,{'SAVED_TO_PRACTICE_DATA':str(root/'data')}), patch.object(installer.shutil,'move',side_effect=fail_new_install):
                with self.assertRaisesRegex(OSError,'failed installation'):
                    installer.install(ROOT/'skills/xhs-favorites-distiller',target,replace=True)
            self.assertEqual((target/'SKILL.md').read_text(),'previous skill')
            self.assertEqual(list((root/'data/backups').iterdir()),[])

    def test_source_metadata_update_is_reassessed(self):
        with tempfile.TemporaryDirectory() as tmp:
            db=inbox.connect(tmp)
            try:
                note=dict(source='export',id='1',title='original',url='',content='same body',complete=True)
                inbox.ingest(db,[note]); inbox.assess(db,'export','1',1,'skip','Already covered')
                inbox.ingest(db,[dict(note,title='corrected title')])
                self.assertEqual(inbox.pending(db,5)[0]['revision'],2)
            finally:
                db.close()


if __name__=='__main__':
    unittest.main()
