import streamlit as st
import requests
import pandas as pd

API_URL = "http://localhost:8000/api/v1"

SEVERITY_COLOR = {
    "critical": "🔴",
    "high":     "🟠",
    "medium":   "🟡",
    "low":      "🟢",
}
SOURCE_LABEL = {
    "static":  "📋 Static",
    "runtime": "⚡ Runtime",
    "ast":     "🌲 AST",
}


def render():
    st.title("🐞 Bug Explorer & AI Analysis")
    st.markdown("---")

    # ── Project selector ──────────────────────────────────────────────────────
    try:
        proj_res = requests.get(f"{API_URL}/projects", timeout=5)
    except Exception:
        st.warning("⚠️ Backend API is offline. Start the backend first.")
        return

    if proj_res.status_code != 200 or not proj_res.json():
        st.info("No projects registered yet. Go to **Projects** to add one.")
        return

    projects = proj_res.json()
    proj_map = {f"{p['name']}  (ID {p['id']})": p for p in projects}
    chosen_label = st.selectbox("📁 Select Project", list(proj_map.keys()))
    proj = proj_map[chosen_label]
    proj_id = proj["id"]

    # ── Fetch bugs ────────────────────────────────────────────────────────────
    bugs_res = requests.get(f"{API_URL}/projects/{proj_id}/bugs", timeout=10)
    if bugs_res.status_code != 200:
        st.error("Failed to load bugs.")
        return

    bugs = bugs_res.json()

    # ── Filter bar ────────────────────────────────────────────────────────────
    col_sev, col_src, col_search = st.columns([2, 2, 3])
    with col_sev:
        sev_filter = st.multiselect(
            "Severity",
            ["critical", "high", "medium", "low"],
            default=["critical", "high", "medium", "low"],
        )
    with col_src:
        src_filter = st.multiselect(
            "Source",
            ["runtime", "static", "ast"],
            default=["runtime", "static", "ast"],
        )
    with col_search:
        search = st.text_input("🔍 Search", placeholder="error type, file, message…")

    filtered = [
        b for b in bugs
        if b.get("severity") in sev_filter
        and b.get("source") in src_filter
        and (
            not search or search.lower() in (b.get("error_type") or "").lower()
            or search.lower() in (b.get("message") or "").lower()
            or search.lower() in (b.get("file_path") or "").lower()
        )
    ]

    # ── Summary metrics ───────────────────────────────────────────────────────
    m1, m2, m3, m4, m5 = st.columns(5)
    m1.metric("Total", len(bugs))
    m2.metric("🔴 Critical", sum(1 for b in bugs if b["severity"] == "critical"))
    m3.metric("🟠 High",     sum(1 for b in bugs if b["severity"] == "high"))
    m4.metric("🟡 Medium",   sum(1 for b in bugs if b["severity"] == "medium"))
    m5.metric("🟢 Low",      sum(1 for b in bugs if b["severity"] == "low"))

    st.markdown("---")

    if not filtered:
        st.info("No bugs match the current filters.")
        return

    # ── Bug table ─────────────────────────────────────────────────────────────
    rows = []
    for b in filtered:
        rows.append({
            "ID": b["id"],
            "Sev": SEVERITY_COLOR.get(b["severity"], "⚪") + " " + b["severity"].title(),
            "Type": b["error_type"],
            "Message": (b.get("message") or "")[:80],
            "File": (b.get("file_path") or "").split("/")[-1].split("\\")[-1],
            "Line": b.get("line_number") or "",
            "Src": SOURCE_LABEL.get(b.get("source", ""), b.get("source", "")),
            "Status": b.get("status", "Open"),
        })
    df = pd.DataFrame(rows)
    st.dataframe(df, use_container_width=True, hide_index=True)

    st.markdown("---")
    st.subheader("🔍 Bug Details & AI Root-Cause Analysis")

    bug_options = {f"#{b['id']}  {b['error_type']}  —  {(b.get('message') or '')[:60]}": b for b in filtered}
    selected_label = st.selectbox("Select Bug", list(bug_options.keys()))
    bug = bug_options[selected_label]

    # ── Bug detail card ───────────────────────────────────────────────────────
    col_a, col_b = st.columns(2)
    col_a.markdown(f"**Error Type:** `{bug['error_type']}`")
    col_a.markdown(f"**Severity:** {SEVERITY_COLOR.get(bug['severity'], '')} `{bug['severity']}`")
    col_a.markdown(f"**Source:** {SOURCE_LABEL.get(bug.get('source',''), bug.get('source',''))}")
    col_b.markdown(f"**File:** `{bug.get('file_path') or 'N/A'}`")
    col_b.markdown(f"**Line:** `{bug.get('line_number') or 'N/A'}`")
    col_b.markdown(f"**Status:** `{bug.get('status', 'Open')}`")

    if bug.get("message"):
        st.markdown(f"**Message:** {bug['message']}")

    if bug.get("stack_trace"):
        with st.expander("📜 Stack Trace"):
            st.code(bug["stack_trace"], language="text")

    st.markdown("---")

    # ── AI analysis ───────────────────────────────────────────────────────────
    if st.button("🤖 Run Gemini AI Root-Cause Analysis", use_container_width=True):
        with st.spinner("Sending context to Google Gemini AI…"):
            try:
                an_res = requests.post(f"{API_URL}/bugs/{bug['id']}/ai-analyze", timeout=60)
                if an_res.status_code == 200:
                    analysis = an_res.json()
                    st.success("✅ AI Analysis Complete")

                    c1, c2 = st.columns(2)
                    c1.metric("Confidence", f"{int(analysis.get('confidence', 0) * 100)}%")
                    c2.metric("Severity",   analysis.get("root_cause", "")[:0] or bug["severity"].upper())

                    st.markdown("### 🧠 Root Cause")
                    st.info(analysis.get("root_cause", ""))

                    if analysis.get("suggested_fix"):
                        st.markdown("### 🔧 Suggested Fix")
                        st.success(analysis["suggested_fix"])

                    if analysis.get("patch"):
                        patch = analysis["patch"]
                        st.markdown("### 📝 Code Patch")
                        col_orig, col_fix = st.columns(2)
                        with col_orig:
                            st.markdown("**Original**")
                            st.code(patch.get("original_code", ""), language="python")
                        with col_fix:
                            st.markdown("**Fixed**")
                            st.code(patch.get("fixed_code", ""), language="python")

                        if st.button("⚠️ Apply Fix to Source File", key=f"apply_{bug['id']}"):
                            apply_res = requests.post(f"{API_URL}/bugs/{bug['id']}/apply-fix", timeout=15)
                            if apply_res.status_code == 200:
                                d = apply_res.json()
                                st.success(d["message"])
                                with st.expander("Unified Diff"):
                                    st.code(d.get("diff", ""), language="diff")
                            else:
                                st.error(f"Apply failed: {apply_res.json().get('detail', apply_res.text)}")

                    if analysis.get("facts"):
                        with st.expander("📌 Facts"):
                            for f in analysis["facts"]:
                                st.markdown(f"- {f}")

                    if analysis.get("risks"):
                        with st.expander("⚠️ Risks"):
                            for r in analysis["risks"]:
                                st.markdown(f"- {r}")

                    if analysis.get("tests_to_run"):
                        with st.expander("🧪 Tests to Run"):
                            for t in analysis["tests_to_run"]:
                                st.markdown(f"- {t}")
                else:
                    st.error(f"AI Analysis failed: {an_res.json().get('detail', an_res.text)}")
            except Exception as e:
                st.error(f"Error calling AI analysis: {e}")
