from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet


def generate_report(
    filename,
    name,
    email,
    phone,
    skills,
    ats_score,
    suggestions,
    ai_suggestions,
    resume_text
):

    doc = SimpleDocTemplate(filename)

    styles = getSampleStyleSheet()

    story = []

    # ---------------- Title ---------------- #

    story.append(
        Paragraph(
            "<b>AI Resume Analysis Report</b>",
            styles["Title"]
        )
    )

    story.append(Paragraph("<br/>", styles["Normal"]))

    # ---------------- Candidate Information ---------------- #

    story.append(
        Paragraph("<b>Candidate Information</b>", styles["Heading2"])
    )

    story.append(
        Paragraph(f"<b>Name:</b> {name}", styles["Normal"])
    )

    story.append(
        Paragraph(f"<b>Email:</b> {email}", styles["Normal"])
    )

    story.append(
        Paragraph(f"<b>Phone:</b> {phone}", styles["Normal"])
    )

    story.append(Paragraph("<br/>", styles["Normal"]))

    # ---------------- Skills ---------------- #

    story.append(
        Paragraph("<b>Detected Skills</b>", styles["Heading2"])
    )

    if skills:
        story.append(
            Paragraph(", ".join(skills), styles["Normal"])
        )
    else:
        story.append(
            Paragraph("No skills detected.", styles["Normal"])
        )

    story.append(Paragraph("<br/>", styles["Normal"]))

    # ---------------- ATS Score ---------------- #

    story.append(
        Paragraph("<b>ATS Score</b>", styles["Heading2"])
    )

    story.append(
        Paragraph(f"{ats_score}/100", styles["Normal"])
    )

    story.append(Paragraph("<br/>", styles["Normal"]))

    # ---------------- ATS Suggestions ---------------- #

    story.append(
        Paragraph("<b>ATS Suggestions</b>", styles["Heading2"])
    )

    if suggestions:

        for item in suggestions:

            story.append(
                Paragraph("• " + item, styles["Normal"])
            )

    else:

        story.append(
            Paragraph(
                "Excellent Resume! No ATS improvements required.",
                styles["Normal"]
            )
        )

    story.append(Paragraph("<br/>", styles["Normal"]))

    # ---------------- AI Suggestions ---------------- #

    story.append(
        Paragraph("<b>AI Resume Suggestions</b>", styles["Heading2"])
    )

    if ai_suggestions:

        for item in ai_suggestions:

            story.append(
                Paragraph("• " + item, styles["Normal"])
            )

    else:

        story.append(
            Paragraph(
                "No AI suggestions available.",
                styles["Normal"]
            )
        )

    story.append(Paragraph("<br/>", styles["Normal"]))

    # ---------------- Resume Text ---------------- #

    story.append(
        Paragraph("<b>Extracted Resume Text</b>", styles["Heading2"])
    )

    story.append(
        Paragraph(
            resume_text.replace("\n", "<br/>"),
            styles["Normal"]
        )
    )

    # ---------------- Build PDF ---------------- #

    doc.build(story)