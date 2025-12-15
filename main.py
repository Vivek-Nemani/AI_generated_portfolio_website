import streamlit as st
import os
import re
import zipfile
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, HumanMessage
from PyPDF2 import PdfReader

load_dotenv()
gemini_key = os.getenv("gemini")
if not gemini_key:
    st.error("Missing API key. Add gemini to your .env file.")
    st.stop()
os.environ["GOOGLE_API_KEY"] = gemini_key

st.set_page_config(
    page_title="AI Automated Portfolio Builder",
    page_icon="🌐",
    layout="wide"
)

# UI Styling
st.markdown("""
<style>
.main {
    background: linear-gradient(135deg, #1e293b, #0f172a);
    padding: 30px;
}
.title {
    text-align: center;
    font-size: 40px;
    font-weight: 800;
    color: white;
}
.subtitle {
    text-align: center;
    color: #cbd5f5;
    margin-bottom: 30px;
}
.stTextArea textarea {
    background-color: white !important;
    font-size: 16px;
    border-radius: 8px;
}
.stButton>button {
    background-color: #38bdf8 !important;
    color: black !important;
    font-size: 18px;
    padding: 10px 24px;
    border-radius: 10px;
    font-weight: bold;
}
.stDownloadButton>button {
    background-color: #22c55e !important;
    color: black !important;
    font-size: 18px;
    padding: 10px 24px;
    border-radius: 10px;
    font-weight: bold;
}
</style>
""", unsafe_allow_html=True)

st.markdown("<div class='title'>AI Automated Portfolio Builder</div>", unsafe_allow_html=True)
st.markdown("<div class='subtitle'>Upload a resume — AI will build a portfolio site</div>", unsafe_allow_html=True)

resume_file = st.file_uploader("📄 Upload your resume (PDF)", type=["pdf"])

def extract_text_from_pdf(uploaded_file) -> str:
    """Read text from uploaded PDF file."""
    if not uploaded_file:
        return ""
    reader = PdfReader(uploaded_file)
    pages = [page.extract_text() or "" for page in reader.pages]
    return "\n".join(pages).strip()

if st.button("Generate Portfolio Website"):
    if not resume_file:
        st.warning("Please upload a PDF resume.")
    else:
        resume_text = extract_text_from_pdf(resume_file)
        if not resume_text:
            st.error("Could not read text from the PDF. Please try another file.")
            st.stop()

        with st.spinner("Creating your portfolio using AI..."):
            system_message = """
You are an expert frontend web developer and portfolio designer.

Create a PROFESSIONAL, MODERN, VISUALLY RICH personal portfolio website
based on the user's resume content. Highlight skills, experience,
projects, education, and contact info.

MANDATORY RULES:
- Do NOT generate plain HTML
- Use modern professional color themes (NOT purple gradient)
- Use flat design (NO curves, NO waves, NO circles)
- Use cards with shadows
- Use buttons instead of links
- Fully responsive layout
- Clean typography using Google Fonts
- Smooth hover effects

Generate HTML, CSS, and JavaScript.

STRICT OUTPUT FORMAT:

--html--
[HTML CODE]
--html--

--css--
[CSS CODE]
--css--

--js--
[JAVASCRIPT CODE]
--js--
"""

            messages = [
                SystemMessage(content=system_message),
                HumanMessage(content=f"Resume content:\n{resume_text}")
            ]

            model = ChatGoogleGenerativeAI(
                model="gemini-2.5-flash-lite",
                temperature=0.6
            )

            response = model.invoke(messages)
            content = response.content

            try:
                def parse_output(text: str):
                    """Extract html/css/js even if markers are missing; fallback to fenced blocks."""
                    # Preferred: explicit markers
                    if all(tag in text for tag in ("--html--", "--css--", "--js--")):
                        html_part = text.split("--html--")[1].split("--html--")[0].strip()
                        css_part = text.split("--css--")[1].split("--css--")[0].strip()
                        js_part = text.split("--js--")[1].split("--js--")[0].strip()
                        return html_part, css_part, js_part

                    # Fallback: fenced code blocks ```html ```css ```javascript
                    fence_re = re.compile(r"```(html|css|javascript|js)\\s+([\\s\\S]*?)```", re.IGNORECASE)
                    blocks = {m.group(1).lower(): m.group(2).strip() for m in fence_re.finditer(text)}
                    if blocks:
                        html_part = blocks.get("html", "")
                        css_part = blocks.get("css", "")
                        js_part = blocks.get("javascript", blocks.get("js", ""))
                        if html_part or css_part or js_part:
                            return html_part, css_part, js_part

                    # Last resort: treat entire output as HTML
                    return text.strip(), "", ""

                html_code, css_code, js_code = parse_output(content or "")

                # Ensure the HTML references the generated CSS/JS files
                def ensure_asset_links(html: str, has_css: bool, has_js: bool) -> str:
                    head_close = "</head>"
                    additions = []
                    if has_css and "style.css" not in html:
                        additions.append('<link rel="stylesheet" href="style.css">')
                    if has_js and "script.js" not in html:
                        additions.append('<script defer src="script.js"></script>')
                    if not additions:
                        return html
                    inject_block = "\n".join(additions) + "\n"
                    if head_close in html:
                        return html.replace(head_close, inject_block + head_close, 1)
                    # If no head tag, prepend
                    return inject_block + html

                html_code = ensure_asset_links(
                    html_code,
                    has_css=bool(css_code.strip()),
                    has_js=bool(js_code.strip()),
                )

                with open("index.html", "w", encoding="utf-8") as f:
                    f.write(html_code)

                with open("style.css", "w", encoding="utf-8") as f:
                    f.write(css_code)

                with open("script.js", "w", encoding="utf-8") as f:
                    f.write(js_code)

                with zipfile.ZipFile("website.zip", "w") as zipf:
                    zipf.write("index.html")
                    zipf.write("style.css")
                    zipf.write("script.js")

                with open("website.zip", "rb") as zip_data:
                    st.success("✅ Portfolio website generated successfully!")
                    st.download_button(
                        "⬇️ Download Portfolio ZIP",
                        data=zip_data.read(),
                        file_name="portfolio_website.zip"
                    )

            except Exception as err:
                st.error(f"AI output format error. Please generate again. Details: {err}")