import io
import importlib.util
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

spec=importlib.util.spec_from_file_location('course_models',Path(__file__).parents[1]/'scripts/models.py')
models=importlib.util.module_from_spec(spec)
spec.loader.exec_module(models)

class PublicationTests(unittest.TestCase):
    def test_retry_fingerprint_ignores_publication_receipts_and_transient_logs(self):
        with tempfile.TemporaryDirectory() as directory:
            file=Path(directory,'trial.json')
            record={'id':'sample','sourceCommit':'a'*40,'evidence':['actor/result.json'],'path':'/Users/sample/course/local-results/x'}
            file.write_text(json.dumps(record))
            Path(directory,'patch.diff').write_text('immutable patch')
            _,projected,_,first=models.payload(file)
            self.assertNotIn('/Users/',json.dumps(projected))
            record.update(publicationStatus='verified',wandbRunUrl='https://example.test/run',artifactUrl='https://example.test/artifact')
            file.write_text(json.dumps(record))
            Path(directory,'models.log').write_text('retry log')
            Path(directory,'publication.json').write_text('{}')
            self.assertEqual(models.payload(file)[3],first)
            Path(directory,'patch.diff').write_text('different patch')
            self.assertNotEqual(models.payload(file)[3],first)
    def test_network_read_errors_never_mean_artifact_absence(self):
        class Offline:
            def artifact_collections(self,**kwargs):raise ConnectionError('offline')
        with patch.object(models,'artifact_collection_exists',side_effect=ConnectionError('offline')),self.assertRaises(ConnectionError):models.remote_artifact(Offline(),'team','private','trial-x','checksum')
    def test_credentials_stop_publication_before_remote_writes(self):
        with tempfile.TemporaryDirectory() as directory,patch.dict(os.environ,{'WANDB_API_KEY':'fixture-private-secret'}):
            file=Path(directory,'trial.json');file.write_text('{"id":"sample"}')
            Path(directory,'worker.log').write_text('fixture-private-secret')
            with self.assertRaisesRegex(RuntimeError,'Credential'):models.payload(file)



class CollectionLookupTests(unittest.TestCase):
    def test_new_collection_uses_exact_list_query_not_throwing_name_lookup(self):
        response={'data':{'project':{'access':'PRIVATE','artifactType':{'artifactCollections':{'edges':[], 'pageInfo':{'hasNextPage':False}}}}}}
        def request(req, **kwargs):
            payload=json.loads(req.data)
            self.assertNotIn('artifactCollection(name:',payload['query'])
            self.assertEqual(json.loads(payload['variables']['f']),{'name':'trial-new'})
            return io.BytesIO(json.dumps(response).encode())
        with patch.dict(os.environ,{'WANDB_API_KEY':'test-only'}):
            self.assertFalse(models.artifact_collection_exists('team','private','course-evidence','trial-new',request))
            response['data']['project']['artifactType']['artifactCollections']['edges']=[{'node':{'name':'trial-new'}}]
            self.assertTrue(models.artifact_collection_exists('team','private','course-evidence','trial-new',request))
            response['data']['project']['artifactType']['artifactCollections']['pageInfo']['hasNextPage']=True
            with self.assertRaises(RuntimeError):models.artifact_collection_exists('team','private','course-evidence','trial-new',request)

    def test_missing_type_is_absent_only_after_explicit_private_query(self):
        response={'data':{'project':{'access':'PRIVATE','artifactType':None}}}
        with patch.dict(os.environ,{'WANDB_API_KEY':'test-only'}):
            self.assertFalse(models.artifact_collection_exists('team','private','new-type','new-name',lambda *a,**k:io.BytesIO(json.dumps(response).encode())))
    def test_api_error_and_incomplete_response_cannot_create_artifacts(self):
        for response in [{'errors':[{'message':'denied'}]}, {'data':{'project':{'access':'PRIVATE'}}}, {'data':{'project':{'access':'PUBLIC','artifactType':None}}}]:
            with patch.dict(os.environ,{'WANDB_API_KEY':'test-only'}),self.assertRaises(RuntimeError):
                models.artifact_collection_exists('team','private','new-type','new-name',lambda *a,**k:io.BytesIO(json.dumps(response).encode()))

if __name__=='__main__':unittest.main()
