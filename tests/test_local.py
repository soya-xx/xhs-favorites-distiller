import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
INBOX = ROOT/'skills/xhs-favorites-distiller/scripts/inbox.py'


def load(name, path):
    spec = importlib.util.spec_from_file_location(name,path)
    module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
    return module


inbox = load('inbox',INBOX)
installer = load('installer',ROOT/'scripts/install.py')


class LocalWorkflow(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.db = inbox.connect(self.root/'data')
        self.note = json.loads((ROOT/'examples/notes.json').read_text())[0]

    def tearDown(self):
        self.db.close(); self.temp.cleanup()

    def test_import_decide_repeat_and_changed_source(self):
        self.assertEqual(inbox.ingest(self.db,[self.note])['inserted'],1)
        current = inbox.pending(self.db,5)[0]
        inbox.assess(self.db,current['source'],current['id'],1,'candidate','Recurring handoff failures; compare against existing method')
        self.assertEqual(inbox.pending(self.db,5),[])
        self.assertEqual(inbox.ingest(self.db,[self.note])['unchanged'],1)
        self.assertEqual(inbox.pending(self.db,5),[])
        self.note['content'] += ' Specify who verifies the evidence.'
        self.assertEqual(inbox.ingest(self.db,[self.note])['updated'],1)
        self.assertEqual(inbox.pending(self.db,5)[0]['revision'],2)
        with self.assertRaises(ValueError):
            inbox.assess(self.db,current['source'],current['id'],1,'skip','Stale judgment')
        self.assertEqual(len(inbox.pending(self.db,5)),1)

    def test_invalid_later_item_cannot_partially_import(self):
        with self.assertRaises(ValueError):
            inbox.ingest(self.db,[self.note,dict(self.note,id='bad',complete=True,content='')])
        self.assertEqual(inbox.pending(self.db,5),[])

    def test_duplicate_id_and_false_completeness(self):
        with self.assertRaises(ValueError): inbox.ingest(self.db,[self.note,self.note])
        with self.assertRaises(ValueError): inbox.ingest(self.db,[dict(self.note,complete='false')])
        inbox.ingest(self.db,[dict(self.note,complete=False,content='')])
        self.assertEqual(inbox.pending(self.db,5)[0]['complete'],0)

    def test_same_id_in_two_sources_and_no_premature_consumption(self):
        inbox.ingest(self.db,[self.note,dict(self.note,source='second-export')])
        self.assertEqual(len(inbox.pending(self.db,1)),1)
        self.assertEqual(len(inbox.pending(self.db,5)),2)

    def test_reconsider_with_new_evidence_without_changing_source(self):
        inbox.ingest(self.db,[self.note])
        inbox.assess(self.db,self.note['source'],self.note['id'],1,'needs-evidence','No failed artifact')
        saved=inbox.get_note(self.db,self.note['source'],self.note['id'])
        self.assertEqual(saved['reason'],'No failed artifact')
        inbox.assess(self.db,saved['source'],saved['id'],saved['revision'],'candidate','A new relevant failed artifact was supplied')
        self.assertEqual(inbox.get_note(self.db,saved['source'],saved['id'])['decision'],'candidate')

    def test_cli_handles_export_to_pending_to_decision(self):
        command=[sys.executable,str(INBOX),'--data-dir',str(self.root/'cli')]
        result=subprocess.run(command+['ingest',str(ROOT/'examples/notes.json')],capture_output=True,text=True,timeout=10,check=True)
        self.assertEqual(json.loads(result.stdout)['inserted'],1)
        result=subprocess.run(command+['pending'],capture_output=True,text=True,timeout=10,check=True)
        self.assertEqual(json.loads(result.stdout)[0]['id'],'example-01')
        subprocess.run(command+['assess','reading-export','example-01','--revision','1','--decision','needs-evidence','--reason','No real failed artifact yet'],capture_output=True,text=True,timeout=10,check=True)
        result=subprocess.run(command+['pending'],capture_output=True,text=True,timeout=10,check=True)
        self.assertEqual(json.loads(result.stdout),[])

    def test_install_replacement_preserves_backup_outside_discovery(self):
        source=ROOT/'skills/xhs-favorites-distiller'
        target=self.root/'skills/xhs-favorites-distiller'
        with patch.dict(os.environ,{'SAVED_TO_PRACTICE_DATA':str(self.root/'state')}):
            installer.install(source,target)
            self.assertTrue((target/'scripts/inbox.py').is_file())
            (target/'SKILL.md').write_text('previous version',encoding='utf-8')
            with self.assertRaises(ValueError): installer.install(source,target)
            _, backup=installer.install(source,target,replace=True)
            self.assertEqual((backup/'SKILL.md').read_text(),'previous version')
            self.assertNotIn(self.root/'skills',backup.parents)
            self.assertEqual((source/'SKILL.md').read_text(),(target/'SKILL.md').read_text())


if __name__ == '__main__': unittest.main()
