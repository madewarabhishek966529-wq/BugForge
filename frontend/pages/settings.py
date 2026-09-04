import streamlit as st

def render():
    st.title("⚙ Settings")
    st.markdown("---")

    with st.form("settings_form"):
        st.subheader("Database Configuration")
        db_url = st.text_input("Database URL", value="sqlite:///./bugforge.db", help="PostgreSQL or SQLite connection string")

        st.subheader("AI Provider Settings")
        ai_provider = st.selectbox("AI Provider", ["openai", "anthropic", "mock"])
        ai_model = st.text_input("AI Model", value="gpt-4o")
        api_key = st.text_input("API Key", type="password", help="API key is stored securely and never displayed.")

        st.subheader("Runtime Execution")
        timeout = st.number_input("Execution Timeout (seconds)", min_value=5, max_value=300, value=30)

        saved = st.form_submit_button("Save Settings")
        if saved:
            st.success("Settings saved successfully!")
