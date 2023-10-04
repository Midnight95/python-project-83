from page_analyzer.config import *


def test_get_last_status_codes():
    # Test case 1: Ensuring the returned dictionary has the latest status codes for each URL
    checks = [
        {'id': 1, 'url_id': 1, 'status_code': 200, 'created_at': date.today()},
        {'id': 2, 'url_id': 1, 'status_code': 404, 'created_at': date.today()},
        {'id': 3, 'url_id': 2, 'status_code': 200, 'created_at': date.today()},
    ]
    expected_result = {
        1: {'id': 2, 'status_code': 404, 'created_at': date.today()},
        2: {'id': 3, 'status_code': 200, 'created_at': date.today()}
    }
    assert get_last_status_codes(checks) == expected_result


# Helper class for mocking the page response object
class MockPage:
    def __init__(self, content, status_code=200):
        self.text = content
        self.status_code = status_code
