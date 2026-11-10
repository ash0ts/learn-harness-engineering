import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

spec=importlib.util.spec_from_file_location('protocol_five_schedule',Path(__file__).parents[1]/'scripts/protocol5.py')
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)

class CampaignScheduleTests(unittest.TestCase):
    def test_unknown_ledger_stops_before_dispatch(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);schedule=root/'schedule.json'
            module.write(schedule,{'sourceCommit':'a'*40,'inputsSha256':{},'steps':[{'id':'one','kind':'qualification','status':'prepared'}]})
            module.write(root/'budget.json',{'halted':'Missing usage','reservations':{'old':2}})
            with patch.object(module.subprocess,'check_output',return_value='a'*40),patch.object(module.subprocess,'Popen',side_effect=AssertionError):
                with self.assertRaisesRegex(RuntimeError,'Unresolved accounting'):module.run(schedule,root)
            self.assertEqual(module.read(schedule)['steps'][0]['status'],'prepared')
    def test_interrupted_step_never_replays(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);schedule=root/'schedule.json'
            module.write(schedule,{'sourceCommit':'a'*40,'inputsSha256':{},'steps':[{'id':'one','kind':'comparisons','status':'running'}]})
            with patch.object(module.subprocess,'check_output',return_value='a'*40),patch.object(module.subprocess,'Popen',side_effect=AssertionError):
                with self.assertRaisesRegex(RuntimeError,'interrupted'):module.run(schedule,root)
    def test_timer_keeps_real_duration_and_stable_checkpoint(self):
        step={'id':'fixed','kind':'loop','mode':'timer'}
        first=module.command(step,Path('/evidence'),'a'*40)
        self.assertEqual(first,module.command(step,Path('/evidence'),'a'*40))
        self.assertEqual(first[first.index('--duration-seconds')+1],'7200')
        self.assertEqual(first[first.index('--max-rounds')+1],'8')
    def test_control_and_pair_commands_cannot_approve_graphs(self):
        control=module.command({'id':'fixed','kind':'control','project':'project-04','control':'reference'},Path('/evidence'),'a'*40)
        self.assertIn('control-project-04-reference-fixed',control)
        pair=module.command({'id':'pair','kind':'verification-pairs','trial':'candidate'},Path('/evidence'),'a'*40)
        self.assertIn('graph-pairs',pair)
        self.assertNotIn('--decision',pair)

if __name__=='__main__':unittest.main()
