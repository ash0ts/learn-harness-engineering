import unittest
import json
import hashlib
import html
from unittest.mock import patch
import publication

class PublicationGuards(unittest.TestCase):
    def test_stale_rendered_totals_are_rejected(self):
        row={'project':'project-01','variant':'minimal','sourceCommit':'fixture','outcome':'passed','estimatedCostUsd':0.1}
        canonical=("project_id = 'overview'\nsaved = json.loads("+repr(json.dumps({'trials':[row]}))+")\n").encode()
        table=[{'project':'project-01','variant':'minimal','source_commit':'fixture','attempts':1,'passed':1,'task_failed':0,'infrastructure_failed':0,'telemetry_missing':0,'known_estimate_usd':0.1,'unknown_cost_attempts':0}]
        def session():return {'cells':[{'outputs':[{'data':{'text/html':"<marimo-table data-data='"+html.escape(json.dumps(json.dumps(table)),quote=True)+"'></marimo-table>"}}]}]}
        self.assertEqual(publication.verify_rendered_aggregates(session(),canonical),1)
        table[0]['attempts']=2
        with self.assertRaisesRegex(RuntimeError,'Displayed aggregates'):
            publication.verify_rendered_aggregates(session(),canonical)
    def test_outputs_are_bound_to_canonical_cell_source(self):
        source=b'@app.cell\ndef _():\n    x = 1\n    return x\n'
        code='x = 1'; checksum=hashlib.md5(code.encode()).hexdigest()
        cell={'id':'one','code':code,'code_hash':checksum}
        output={'id':'one','code_hash':checksum,'outputs':[]}
        def html(): return ('{"notebook": '+json.dumps({'cells':[cell]})+', "session": '+json.dumps({'cells':[output]})+'}').encode()
        publication.verify_rendered_source(html(),source)
        output['code_hash']='stale'
        with self.assertRaisesRegex(RuntimeError,'different cell source'):
            publication.verify_rendered_source(html(),source)
        cell['code']='x = 2'
        with self.assertRaisesRegex(RuntimeError,'differs from canonical'):
            publication.verify_rendered_source(html(),source)
    def test_changed_remote_version_is_not_silently_accepted(self):
        row={'id':'test','expectedRemoteVersion':{'versionIndex':0},'expectedRemoteEditedAt':'old','expectedRemoteSha256':publication.digest(b'source')}
        with patch.object(publication,'remote',return_value={'currentVersion':{'versionIndex':1},'lastSourceEditedAt':'new'}), patch.object(publication,'source_bytes',return_value=b'source'):
            with self.assertRaisesRegex(RuntimeError,'Remote edits detected'):
                publication.check_remote({},row)
    def test_basic_placeholder_is_not_publication_success(self):
        row={'id':'test','file':'forge/notebooks/00-overview.py'}
        with patch.object(publication,'remote',return_value={}), patch.object(publication,'source_bytes',return_value=b'BASIC starter'):
            with self.assertRaisesRegex(RuntimeError,'does not match canonical'):
                publication.verify({},row)

if __name__=='__main__':unittest.main()
