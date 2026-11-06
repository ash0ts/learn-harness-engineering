import unittest
from unittest.mock import patch
import publication

class PublicationGuards(unittest.TestCase):
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
