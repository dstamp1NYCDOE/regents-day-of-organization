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


def main(students_in_section_df):
    flowables = []

    exam_title = students_in_section_df.iloc[0, :]["Exam Title"]
    exam_code = students_in_section_df.iloc[0, :]["Course"]
    section = students_in_section_df.iloc[0, :]["Section"]
    Room = students_in_section_df.iloc[0, :]["Room_y"]

    paragraph = Paragraph(
        f"{exam_title} - {exam_code}/{section} - Room {Room}",
        styles["Title"],
    )
    flowables.append(paragraph)

    cols_to_add = [
        "Student Sign In",
        "Student Sign Out",
        "A=Abs\nP=Pres",
    ]
    for col in cols_to_add:
        students_in_section_df[col] = ""

    cols = [
        "StudentID",
        "LastName",
        "FirstName",
        "A=Abs\nP=Pres",
        "Student Sign In",
        "Student Sign Out",
    ]
    students_in_section_df = students_in_section_df[cols]

    sections_table = return_df_as_table(students_in_section_df, num_of_blank_rows=4)
    flowables.append(sections_table)

    flowables.append(Spacer(0 * inch, 1 * inch))

    flowables.append(PageBreak())

    return flowables


def return_df_as_table(
    df, cols=None, colWidths=None, rowHeights=None, num_of_blank_rows=None
):
    if cols:
        table_data = df[cols].values.tolist()
    else:
        cols = df.columns
        table_data = df.values.tolist()
    if num_of_blank_rows:
        for i in range(num_of_blank_rows):
            table_data.append(["" for i in cols])
    table_data.insert(0, cols)
    t = Table(table_data, colWidths=colWidths, repeatRows=1, rowHeights=rowHeights)
    PADDING = 1
    t.setStyle(
        TableStyle(
            [
                ("ALIGN", (0, 0), (100, 100), "CENTER"),
                ("VALIGN", (0, 0), (100, 100), "MIDDLE"),
                ("FONTSIZE", (0, 0), (-1, -1), 9),
                ("LEFTPADDING", (0, 0), (-1, -1), 10 * PADDING),
                ("RIGHTPADDING", (0, 0), (-1, -1), 10 * PADDING),
                ("BOTTOMPADDING", (0, 0), (-1, -1), PADDING),
                ("TOPPADDING", (0, 0), (-1, -1), PADDING),
                ("ROWBACKGROUNDS", (0, 0), (-1, -1), (0xD0D0FF, None)),
                ("GRID", (0, 0), (-1, -1), 0.25, colors.black),
            ]
        )
    )
    return t
