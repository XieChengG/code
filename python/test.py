import os
import sys
import unittest


base_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(base_dir)

import analysis_nginx_logfile


class TestAnalysisNginxLogfile(unittest.TestCase):
    def test_transfer_dict(self):
        result = analysis_nginx_logfile.transfer_dict(
            r"c:\Users\ye\PycharmProjects\code\python/nginx.log"
        )
        self.assertIsInstance(result, list, "函数应该返回一个列表")


if __name__ == "__main__":
    unittest.main()
