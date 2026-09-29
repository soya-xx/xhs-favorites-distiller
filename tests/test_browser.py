"""Optional real Chromium test: run using the Playwright virtual environment."""
import importlib.util
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import tempfile
import threading
import unittest

SCRIPT = Path(__file__).resolve().parents[1]/'skills/xhs-favorites-distiller/scripts/browser.py'
spec = importlib.util.spec_from_file_location('capture_browser', SCRIPT)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class Page(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-Type', 'text/html; charset=utf-8')
        self.end_headers()
        self.wfile.write(b'''<title>Collection fixture</title><body><h1>Login required</h1>
<a href="/note/one">Example note</a><div id="result"></div>
<script>setTimeout(()=>{let n=Number(localStorage.getItem('visits')||0)+1;
localStorage.setItem('visits',n);document.querySelector('#result').textContent='visit '+n;
document.querySelector('#result').className='ready'},200)</script></body>''')

    def log_message(self, *args):
        pass


@unittest.skipUnless(importlib.util.find_spec('playwright'), 'optional Playwright runtime required')
class BrowserCapture(unittest.TestCase):
    def test_real_browser_dynamic_capture_persistence_and_unverified_login(self):
        import json
        server = ThreadingHTTPServer(('127.0.0.1', 0), Page)
        threading.Thread(target=server.serve_forever, daemon=True).start()
        try:
            with tempfile.TemporaryDirectory() as root:
                url = 'http://127.0.0.1:'+str(server.server_port)
                for visit in (1, 2):
                    output = module.capture(url, root, wait_for='.ready')
                    evidence = json.loads((output/'page.json').read_text())
                    self.assertIn('visit '+str(visit), evidence['text'])
                    self.assertIn('Login required', evidence['text'])
                    self.assertFalse(evidence['complete'])
                    self.assertEqual(evidence['source_status'], 'unverified')
                    self.assertEqual(evidence['http_status'], 200)
                    self.assertEqual(evidence['links'][0]['url'], url+'/note/one')
                    self.assertTrue((output/'page.png').read_bytes().startswith(b'\x89PNG'))
        finally:
            server.shutdown()
            server.server_close()
