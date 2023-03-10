from datetime import datetime

import pytest


@pytest.fixture(scope="module")
def timestamp_str():
    return datetime.now().strftime(r"%Y-%m-%d %H:%M:%S:%f")