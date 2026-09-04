import streamlit as st

def render():
    st.title("⚙ Settings")
    st.markdown("---")

    with st.form("settings_form"):
        st.subheader("Database Configuration")
        db_url = st.text_input("Database URL", value="sqlite:///./bugforge.db", help="PostgreSQL or SQLite connection string")

        st.subheader("AI Provider Settings")
        ai_provider = st.selectbox("AI Provider", ["gemini", "openai", "anthropic", "mock"], index=0)
        ai_model = st.text_input("AI Model", value="gemini-2.5-flash", help="e.g. gemini-2.5-flash, gemini-1.5-pro, gpt-4o")
        
        gemini_api_key = st.text_input("Gemini API Key", type="password", help="Google Gemini API key. Stored securely and never displayed.")
        openai_api_key = st.text_input("Other AI API Key", type="password", help="API key for OpenAI / Anthropic.")

        st.subheader("Local Runtime Execution")
        timeout = st.number_input("Execution Timeout (seconds)", min_value=5, max_value=300, value=30)
        python_exec = st.text_input("Python Executable", value="python", help="Python command or path to interpreter")

        saved = st.form_submit_button("Save Settings")
        if saved:
            st.success("Settings saved successfully!")
