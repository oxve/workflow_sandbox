import xml.etree.ElementTree as ET

def find_failing_tests(xml_files):
  failing_tests = {}
  for xml_file in xml_files:
    try:
      tree = ET.parse(xml_file)
      root = tree.getroot()
      failures = []
      
      # Handle testsuites (root or nested)
      if root.tag == 'testsuites':
        suites = root.findall('testsuite')
      elif root.tag == 'testsuite':
        suites = [root]
      else:
        suites = []

      # Also look for any testsuite under root if structure is different
      if not suites:
         suites = root.findall('.//testsuite')

      for suite in suites:
        for case in suite.findall('testcase'):
          failure = case.find('failure')
          if failure is not None:
             test_name = case.get('name')
             if case.get('classname'):
                 test_name = f"{case.get('classname')}.{test_name}"
             message = failure.get('message', '')
             failures.append((test_name, message))
      
      if failures:
        failing_tests[xml_file] = failures
    except Exception as e:
      print(f"Error parsing {xml_file}: {e}")
  return failing_tests
