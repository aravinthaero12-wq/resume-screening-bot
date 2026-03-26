import streamlit as st
import pdfplumber
import docx
import pandas as pd
import re

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
# AUTOMOTIVE SCORING ENGINE
# -----------------------------
def automotive_score(jd_text, resume_text):

    text = resume_text.lower()
    jd = jd_text.lower()

    # -------------------------
    # SKILL MATCH
    # -------------------------
    jd_keywords = set(jd.split())
    resume_keywords = set(text.split())
    matched = jd_keywords.intersection(resume_keywords)

    skill_score = (len(matched) / len(jd_keywords)) * 10 if jd_keywords else 0

    # -------------------------
    # AUTOSAR DEPTH
    # -------------------------
    autosar_score = 0
    if "autosar" in text:
        autosar_score = 5
    if any(x in text for x in ["swc", "bsw", "rte"]):
        autosar_score = 9

    # -------------------------
    # FUNCTIONAL SAFETY
    # -------------------------
    safety_score = 0
    if "iso 26262" in text:
        safety_score = 8
    if "asil" in text:
        safety_score = 10

    # -------------------------
    # DOMAIN (ECU vs NON-ECU)
    # -------------------------
    if any(x in text for x in ["ecu", "can", "lin", "uds"]):
        domain_score = 9
    elif "automotive" in text:
        domain_score = 7
    else:
        domain_score = 4

    # -------------------------
    # ROLE TYPE
    # -------------------------
    if any(x in text for x in ["canoe", "capl", "testing"]):
        role_type = "Testing"
        role_score = 8
    elif any(x in text for x in ["embedded c", "c++"]):
        role_type = "Development"
        role_score = 8
    else:
        role_type = "Unknown"
        role_score = 5

    # -------------------------
    # EXPERIENCE
    # -------------------------
    exp_match = re.search(r'(\d+)\+?\s*years', text)
    exp = int(exp_match.group(1)) if exp_match else 0

    if exp >= 8:
        exp_score = 10
    elif exp >= 5:
        exp_score = 8
    elif exp >= 3:
        exp_score = 6
    else:
        exp_score = 3

    # -------------------------
    # INFOTAINMENT PENALTY
    # -------------------------
    penalty = 0
    if "android" in text and "ecu" not in text:
        penalty = -2

    # -------------------------
    # FINAL SCORE
    # -------------------------
    final_score = round(
        skill_score * 0.25 +
        autosar_score * 0.15 +
        safety_score * 0.15 +
        domain_score * 0.15 +
        role_score * 0.1 +
        exp_score * 0.2 +
        penalty,
        2
    )

    # -------------------------
    # DECISION
    # -------------------------
    if final_score >= 7:
        decision = "Shortlist"
    elif final_score >= 5:
        decision = "Consider"
    else:
        decision = "Reject"

    return {
        "Skill Score": round(skill_score, 2),
        "AUTOSAR Score": autosar_score,
        "Safety Score": safety_score,
        "Domain Score": domain_score,
        "Role Type": role_type,
        "Experience Score": exp_score,
        "Final Score": final_score,
        "Decision": decision
    }

# -----------------------------
# UI
# -----------------------------
st.title("🚀 Automotive Resume Screening BOT (FREE)")

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

        results = []

        for file in resume_files:

            # Read Resume
            if file.name.endswith(".pdf"):
                resume_text = read_pdf(file)
            elif file.name.endswith(".docx"):
                resume_text = read_docx(file)
            else:
                resume_text = file.read().decode()

            evaluation = automotive_score(jd_text, resume_text)

            results.append({
                "Candidate": file.name,
                **evaluation
            })

        df = pd.DataFrame(results)

        # Sort by score
        df = df.sort_values(by="Final Score", ascending=False)

        st.subheader("📊 Screening Results (Ranked)")
        st.dataframe(df)

    else:
        st.warning("Please upload JD and resumes")
