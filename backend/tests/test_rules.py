from datetime import datetime

import pytest

from app.domain.rules import validate_hourly_slot


def test_reject_non_hour_slot():
    with pytest.raises(ValueError):
        validate_hourly_slot(datetime(2026, 5, 22, 10, 30), 2, 4)


def test_reject_hours_over_limit():
    with pytest.raises(ValueError):
        validate_hourly_slot(datetime(2026, 5, 22, 10, 0), 6, 4)


def test_accept_valid_slot():
    validate_hourly_slot(datetime(2026, 5, 22, 10, 0), 2, 4)
