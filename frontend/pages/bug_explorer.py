import streamlit as st
import requests
import pandas as pd

API_URL = "http://localhost:8000/api/v1"

def render():
    st.title("🐞 Bug Explorer & AI Analysis")
    st.markdown("---")

    st.subheader("Registered Projects & Bugs")
    
    try:
        proj_res = requests.get(f"{API_URL}/projects")
        if proj_res.status_code == 200:
            projects = proj_res.json()
            if not projects:
                st.info("No projects registered yet. Go to the Projects tab to add one.")
                return

            proj_options = {f"{p['name']} (ID: {p['id']})": p['id'] for p in projects}
            selected_proj_label = st.selectbox("Select Project", list(proj_options.keys()))
            selected_proj_id = proj_options[selected_proj_label]

            bugs_res = requests.get(f"{API_URL}/projects/{selected_proj_id}/bugs")
            if bugs_res.status_code == 200:
                bugs = bugs_res.json()
                if not bugs:
                    st.info("No bugs detected for this project yet. Run project execution to detect bugs.")
                else:
                    df = pd.DataFrame(bugs)
                    display_cols = [c for c in ["id", "severity", "error_type", "file_path", "line_number", "source", "status"] if c in df.columns]
                    st.dataframe(df[display_cols], use_container_width=True)

                    st.markdown("### 🔍 Bug Details & AI Root-Cause Analysis")
                    bug_options = {f"Bug #{b['id']}: {b['title']}": b for b in bugs}
                    selected_bug_label = st.selectbox("Select Bug to Analyze", list(bug_options.keys()))
                    selected_bug = bug_options[selected_bug_label]

                    with st.expander(f"📌 Bug #{selected_bug['id']} Overview", expanded=True):
                        st.write(f"**Error Type:** `{selected_bug['error_type']}`")
                        st.write(f"**Message:** {selected_bug['message']}")
                        st.write(f"**File:** `{selected_bug['file_path']}:{selected_bug['line_number']}`")
                        st.write(f"**Status:** {selected_bug['status']}")
                        
                        if selected_bug.get("stack_trace"):
                            st.markdown("**Stack Trace:**")
                            st.code(selected_bug["stack_trace"])

                        if st.button("🤖 Run Gemini AI Root-Cause Analysis", key=f"analyze_{selected_bug['id']}"):
                            with st.spinner("Analyzing bug context with Google Gemini AI..."):
                                try:
                                    an_res = requests.post(f"{API_URL}/bugs/{selected_bug['id']}/ai-analyze")
                                    if an_res.status_code == 200:
                                        analysis = an_res.json()
                                        st.success("AI Analysis Complete!")
                                        st.subheader("Root Cause Diagnosis")
                                        st.write(analysis.get("root_cause"))
                                        st.metric("Confidence Score", f"{int(analysis.get('confidence', 0) * 100)}%")

                                        if analysis.get("suggested_fix"):
                                            st.subheader("Suggested Fix")
                                            st.write(analysis["suggested_fix"])

                                        if analysis.get("patch"):
                                            st.subheader("Code Patch Diff")
                                            patch = analysis["patch"]
                                            st.code(f"# File: {patch.get('file')}\n- {patch.get('original_code')}\n+ {patch.get('fixed_code')}", language="diff")
                                    else:
                                        st.error(f"AI Analysis Failed: {an_res.text}")
                                except Exception as e:
                                    st.error(f"Error calling AI analysis API: {e}")
        else:
            st.error("Failed to load projects from backend.")
    except Exception as e:
        st.warning("Backend API is currently offline. Start the backend to view project bugs.")
