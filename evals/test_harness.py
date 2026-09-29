import json
import contextlib
import io
import os
import subprocess
import sys
from pathlib import Path
import tempfile
import unittest
from run import fixtures,preserve_exact,selftest,validate,run_stage
from generation import cases,validate as validate_generation

class HarnessTests(unittest.TestCase):
    def test_checker_controls(self):
        self.assertTrue(selftest(fixtures())['pass'])

    def test_nonactivation_dispositions_are_equivalent(self):
        items=fixtures()
        rows={'decisions':[{'id':c['id'],'action':'activate' if c['expected']=='activate' else 'reject','reason':'given evidence'} for c in items]}
        result=validate(rows,items)
        self.assertTrue(result['pass'])
        self.assertFalse(result['cases'][5]['workflow_match'])

    def test_duplicate_output_cannot_replace_missing_case(self):
        items=fixtures();row={'id':items[0]['id'],'action':'activate','reason':'evidence'}
        self.assertFalse(validate({'decisions':[row]*len(items)},items)['pass'])

    def test_cache_input_change_fails_without_overwrite(self):
        with tempfile.TemporaryDirectory() as folder:
            p=Path(folder)/'prompt.txt'
            preserve_exact(p,'original');preserve_exact(p,'original')
            with self.assertRaises(ValueError):preserve_exact(p,'changed')
            self.assertEqual(p.read_text(),'original')

    def test_selftest_needs_no_codex_and_writes_nothing(self):
        root=Path(__file__).resolve().parent
        with tempfile.TemporaryDirectory() as folder:
            output=Path(folder)/'must-not-exist'
            for script in ('run.py','generation.py'):
                env=os.environ.copy();env['PATH']=''
                result=subprocess.run([sys.executable,str(root/script),'--selftest-only','--output-dir',str(output)],env=env,text=True,capture_output=True)
                self.assertEqual(result.returncode,0,result.stderr)
                self.assertFalse(output.exists())

    def test_exit_codes_distinguish_full_failure_and_ablation(self):
        with tempfile.TemporaryDirectory() as folder:
            p=Path(folder);items=fixtures()[:1]
            (p/'output.schema.json').write_text('{}\n');(p/'fixtures.json').write_text('{}\n')
            for arm,expected in [('full',1),('without_value_filter',0)]:
                (p/(arm+'.prompt.txt')).write_text('prompt')
                (p/(arm+'-1.json')).write_text(json.dumps({'decisions':[{'id':items[0]['id'],'action':'reject','reason':'bad decision'}]}))
                with contextlib.redirect_stdout(io.StringIO()):
                    code=run_stage(p,None,[arm],items,{arm:'prompt'},{},validate,1,1,'activation',{})
                self.assertEqual(code,expected)

    def test_zero_repetitions_are_not_a_pass(self):
        root=Path(__file__).resolve().parent
        result=subprocess.run([sys.executable,str(root/'run.py'),'--repeats','0'],text=True,capture_output=True)
        self.assertNotEqual(result.returncode,0)
        self.assertIn('must be positive',result.stderr)

    def test_generation_rejects_low_value_creation(self):
        items=cases();rows={'decisions':[{'id':c['id'],'create_candidate':c['expected_create'],'reason':'evidence'} for c in items]}
        self.assertTrue(validate_generation(rows,items)['pass'])
        rows['decisions'][2]['create_candidate']=True
        self.assertFalse(validate_generation(rows,items)['pass'])

if __name__=='__main__':unittest.main()
