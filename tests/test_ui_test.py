import unittest
import os

class TestUITest(unittest.TestCase):

    def test_ui_test_file_exists(self):
        self.assertTrue(os.path.exists("/app/tests/test_ui.py"))

    def test_html_file_exists(self):
        self.assertTrue(os.path.exists("/app/tests/ui_test_demo.html"))
        with open("/app/tests/test_ui.py", "r") as f:
            ui_test_content = f.read()
        self.assertTrue("playwright" in ui_test_content)
        self.assertTrue("run_ui_test" in ui_test_content

if __name__ == '__main__':
    unittest.main()