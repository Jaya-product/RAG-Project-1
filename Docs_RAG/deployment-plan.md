# Deployment Plan: Dietary Guidance RAG Chatbot

This document outlines the deployment strategy for the Dietary Guidance RAG Chatbot using **Streamlit Community Cloud**, which provides free, seamless hosting for Streamlit applications directly from a GitHub repository.

## 1. Pre-Deployment Preparation

Since the application uses a local persistent ChromaDB and external API keys, a few preparations must be made to the local repository before pushing it to GitHub.

### A. Pre-build the Vector Database
Streamlit Community Cloud containers are ephemeral, meaning they reset upon waking up. Rebuilding the Vector Database every time would be slow and inefficient.
*   **Action:** Ensure the `chroma_db` directory is fully built locally by running the ingestion scripts.
*   **Action:** Ensure that `.gitignore` does **NOT** ignore the `chroma_db/` directory, as the pre-built database needs to be pushed to GitHub so the app can read from it immediately.

### B. Update `.gitignore`
Ensure sensitive and unnecessary files are not pushed to the repository.
*   Exclude `.env` (contains your GROQ API key).
*   Exclude `.venv` (virtual environment folder).
*   Exclude `__pycache__` folders.

### C. Verify `requirements.txt`
Ensure `requirements.txt` is in the root directory and contains all necessary libraries. It currently contains the required packages:
*   `streamlit`
*   `langchain`
*   `langchain-groq`
*   `chromadb`
*   `sentence-transformers`
*   `python-dotenv`

## 2. GitHub Integration

Streamlit Community Cloud deploys directly from a GitHub repository.

1.  **Create a Repository:** Create a new repository on GitHub (Public or Private).
2.  **Commit Code:** Commit the entire project structure (including `ui/`, `scripts/`, `chroma_db/`, and `requirements.txt`) to the repository.
3.  **Push:** Push the local codebase to the `main` branch of the GitHub repository.

## 3. Deploying on Streamlit Community Cloud

Once the code is on GitHub, deployment takes only a few clicks.

1.  **Sign In:** Go to [share.streamlit.io](https://share.streamlit.io/) and sign in with your GitHub account.
2.  **New App:** Click on **"New app"**.
3.  **Configure App Settings:**
    *   **Repository:** Select the repository you just created.
    *   **Branch:** `main`
    *   **Main file path:** `ui/app.py` (It is crucial to specify the `ui` folder).
4.  **Do Not Click Deploy Yet!** You must configure secrets first.

## 4. Secrets Management (Environment Variables)

Because you did not upload your `.env` file, the Streamlit server does not have your `GROQ_API_KEY`. If deployed without it, the app will crash.

1.  On the deployment configuration screen, click **"Advanced settings..."**.
2.  Locate the **"Secrets"** text box.
3.  Add your API key using the standard TOML/Key-Value format:
    ```toml
    GROQ_API_KEY="your_actual_api_key_here"
    ```
    *(Note: Streamlit Cloud automatically injects these secrets into `st.secrets` and `os.environ`, so `load_dotenv()` will safely fall back and find the keys without requiring code changes.)*
4.  Click **"Save"**.

## 5. Finalizing Deployment

1.  Click **"Deploy!"**.
2.  Streamlit will spin up a container, read your `requirements.txt`, install dependencies (including downloading the Hugging Face embedding model on first boot), and launch the app.
3.  The application will be assigned a public URL (e.g., `https://your-app-name.streamlit.app`) which can be shared with users.

## 6. Post-Deployment Maintenance
*   **Updating the Knowledge Base:** To add new dietary documents, run the ingestion script locally to update the local `chroma_db` folder, then commit and push the updated `chroma_db` folder to GitHub. Streamlit Cloud will automatically detect the push and reboot the app with the new data.
*   **Waking up the App:** If the app receives no traffic for 7 consecutive days, Streamlit Cloud may put it to sleep. You can simply visit the URL to wake it up again.
