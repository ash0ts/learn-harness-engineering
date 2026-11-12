"""Receive credentials over stdin; keep them out of files and command arguments."""
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import time

settings = json.loads(sys.stdin.readline())
env = dict(os.environ, **settings['environment'])
out = Path('/tmp/workshop-grade')
out.mkdir(exist_ok=True)
started = time.time()
child = subprocess.Popen(['xvfb-run', '-a', 'node', '/tmp/workshop.cjs', '/tmp/scenario.json'], env=env,
                         stdout=subprocess.PIPE, stderr=subprocess.STDOUT, start_new_session=True)
forced = False
try:
    text, _ = child.communicate(timeout=420)
except subprocess.TimeoutExpired:
    forced = True
    os.killpg(child.pid, signal.SIGKILL)
    text, _ = child.communicate(timeout=10)
secret = env.get('WANDB_API_KEY', '').encode()
if secret:
    text = text.replace(secret, b'[redacted]')
(out / 'process.log').write_bytes(text)
(out / 'process.json').write_text(json.dumps({'exitCode': child.returncode, 'forced': forced,
    'elapsedSeconds': time.time() - started, 'childExited': child.poll() is not None}))
sys.exit(child.returncode if not forced else 124)
