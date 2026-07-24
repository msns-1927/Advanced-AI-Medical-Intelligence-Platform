import os
from datetime import datetime

from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer
)

from reportlab.lib.styles import getSampleStyleSheet

# Reports folder
REPORT_FOLDER = "reports"

os.makedirs(REPORT_FOLDER, exist_ok=True)


def generate_pdf_report(
    filename,
    prediction,
    confidence,
    medical_report
):

    pdf_filename = (
        os.path.splitext(filename)[0]
        + "_Medical_Report.pdf"
    )

    pdf_path = os.path.join(
        REPORT_FOLDER,
        pdf_filename
    )

    doc = SimpleDocTemplate(pdf_path)

    styles = getSampleStyleSheet()

    story = []

    # Title
    story.append(
        Paragraph(
            "<b>Advanced AI Medical Intelligence Platform</b>",
            styles["Title"]
        )
    )

    story.append(Spacer(1, 20))

    # Date
    story.append(
        Paragraph(
            f"<b>Date:</b> {datetime.now()}",
            styles["BodyText"]
        )
    )

    story.append(Spacer(1, 12))

    # Filename
    story.append(
        Paragraph(
            f"<b>Image:</b> {filename}",
            styles["BodyText"]
        )
    )

    story.append(Spacer(1, 12))

    # Prediction
    story.append(
        Paragraph(
            f"<b>Prediction:</b> {prediction}",
            styles["BodyText"]
        )
    )

    story.append(Spacer(1, 12))

    # Confidence
    story.append(
        Paragraph(
            f"<b>Confidence:</b> {confidence:.2f} %",
            styles["BodyText"]
        )
    )

    story.append(Spacer(1, 20))

    # AI Report
    story.append(
        Paragraph(
            "<b>AI Medical Report</b>",
            styles["Heading2"]
        )
    )

    story.append(Spacer(1, 12))

    clean_report = (
        medical_report
        .replace("**", "")
        .replace("\n", "<br/>")
    )

    story.append(
        Paragraph(
            clean_report,
            styles["BodyText"]
        )
    )

    story.append(Spacer(1, 20))

    # Disclaimer
    story.append(
        Paragraph(
            "<b>Disclaimer:</b> "
            "This report is AI-generated for educational purposes only. "
            "It should not replace professional medical diagnosis.",
            styles["Italic"]
        )
    )

    doc.build(story)

    return pdf_path