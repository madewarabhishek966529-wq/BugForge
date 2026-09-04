# Demo Buggy Task Manager

A deliberately broken Python project for testing BugForge analysis.

## Bugs Included

| # | Type | Location | Description |
|---|------|----------|-------------|
| 1 | RuntimeError | `main.py:10` | Division by zero in stats calculation |
| 2 | TypeError | `tasks.py:18` | Adding `int` to `str` instead of converting |
| 3 | NameError | `tasks.py:31` | Variable used before assignment |
| 4 | AttributeError | `utils.py:12` | Calling `.strip()` on an integer |
| 5 | Logic Bug | `main.py` | Delete button deletes wrong task index |
| 6 | Logic Bug | `main.py` | Mark Complete button never updates the label |
| 7 | Unused Import | `utils.py:1` | `import os` is never used |
| 8 | Missing Return | `utils.py:20` | Function falls off without returning a value |

## Running the Project

```bash
python main.py
```
