"""Guidance must describe the actual saved state without dispatching work."""
import sys,tempfile,json
from pathlib import Path
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from workshop_workspace import WorkshopWorkspace
from workshop_teaching import LABS
from workshop_cells import action_cells
class GuidanceTest(unittest.TestCase):
    def test_retry_needs_verified_recovery_and_never_bypasses_approval(self):
        learner=WorkshopWorkspace.__new__(WorkshopWorkspace)
        learner.ledger=lambda:{'reservations':{'unsettled':2}}
        learner.incomplete_operations=lambda:[]
        self.assertFalse(learner.workshop_controller_terminal({'node':'recover'}))
        learner.ledger=lambda:{'reservations':{}}
        learner.incomplete_operations=lambda:[{'cleanup':'unknown'}]
        self.assertFalse(learner.workshop_controller_terminal({'status':'blocked'}))
        learner.incomplete_operations=lambda:[]
        self.assertTrue(learner.workshop_controller_terminal({'node':'recover'}))
        self.assertFalse(learner.workshop_controller_terminal({'node':'recover','pending':{'id':'same'}}))
        self.assertFalse(learner.workshop_controller_terminal({'node':'approval'}))
    def test_every_lab_has_distinct_named_actions_and_evidence_questions(self):
        self.assertEqual(len(LABS),8)
        labels=[]
        for key,lab in LABS.items():
            self.assertGreater(len(lab['inspect']),100)
            self.assertGreater(len(lab['edit']),100)
            for source in action_cells(key):compile(source,key,'exec')
            labels.extend(action[1] for action in lab['actions'])
        self.assertEqual(len(set(labels)),len(labels))
    def test_next_action_tracks_dirty_saved_and_pending_approval(self):
        learner=WorkshopWorkspace.__new__(WorkshopWorkspace)
        learner.state={};learner.workshop_controller=lambda:None
        learner.blocked=lambda:None;learner.connected=False
        learner.workshop_files=lambda:{'files':{'file.ts':'saved'}}
        self.assertIn('Prepare',learner.workshop_next_step({}))
        learner.state={'workshop':{'ready':True,'draftSnapshot':'snapshot','draftSha256':'hash'}}
        self.assertIn('Save and check',learner.workshop_next_step({'file.ts':'unsaved'}))
        learner.state['workshop']['lastCheck']={'snapshotSha256':'hash'}
        self.assertIn('Connect',learner.workshop_next_step({'file.ts':'saved'}))
        learner.workshop_controller=lambda:{'node':'approval'}
        self.assertIn('approve or reject',learner.workshop_next_step({'file.ts':'changed'}))
if __name__=='__main__':unittest.main()
