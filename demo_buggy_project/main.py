"""
Task Manager — Main Entry Point (Tkinter UI)
BUG 1: ZeroDivisionError in stats calculation
BUG 5: Delete button deletes wrong index (off-by-one)
BUG 6: Mark Complete button updates internal state but never refreshes the list label
"""
import tkinter as tk
from tkinter import messagebox, font
from tasks import create_task, filter_tasks, sort_tasks
from utils import sanitize_title, format_priority, validate_task_title


# ── State ─────────────────────────────────────────────────────────────────────
task_store: list[dict] = []


# ── Stats (BUG 1: ZeroDivisionError when no tasks exist) ──────────────────────
def get_completion_rate() -> float:
    total = len(task_store)
    done = sum(1 for t in task_store if t["done"])
    # BUG 1: ZeroDivisionError — no guard for total == 0
    return (done / total) * 100


# ── UI Callbacks ───────────────────────────────────────────────────────────────
def add_task_callback():
    raw_title = entry_title.get()
    priority_str = priority_var.get()

    if not validate_task_title(raw_title):
        messagebox.showerror("Error", "Task title must be 1–100 characters.")
        return

    clean_title = sanitize_title(raw_title)
    priority = int(priority_str)
    task = create_task(clean_title, priority)
    task_store.append(task)
    entry_title.delete(0, tk.END)
    refresh_list()
    update_stats()


def delete_task_callback():
    try:
        # BUG 5: Off-by-one — listbox index starts at 0, but we subtract 1 again
        selected_index = listbox.curselection()[0]
        wrong_index = selected_index - 1   # BUG 5: deletes the task ABOVE the selected one
        task_store.pop(wrong_index)
        refresh_list()
        update_stats()
    except IndexError:
        messagebox.showwarning("Warning", "Please select a task to delete.")


def mark_done_callback():
    try:
        selected_index = listbox.curselection()[0]
        task_store[selected_index]["done"] = True
        # BUG 6: refresh_list() is NOT called here — the UI never updates
        # The task stays showing as incomplete in the listbox
        update_stats()
    except IndexError:
        messagebox.showwarning("Warning", "Please select a task to mark as complete.")


def refresh_list():
    listbox.delete(0, tk.END)
    for task in task_store:
        status = "✅" if task["done"] else "⬜"
        priority_label = format_priority(task["priority"]) or ""
        listbox.insert(tk.END, f"{status} {priority_label} {task['title']}")


def update_stats():
    if task_store:
        rate = get_completion_rate()
        lbl_stats.config(text=f"Tasks: {len(task_store)} | Completion: {rate:.0f}%")
    else:
        # BUG 1 triggered: calling get_completion_rate() with 0 tasks causes ZeroDivisionError
        rate = get_completion_rate()
        lbl_stats.config(text=f"Tasks: 0 | Completion: {rate:.0f}%")


# ── Build UI ───────────────────────────────────────────────────────────────────
root = tk.Tk()
root.title("🗒 Task Manager (BugForge Demo)")
root.geometry("560x480")
root.resizable(False, False)
root.configure(bg="#1e1e2e")

DARK   = "#1e1e2e"
CARD   = "#313244"
ACCENT = "#cba6f7"
TEXT   = "#cdd6f4"
GREEN  = "#a6e3a1"
RED    = "#f38ba8"

title_font  = font.Font(family="Segoe UI", size=14, weight="bold")
normal_font = font.Font(family="Segoe UI", size=10)

# Header
tk.Label(root, text="🗒 Task Manager", font=title_font, bg=DARK, fg=ACCENT).pack(pady=(18, 2))
tk.Label(root, text="BugForge Demo Project — contains intentional bugs", font=normal_font, bg=DARK, fg="#6c7086").pack()

# Input area
frame_input = tk.Frame(root, bg=CARD, pady=10, padx=10)
frame_input.pack(fill="x", padx=20, pady=(12, 4))

tk.Label(frame_input, text="Task Title:", bg=CARD, fg=TEXT, font=normal_font).grid(row=0, column=0, sticky="w")
entry_title = tk.Entry(frame_input, width=32, font=normal_font, bg="#45475a", fg=TEXT, insertbackground=TEXT, relief="flat")
entry_title.grid(row=0, column=1, padx=(8, 12))

tk.Label(frame_input, text="Priority:", bg=CARD, fg=TEXT, font=normal_font).grid(row=0, column=2, sticky="w")
priority_var = tk.StringVar(value="1")
priority_menu = tk.OptionMenu(frame_input, priority_var, "1", "2", "3")
priority_menu.config(font=normal_font, bg="#45475a", fg=TEXT, relief="flat", highlightthickness=0)
priority_menu.grid(row=0, column=3, padx=(4, 0))

btn_add = tk.Button(
    frame_input, text="➕ Add Task", font=normal_font,
    bg=ACCENT, fg=DARK, relief="flat", padx=10,
    command=add_task_callback,
)
btn_add.grid(row=1, column=0, columnspan=4, pady=(10, 0), sticky="ew")

# Task list
frame_list = tk.Frame(root, bg=DARK)
frame_list.pack(fill="both", expand=True, padx=20, pady=8)

scrollbar = tk.Scrollbar(frame_list)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

listbox = tk.Listbox(
    frame_list, font=normal_font, bg=CARD, fg=TEXT,
    selectbackground=ACCENT, selectforeground=DARK,
    relief="flat", highlightthickness=0,
    yscrollcommand=scrollbar.set,
)
listbox.pack(fill="both", expand=True)
scrollbar.config(command=listbox.yview)

# Action buttons
frame_actions = tk.Frame(root, bg=DARK)
frame_actions.pack(fill="x", padx=20, pady=(0, 8))

btn_done = tk.Button(
    frame_actions, text="✅ Mark Complete", font=normal_font,
    bg=GREEN, fg=DARK, relief="flat", padx=10,
    command=mark_done_callback,
)
btn_done.pack(side=tk.LEFT, expand=True, fill="x", padx=(0, 4))

btn_delete = tk.Button(
    frame_actions, text="🗑 Delete Task", font=normal_font,
    bg=RED, fg=DARK, relief="flat", padx=10,
    command=delete_task_callback,
)
btn_delete.pack(side=tk.LEFT, expand=True, fill="x", padx=(4, 0))

# Stats bar
lbl_stats = tk.Label(root, text="Tasks: 0 | Completion: —", font=normal_font, bg=DARK, fg="#6c7086")
lbl_stats.pack(pady=(0, 12))

# ── Trigger BUG 1 on startup by calling update_stats with empty list ──────────
update_stats()   # ZeroDivisionError raised here immediately

root.mainloop()
