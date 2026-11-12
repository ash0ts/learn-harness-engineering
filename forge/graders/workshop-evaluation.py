"""Execute the student's calculation and logging call without exposing credentials.

The coordinator publishes these exact recorded run.log calls to the stable W&B run.
"""
import importlib.util
import json
import pathlib
import sys

source, checks_file, output = map(pathlib.Path, sys.argv[1:])
spec = importlib.util.spec_from_file_location('student_evaluation', source)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
calls = []


class RecordedRun:
    def log(self, metrics, step=0):
        if step != 0 or not isinstance(metrics, dict) or any(not k.startswith('student/') or not isinstance(v, (int, float)) for k, v in metrics.items()):
            raise ValueError('Log numeric student/ metrics at step 0')
        calls.append({'metrics': metrics, 'step': step})


probe = [{'passed': True}, {'passed': False}, {'passed': True}]
expected = module.evaluate(probe)
if expected.get('checks_passed') != 2 or expected.get('checks_total') != 3:
    raise ValueError('Evaluation must distinguish two passed checks out of three')
checks = json.loads(checks_file.read_text())['checks']
metrics = module.evaluate(checks)
module.log_evaluation(RecordedRun(), metrics)
if len(calls) != 1 or calls[0]['metrics'] != {'student/' + key: value for key, value in metrics.items()}:
    raise ValueError('The student logging function did not log its evaluation')
output.write_text(json.dumps({'source': 'workshop/evaluation.py', 'metrics': metrics, 'calls': calls}, indent=2))
