import streamlit as st
import requests
import tkinter as tk
from tkinter import filedialog
from pathlib import Path

API_URL = "http://localhost:8000/api/v1"


def _pick_folder() -> str:
    """Opens a native OS folder picker dialog and returns the selected path."""
    root = tk.Tk()
    root.withdraw()          # Hide the main tkinter window
    root.wm_attributes("-topmost", True)   # Bring dialog to front
    folder = filedialog.askdirectory(title="Select Project Folder")
    root.destroy()
    return folder or ""


def render():
    st.title("📁 Projects")
    st.markdown("---")

    # ── Initialise session state ──────────────────────────────────────────
    if "selected_folder" not in st.session_state:
        st.session_state["selected_folder"] = ""
    if "project_name_auto" not in st.session_state:
        st.session_state["project_name_auto"] = ""

    # ── Add Local Project ─────────────────────────────────────────────────
    st.subheader("Add Local Project")

    # Folder picker row (lives OUTSIDE the form so the button triggers immediately)
    col_path, col_btn = st.columns([4, 1])
    with col_path:
        folder_display = st.text_input(
            "Local Project Path",
            value=st.session_state["selected_folder"],
            placeholder="e.g. C:/Projects/MyService",
            key="folder_input",
        )
        # Keep session state in sync if user edits manually
        if folder_display != st.session_state["selected_folder"]:
            st.session_state["selected_folder"] = folder_display
            if folder_display:
                st.session_state["project_name_auto"] = Path(folder_display).name

    with col_btn:
        st.markdown("<br>", unsafe_allow_html=True)   # vertical alignment
        if st.button("📂 Browse…", help="Open system folder picker"):
            chosen = _pick_folder()
            if chosen:
                st.session_state["selected_folder"] = chosen
                st.session_state["project_name_auto"] = Path(chosen).name
                st.rerun()

    with st.form("add_project_form"):
        project_name = st.text_input(
            "Project Name",
            value=st.session_state.get("project_name_auto", ""),
            placeholder="e.g. My Python Service",
        )
        submitted = st.form_submit_button("➕ Add Project", use_container_width=True)

        if submitted:
            path = st.session_state["selected_folder"]
            if not project_name or not path:
                st.error("Please provide a project name and select a project folder.")
            elif not Path(path).is_dir():
                st.error(f"Path does not exist or is not a directory: `{path}`")
            else:
                try:
                    res = requests.post(
                        f"{API_URL}/projects",
                        json={"name": project_name, "path": path},
                    )
                    if res.status_code == 201:
                        st.success(f"✅ Project **{project_name}** added successfully!")
                        st.session_state["selected_folder"] = ""
                        st.session_state["project_name_auto"] = ""
                    else:
                        st.error(f"Error adding project: {res.text}")
                except Exception as e:
                    st.error(f"Failed to connect to backend API: {e}")

    # ── Registered Projects ───────────────────────────────────────────────
    st.markdown("---")
    st.subheader("Registered Projects")

    st.warning(
        "⚠️ **Warning:** BugForge will execute code from this project on your "
        "local computer. Only analyze and run projects that you trust."
    )
    confirm_exec = st.checkbox(
        "I understand and confirm that I trust local project execution on this machine."
    )

    try:
        res = requests.get(f"{API_URL}/projects")
        if res.status_code == 200:
            projects = res.json()
            if not projects:
                st.info("No projects registered yet. Use the form above to add one.")
            else:
                for proj in projects:
                    with st.expander(f"📌 {proj['name']}  —  `{proj['path']}`"):
                        c1, c2 = st.columns(2)
                        c1.write(f"**Language:** {proj['language']}")
                        c2.write(f"**Added:** {proj['created_at'][:19].replace('T', ' ')}")

                        entry_point = st.text_input(
                            "Entry File",
                            value="main.py",
                            key=f"entry_{proj['id']}",
                            help="Relative path to the Python file to execute (e.g. main.py or src/app.py)",
                        )

                        act1, act2, act3 = st.columns(3)

                        # Scan
                        if act1.button("🔍 Scan", key=f"scan_{proj['id']}", use_container_width=True):
                            try:
                                r = requests.post(f"{API_URL}/projects/{proj['id']}/scan")
                                if r.status_code == 200:
                                    d = r.json()
                                    st.success(
                                        f"Found **{d['files_found']}** Python files. "
                                        f"Entry points: `{', '.join(d['entry_points']) or 'none detected'}`"
                                    )
                                    if d["file_map"]:
                                        with st.expander("📄 File Map"):
                                            st.code("\n".join(d["file_map"]))
                                else:
                                    st.error(f"Scan failed: {r.text}")
                            except Exception as e:
                                st.error(f"Error scanning project: {e}")

                        # Run
                        if act2.button("▶ Run", key=f"run_{proj['id']}", use_container_width=True):
                            if not confirm_exec:
                                st.error(
                                    "Execution blocked: tick the confirmation checkbox above first."
                                )
                            else:
                                with st.spinner(f"Executing `{entry_point}` locally…"):
                                    try:
                                        r = requests.post(
                                            f"{API_URL}/projects/{proj['id']}/run",
                                            json={"entry_point": entry_point},
                                        )
                                        if r.status_code == 200:
                                            result = r.json()
                                            if result.get("timed_out"):
                                                st.error("⏱ Execution Timed Out!")
                                            elif result.get("exit_code") == 0:
                                                st.success("✅ Execution completed successfully.")
                                            else:
                                                st.warning(
                                                    f"Process exited with code {result.get('exit_code')}"
                                                )
                                            if result.get("stdout"):
                                                st.markdown("**stdout**")
                                                st.code(result["stdout"])
                                            if result.get("stderr"):
                                                st.markdown("**stderr**")
                                                st.code(result["stderr"])
                                        else:
                                            st.error(f"Run failed: {r.text}")
                                    except Exception as e:
                                        st.error(f"Error running project: {e}")

                        # Open folder
                        if act3.button("📂 Open Folder", key=f"open_{proj['id']}", use_container_width=True):
                            import subprocess, os, sys
                            path = proj["path"]
                            if sys.platform == "win32":
                                os.startfile(path)
                            elif sys.platform == "darwin":
                                subprocess.Popen(["open", path])
                            else:
                                subprocess.Popen(["xdg-open", path])
        else:
            st.error("Failed to load projects from backend API.")
    except Exception:
        st.warning("⚠️ Backend API is currently offline. Start the backend to view project data.")
