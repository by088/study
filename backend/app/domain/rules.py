from datetime import datetime


def validate_hourly_slot(start_at: datetime, hours: int, max_hours: int) -> None:
    if start_at.minute != 0 or start_at.second != 0:
        raise ValueError("Reservation must start at exact hour.")
    if hours < 1 or hours > max_hours:
        raise ValueError(f"Reservation hours must be between 1 and {max_hours}.")
