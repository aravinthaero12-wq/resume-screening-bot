def advanced_screening(jd_text, resume_text):
    try:
        jd = jd_text.lower()
        text = resume_text.lower()

        keywords = []
        skills = ["autosar", "embedded", "python", "canoe", "capl", "iso 26262", "ecu"]

        for skill in skills:
            if skill in jd:
                keywords.append(skill)

        projects = text.split("project")

        usage = {}
        total_score = 0

        for skill in keywords:
            count = sum(1 for p in projects if skill in p)
            usage[skill] = count

            if count >= 3:
                score = 10
            elif count == 2:
                score = 7
            elif count == 1:
                score = 4
            else:
                score = 0

            total_score += score

        max_score = len(keywords) * 10 if keywords else 1
        final_score = round((total_score / max_score) * 10, 2)

        if final_score >= 7:
            decision = "Shortlist"
        elif final_score >= 5:
            decision = "Consider"
        else:
            decision = "Reject"

        return {
            "Keywords": ", ".join(keywords),
            "Projects": len(projects),
            "Final Score": final_score,
            "Decision": decision
        }

    except Exception as e:
        return {
            "Error": str(e),
            "Final Score": 0,
            "Decision": "Error"
        }
