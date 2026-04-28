import os

# 1. README.md Content
readme_content = """# 🛡️ Axion Sentinel Elite: Governance Engine
### *Context-Aware Sovereign Content Verification for Enterprise Marketing*

![Azure OpenAI](https://img.shields.io/badge/Azure-OpenAI-0078D4?style=for-the-badge&logo=microsoft-azure&logoColor=white)
![Qdrant](https://img.shields.io/badge/Qdrant-Vector_DB-E22D30?style=for-the-badge)
![Streamlit](https://img.shields.io/badge/Streamlit-App-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)

---

## 📖 Overview
Axion Sentinel Elite is a sophisticated **Content Operations Audit Engine** designed to solve the "consistency under constraint" problem in enterprise marketing. It serves as the "last line of defense", ensuring every piece of content adheres to strict brand guidelines, audience-specific tones, and channel-specific formatting rules.

## 🎯 Key Features
- **3x3 Governance Matrix**: Automatically pivots logic based on 6 channels (LinkedIn, Press Release, etc.) and 3 audiences (Executive, Practitioner, Technical).
- **RAG-Backed Compliance**: Retrieves sovereign brand rules from a vector store to flag prohibited jargon like "leverage" or "synergy".
- **Hard-Enforcement Truncation**: Physically prevents content from exceeding channel word limits (e.g., 10 words for headlines, 150 for LinkedIn).
- **Enterprise Business Impact**: Calculates "Governance Savings" and "Efficiency Gains" in real-time to demonstrate ROI.
- **Traceable Change Log**: Provides a line-by-line rationale for every modification made to the original draft.

## ⚙️ Setup
1. Install dependencies: `pip install -r requirements.txt`
2. Create a `.env` file based on `.env.example`.
3. Run the app: `streamlit run app.py`

---
*Developed for the Hackathon Track: AI/AI Agents in Marketing Operations.*
"""

# 2. requirements.txt Content
requirements_content = """streamlit
pandas
plotly
openai
azure-openai
qdrant-client
python-dotenv
fpdf2
pdfplumber
python-docx
diff-match-patch
"""

# 3. .gitignore Content
gitignore_content = """# Secrets
.env

# Python
__pycache__/
*.py[cod]
*$py.class
venv/
env/

# OS
.DS_Store
"""

# 4. .env.example Content
env_example_content = """# Azure OpenAI Config
AZURE_OPENAI_API_KEY=your_key_here
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_API_VERSION=2024-12-01-preview
AZURE_OPENAI_DEPLOYMENT=your_gpt_model_name
AZURE_OPENAI_EMBEDDINGS_DEPLOYMENT=your_embedding_model_name

# Qdrant Config
QDRANT_HOST=localhost
QDRANT_PORT=6333
"""

# Write files
with open("README_DEMO.md", "w") as f: f.write(readme_content)
with open("requirements_DEMO.txt", "w") as f: f.write(requirements_content)
with open(".gitignore_DEMO", "w") as f: f.write(gitignore_content)
with open(".env.example_DEMO", "w") as f: f.write(env_example_content)
