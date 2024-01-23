from reportlab.graphics import shapes
from reportlab.lib import colors
from reportlab.lib.enums import TA_JUSTIFY, TA_LEFT, TA_CENTER, TA_RIGHT
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm, inch
from reportlab.platypus import (
    Paragraph,
    PageBreak,
    Spacer,
    Image,
    Table,
    TableStyle,
    ListFlowable,
)
from reportlab.platypus import SimpleDocTemplate


styles = getSampleStyleSheet()

styles.add(
    ParagraphStyle(
        name="Normal_RIGHT",
        parent=styles["Normal"],
        alignment=TA_RIGHT,
    )
)

styles.add(
    ParagraphStyle(
        name="Body_Justify",
        parent=styles["BodyText"],
        alignment=TA_JUSTIFY,
    )
)

styles.add(
    ParagraphStyle(
        name="Title_LARGE",
        parent=styles["Title"],
        alignment=TA_CENTER,
        fontSize=72,
        leading=int(72 * 1.2),
    )
)


def main(sections_df):
    flowables = []

    time = sections_df.iloc[0, :]["Time"]
    start_time = return_start_time(time)
    uniform_admissions_deadline = return_uniform_admissions_deadline(time)

    exam_title = sections_df.iloc[0, :]["Exam Title"]
    Room = sections_df.iloc[0, :]["Room"]

    exam_dropoff_location = return_exam_dropoff_location(exam_title)

    paragraph = Paragraph(
        f"{exam_title} - {Room}",
        styles["Title_LARGE"],
    )
    flowables.append(paragraph)

    cols = [
        "Section",
        "Type",
        "Time Alotted",
        "#_of_students",
    ]
    sections_df = sections_df[cols]
    total = sections_df["#_of_students"].sum()
    sections_df.loc[len(sections_df)] = {
        "Section": "Total",
        "Type": "",
        "Time Alotted": "",
        "#_of_students": total,
    }

    sections_table = return_df_as_table(sections_df)
    flowables.append(sections_table)

    flowables.append(Spacer(0 * inch, 1 * inch))

    paragraph = Paragraph(
        f"Exam Start Time: {start_time}",
        styles["Heading2"],
    )
    flowables.append(paragraph)

    paragraph = Paragraph(
        f"Uniform Admissions Deadline: {uniform_admissions_deadline}",
        styles["Heading2"],
    )
    flowables.append(paragraph)

    paragraph = Paragraph(
        f"Exam Dropoff Location: {exam_dropoff_location}",
        styles["Heading2"],
    )
    flowables.append(paragraph)

    flowables.append(PageBreak())

    return flowables


def return_exam_dropoff_location(exam_title):
    if exam_title == "ELA":
        return "227"
    elif exam_title in ['Global','USH']:
        return '427'
    else:
        return "202"


def return_start_time(Time):
    if Time == "AM":
        return "9:15 AM"
    if Time == "PM":
        return "1:15 PM"


def return_uniform_admissions_deadline(Time):
    if Time == "AM":
        return "10:00 AM"
    if Time == "PM":
        return "2:00 PM"


def return_df_as_table(df, cols=None, colWidths=None, rowHeights=None):
    if cols:
        table_data = df[cols].values.tolist()
    else:
        cols = df.columns
        table_data = df.values.tolist()
    table_data.insert(0, cols)
    t = Table(table_data, colWidths=colWidths, repeatRows=1, rowHeights=rowHeights)
    t.setStyle(
        TableStyle(
            [
                ("ALIGN", (0, 0), (100, 100), "CENTER"),
                ("VALIGN", (0, 0), (100, 100), "MIDDLE"),
                ("FONTSIZE", (0, 0), (-1, -1), 12),
                ("LEFTPADDING", (0, 0), (-1, -1), 5),
                ("RIGHTPADDING", (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("ROWBACKGROUNDS", (0, 0), (-1, -1), (0xD0D0FF, None)),
                ("INNERGRID", (0, 0), (-1, -1), 0.25, colors.black),
            ]
        )
    )
    return t
