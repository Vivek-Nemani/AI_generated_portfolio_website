# AI Automated Portfolio Builder

A Streamlit app that takes a PDF resume, sends it to Gemini (via LangChain), and returns a downloadable portfolio website (HTML/CSS/JS + ZIP). The app also injects asset links if the model forgets them.

## Prerequisites
- Python 3.12+
- Google Gemini API key (set as `gemini` in `.env`)

## Setup
```bash
cd "/Users/vivek/anaconda_projects/Innomatics/data science/Langchain/AIgenerated_portfolio_website"
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Create `.env` in the project root:
```
gemini=YOUR_API_KEY_HERE
```

## Run
```bash
source .venv/bin/activate
streamlit run main.py
```
Then open the local URL Streamlit prints (usually http://localhost:8501).

## Using the app
1. Upload your resume as PDF.
2. Click “Generate Portfolio Website.”
3. Download the ZIP (contains `index.html`, `style.css`, `script.js`).

## Preview the generated site locally
```bash
unzip website.zip -d site
cd site
python -m http.server 8000
# Visit http://localhost:8000
```

## Notes
- `.gitignore` excludes `.venv/`, `.env`, generated `site/`, and `website.zip`.
- If the model output is missing sections, the app shows the raw output and uses fallbacks to keep generating the page.

