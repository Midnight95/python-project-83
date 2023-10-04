from page_analyzer.config import get_last_status_codes
from datetime import date


def test_get_last_status_codes():
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


class MockPage:
    def __init__(self, content, status_code=200):
        self.text = content
        self.status_code = status_code
