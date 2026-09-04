"""
Task Manager Data Layer
BUG 2: TypeError when building task summary string (int + str)
BUG 3: NameError - variable used before assignment
"""
from datetime import datetime


def create_task(title: str, priority: int = 1) -> dict:
    return {
        "title": title,
        "priority": priority,
        "done": False,
        "created_at": datetime.now().isoformat(),
    }


def get_task_summary(task: dict) -> str:
    # BUG 2: TypeError — priority is int, cannot concatenate with str directly
    summary = "Task: " + task["title"] + " | Priority: " + task["priority"]
    return summary


def filter_tasks(tasks: list, show_done: bool = False) -> list:
    # BUG 3: NameError — 'result' is referenced before assignment in the else branch
    if show_done:
        result = [t for t in tasks if t["done"]]
    else:
        result = [t for t in tasks if not t["done"]]

    # Simulating a code path where result was never set (logic gap)
    return ressult  # NameError: 'ressult' is misspelled


def sort_tasks(tasks: list) -> list:
    return sorted(tasks, key=lambda t: t["priority"], reverse=True)
