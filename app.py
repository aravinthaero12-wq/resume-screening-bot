import re

# -----------------------------
# EXTRACT KEYWORDS FROM JD
# -----------------------------
def extract_jd_keywords(jd_text):
    jd = jd_text.lower()

    important_skills = [
        "autosar", "embedded c", "c++", "python",
        "canoe", "capl", "jenkins",
        "iso 26262", "asil",
        "ecu", "can", "lin", "uds"
    ]

    keywords = [skill for skill in important_skills if skill in jd]

    return keywords


# -----------------------------
# SPLIT RESUME INTO PROJECTS
# -----------------------------
def extract_projects(resume_text):
    text = resume_text.lower()

    # Simple split based on "project" keyword
    projects = re.split(r'project[s]?:', text)

    return projects if len(projects) > 1 else [text]


# -----------------------------
# SKILL USAGE PER PROJECT
# -----------------------------
def skill_usage_analysis(keywords, projects):

    skill_project_count = {skill: 0 for skill in keywords}

    for project in projects:
        for skill in keywords:
            if skill in project:
                skill_project_count[skill] += 1

    return skill_project_count


# -----------------------------
# FINAL SCORING BASED ON USAGE
# -----------------------------
def advanced_screening(jd_text, resume_text):

    keywords = extract_jd_keywords(jd_text)
    projects = extract_projects(resume_text)

    usage = skill_usage_analysis(keywords, projects)

    # Score calculation
    total_score = 0
    max_score = len(keywords) * 10 if keywords else 1

    skill_scores = {}

    for skill, count in usage.items():
        if count >= 3:
            score = 10
        elif count == 2:
            score = 7
        elif count == 1:
            score = 4
        else:
            score = 0

        skill_scores[skill] = score
        total_score += score

    final_score = round((total_score / max_score) * 10, 2)

    # Decision
    if final_score >= 7:
        decision = "Shortlist"
    elif final_score >= 5:
        decision = "Consider"
    else:
        decision = "Reject"

    return {
        "Keywords": ", ".join(keywords),
        "Projects Found": len(projects),
        "Skill Usage": usage,
        "Skill Scores": skill_scores,
        "Final Score": final_score,
        "Decision": decision
    }
