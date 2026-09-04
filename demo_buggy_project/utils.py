"""
Utility helpers for Task Manager
BUG 4: AttributeError — calling .strip() on an integer
BUG 7: Unused import (os)
BUG 8: Missing return value in format_priority()
"""
import os   # BUG 7: never used


PRIORITY_LABELS = {1: "Low", 2: "Medium", 3: "High"}


def sanitize_title(title) -> str:
    # BUG 4: AttributeError if title is accidentally passed as int
    return title.strip().title()


def format_priority(priority: int) -> str:
    label = PRIORITY_LABELS.get(priority, "Unknown")
    if label != "Unknown":
        return f"[{label}]"
    # BUG 8: Missing return — falls off here when priority is invalid,
    # returning None instead of a string, which breaks string concatenation later


def validate_task_title(title: str) -> bool:
    if len(title) == 0:
        return False
    if len(title) > 100:
        return False
    return True
