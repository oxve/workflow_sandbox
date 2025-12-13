import unittest
from unittest.mock import patch, MagicMock
import os
import sys
import json
import io
import shutil
import tempfile

# Add the directory containing the module to sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import automated_test_filters
import junit_mini_parser

class TestAutomatedTestFilters(unittest.TestCase):

    @patch('junit_mini_parser.find_failing_tests')
    def test_main_logic(self, mock_find):

        mock_find.return_value = {
            "path/to/targetA_result.xml": [("ClassA.TestA", "msg")],
            "path/to/targetB_testoutput.xml": [("ClassB.TestB", "msg")]
        }

        # Prepare args
        test_args = [
            'prog',
            '--input-dir', 'tmp_in',
            '--filter-out-dir', 'tmp_filters'
        ]

        with patch.object(sys, 'argv', test_args):
             with patch('os.walk') as mock_walk:
                mock_walk.return_value = [
                   ('tmp_in', [], ['targetA_result.xml', 'targetB_testoutput.xml'])
                ]

                with patch('builtins.open', unittest.mock.mock_open()) as mock_file:
                     with patch('os.makedirs') as mock_mkdirs:
                        # Capture stdout
                         with patch('sys.stdout', new=io.StringIO()) as fake_out:
                            automated_test_filters.main()
                            output = fake_out.getvalue()

                         self.assertIn("FAILED_TARGETS=targetA targetB", output)

                         # Verify writes
                         # We expect 2 writes
                         self.assertEqual(mock_file.call_count, 2)


class TestIntegration(unittest.TestCase):
    def test_full_flow(self):
        # Setup temp directories
        out_dir = tempfile.mkdtemp()
        filter_dir = tempfile.mkdtemp()

        try:
            # Create a fake XML file
            with open(os.path.join(out_dir, 'my_test_result.xml'), 'w') as f:
                f.write('''
<testsuites>
  <testsuite name="Suite1">
    <testcase name="Test1" classname="TestSuite1">
      <failure message="failed"/>
    </testcase>
  </testsuite>
</testsuites>
''')

            # Run main
            test_args = [
                'prog',
                '--input-dir', out_dir,
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
                self.assertEqual(data['failing_tests'], ['Suite1.Test1'])

        finally:
            shutil.rmtree(out_dir)
            shutil.rmtree(filter_dir)

if __name__ == '__main__':
    unittest.main()
