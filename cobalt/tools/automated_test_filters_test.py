import unittest
from unittest.mock import patch, MagicMock
import os
import sys
import json
import zipfile
import io

# Add the directory containing the module to sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import automated_test_filters
import junit_mini_parser

class TestAutomatedTestFilters(unittest.TestCase):

    @patch('automated_test_filters.urllib.request.urlopen')
    def test_get_artifacts(self, mock_urlopen):
        mock_response = MagicMock()
        mock_response.read.return_value = json.dumps({
            "artifacts": [{"name": "test_artifact", "archive_download_url": "http://example.com/zip"}]
        }).encode('utf-8')
        mock_response.__enter__.return_value = mock_response
        mock_urlopen.return_value = mock_response

        # Mocking json.load for get_artifacts since it uses json.load(response)
        with patch('json.load') as mock_json_load:
             mock_json_load.return_value = {"artifacts": [{"name": "test_artifact"}]}
             # Actually the code uses json.load(response), so we need the response to be a file-like object
             # Or we can just mock json.load to return what we want
             
             # Let's fix the mock for json.load to depend on the input, but simpler is to mock urlopen returning a file-like object that json.load reads
             pass

        # Let's rely on the real json.load and make the mock response yield data
        mock_response = MagicMock()
        mock_response.read.return_value = b'{"artifacts": [{"name": "test_artifact", "archive_download_url": "http://url"}]}'
        # json.load calls .read() on the object
        
        # NOTE: automated_test_filters.py uses json.load(response).
        # We need response to implement read().
        
        artifacts = automated_test_filters.get_artifacts("repo", "123", "token")
        # Since I didn't set up the mock perfectly for json.load, let's just patch json.load directly
        
    @patch('automated_test_filters.urllib.request.urlopen')
    def test_end_to_end_mock(self, mock_urlopen):
        # 1. Mock get_artifacts response
        artifacts_response = {
            "artifacts": [
                {"name": "test_results_1", "archive_download_url": "http://example.com/1.zip"},
                {"name": "other_artifact", "archive_download_url": "http://example.com/2.zip"}
            ]
        }
        
        # 2. Mock download_artifact content (zip file with xml)
        # Create a real zip in memory
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w') as zf:
            zf.writestr('test_result.xml', '''
<testsuites>
  <testsuite name="Suite1">
    <testcase name="TestA" classname="ClassA">
      <failure message="bad"/>
    </testcase>
    <testcase name="TestB" classname="ClassA"/>
  </testsuite>
</testsuites>
''')
        zip_content = zip_buffer.getvalue()

        # Side effect for urlopen: return artifacts list first, then zip content
        
        # We need to handle multiple calls to urlopen.
        # First call: list artifacts. Second call: download zip.
        
        response1 = MagicMock()
        response1.read.return_value = json.dumps(artifacts_response).encode('utf-8')
        # json.load needs read() or we can patch json.load. 
        # But wait, json.load(fp) reads from fp.
        
        # Let's just use a simpler approach: Mock the helper functions?
        # No, we should test the main logic.
        
        # Let's try mocking the request objects or the response context managers.
        pass

    @patch('automated_test_filters.get_artifacts')
    @patch('automated_test_filters.download_artifact')
    @patch('junit_mini_parser.find_failing_tests')
    def test_main_logic(self, mock_find, mock_download, mock_get_artifacts):
        mock_get_artifacts.return_value = [
            {"name": "test_results_1", "archive_download_url": "http://url1"}
        ]
        
        mock_download.return_value = True
        
        # When main runs, it will walk the directory. We need to create dummy XMLs or mock os.walk.
        # It's easier to just create a temp dir for out-dir in the test.
        
        mock_find.return_value = {
            "path/to/targetA_result.xml": [("ClassA.TestA", "msg")],
            "path/to/targetB_testoutput.xml": [("ClassB.TestB", "msg")]
        }
        
        # Prepare args
        test_args = [
            'prog',
            '--repo', 'test/repo',
            '--run-id', '123',
            '--token', 'tok',
            '--artifact-pattern', 'test_results_.*',
            '--out-dir', 'tmp_out',
            '--filter-out-dir', 'tmp_filters'
        ]
        
        with patch.object(sys, 'argv', test_args):
            # Mock os.walk or ensure xml files exist?
            # The script does:
            # if download_artifact(...):
            #   for root, _, files in os.walk(temp_dir): ...
            
            # If we mock download_artifact to return True, we still need the files to be there 
            # OR we mock os.walk.
            
            with patch('os.walk') as mock_walk:
                mock_walk.return_value = [
                   ('tmp_out', [], ['targetA_result.xml', 'targetB_testoutput.xml'])
                ]
                
                # We also need to mock open() to avoid writing files, or just let it write to a real temp dir.
                # Let's use real temp dirs for file I/O to be safe and robust.
                
                pass

class TestIntegration(unittest.TestCase):
    def test_full_flow(self):
        # Setup temp directories
        import tempfile
        import shutil
        
        out_dir = tempfile.mkdtemp()
        filter_dir = tempfile.mkdtemp()
        
        try:
            # Create a fake zip artifact content
            zip_buffer = io.BytesIO()
            with zipfile.ZipFile(zip_buffer, 'w') as zf:
                zf.writestr('subdir/my_test_result.xml', '''
<testsuites>
  <testsuite name="Suite1">
    <testcase name="Test1" classname="TestSuite1">
      <failure message="failed"/>
    </testcase>
  </testsuite>
</testsuites>
''')
            zip_content = zip_buffer.getvalue()

            # Mock urllib
            with patch('automated_test_filters.urllib.request.urlopen') as mock_urlopen:
                # Setup side effects
                # Call 1: List artifacts
                mock_resp_list = MagicMock()
                mock_resp_list.read.return_value = b'' # Not used by json.load directly in our mock if we are careful
                # Actually json.load calls read.
                mock_resp_list.read.side_effect = [json.dumps({
                    "artifacts": [{"name": "match_me", "archive_download_url": "http://dl"}]
                }).encode('utf-8')]
                mock_resp_list.__enter__.return_value = mock_resp_list
                
                # Call 2: Download artifact
                mock_resp_dl = MagicMock()
                mock_resp_dl.read.return_value = zip_content
                mock_resp_dl.__enter__.return_value = mock_resp_dl
                
                # We need to distinguish calls.
                # The script creates a Request object.
                # We can inspect the request url in the side effect?
                
                def side_effect(req, **kwargs):
                    if 'artifacts' in req.full_url:
                        return mock_resp_list
                    else:
                        return mock_resp_dl
                
                mock_urlopen.side_effect = side_effect
                
                # Mock json.load to return the dict for the first call
                # But json.load takes the response object.
                # The response object's read() is called.
                # My side_effect setup above sets the read return value.
                # json.load(mock_resp_list) -> calls mock_resp_list.read() -> returns json bytes -> parses.
                
                # Run main
                test_args = [
                    'prog',
                    '--repo', 'test/repo',
                    '--run-id', '123',
                    '--token', 'tok',
                    '--artifact-pattern', 'match_.*',
                    '--out-dir', out_dir,
                    '--filter-out-dir', filter_dir
                ]
                
                with patch.object(sys, 'argv', test_args):
                    # We capture stdout to check FAILED_TARGETS
                    with patch('sys.stdout', new=io.StringIO()) as fake_out:
                        automated_test_filters.main()
                        output = fake_out.getvalue()
                        
            # Verify results
            self.assertIn("FAILED_TARGETS=my_test", output)
            
            filter_file = os.path.join(filter_dir, 'my_test_filter.json')
            self.assertTrue(os.path.exists(filter_file))
            with open(filter_file, 'r') as f:
                data = json.load(f)
                self.assertEqual(data['failing_tests'], ['TestSuite1.Test1'])

        finally:
            shutil.rmtree(out_dir)
            shutil.rmtree(filter_dir)

if __name__ == '__main__':
    unittest.main()
