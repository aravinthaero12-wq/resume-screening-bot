import streamlit as st
import pdfplumber
import docx
import pandas as pd
import os
from openai import OpenAI

# Load API key from Streamlit secrets
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# -----------------------------
# FILE READERS
# -----------------------------
def read_pdf(file):
    text = ""
    with pdfplumber.open(file) as pdf:
        for page in pdf.pages:
            text += page.extract_text() or ""
    return text

def read_docx(file):
    doc = docx.Document(file)
    return "\n".join([p.text for p in doc.paragraphs])

# -----------------------------
# AI FUNCTIONS
# -----------------------------
def parse_jd(jd_text):
    prompt = f"""
    Extract structured data from this JD:
    - Role
    - Experience range
    - Mandatory skills
    - Tools
    - Domain

    Return JSON only.

    JD:
    {jd_text}
    """

    response = client.chat.completions.create(
        model="gpt-5.3",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content


def parse_resume(resume_text):
    prompt = f"""
    Extract:
    - Name
    - Total experience
    - Skills
    - Tools
    - Domain
    - Key projects

    Return JSON only.

    Resume:
    {resume_text}
    """

    response = client.chat.completions.create(
        model="gpt-5.3",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content


def evaluate_candidate(jd, resume):
    prompt = f"""
    Compare JD and Resume.

    Give:
    - Skill match score (0-10)
    - Domain match score (0-10)
    - Tools match score (0-10)
    - Experience match score (0-10)
    - Final score (0-10)
    - Strengths
    - Gaps
    - Recommendation (Shortlist / Consider / Reject)

    JD:
    {jd}

    Resume:
    {resume}
    """

    response = client.chat.completions.create(
        model="gpt-5.3",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content


# -----------------------------
# UI
# -----------------------------
st.title("🚀 AI Resume Screening BOT")

st.header("📄 Upload Job Description")
jd_file = st.file_uploader("Upload JD (PDF/DOCX/TXT)")

st.header("📑 Upload Resumes")
resume_files = st.file_uploader("Upload Resumes", accept_multiple_files=True)

if st.button("Run Screening"):

    if jd_file and resume_files:

        # Read JD
        if jd_file.name.endswith(".pdf"):
            jd_text = read_pdf(jd_file)
        elif jd_file.name.endswith(".docx"):
            jd_text = read_docx(jd_file)
        else:
            jd_text = jd_file.read().decode()

        st.subheader("🔍 JD Parsed")
        jd_parsed = parse_jd(jd_text)
        st.write(jd_parsed)

        results = []

        for file in resume_files:

            # Read resume
            if file.name.endswith(".pdf"):
                resume_text = read_pdf(file)
            elif file.name.endswith(".docx"):
                resume_text = read_docx(file)
            else:
                resume_text = file.read().decode()

            parsed_resume = parse_resume(resume_text)
            evaluation = evaluate_candidate(jd_parsed, parsed_resume)

            results.append({
                "Candidate": file.name,
                "Evaluation": evaluation
            })

        df = pd.DataFrame(results)

        st.subheader("📊 Results")
        st.dataframe(df)

    else:
        st.warning("Please upload JD and resumes")