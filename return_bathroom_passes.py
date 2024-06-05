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

import utils
import glob
import pandas as pd  #

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


def main(data):
    administration = data["Administration"]
    exam_book_filename = glob.glob(f"data/{administration}/*ExamBook.csv")[0]
    exam_book_df = pd.read_csv(exam_book_filename)
    exam_book_df["Day"] = exam_book_df["Day"].apply(
        utils.return_regents_day_from_date_str
    )

    for (day, time, course), exam_rooms_df in exam_book_df.drop_duplicates(
        subset=["Course Code", "Room"]
    ).groupby(["Day", "Time", "Course Code"]):
        exam_flowables = []
        exam_title = exam_rooms_df.iloc[0, :]["Exam Title"]
        day_as_str = pd.to_datetime(day).strftime("%Y-%m-%d")
        filename = f"output/{administration}/BathroomPasses/{day_as_str}_{time}_{exam_title}.pdf"
        for index, row in exam_rooms_df.iterrows():
            Room = row["Room"]

            paragraph = Paragraph(
                f"Bathroom Pass - {exam_title} - Room {Room} - {day} - {time}",
                styles["Title"],
            )
            exam_flowables.append(paragraph)

            T = return_bathroom_grid()
            exam_flowables.append(T)
            exam_flowables.append(PageBreak())

        my_doc = SimpleDocTemplate(
            filename,
            pagesize=letter,
            topMargin=0.50 * inch,
            leftMargin=1 * inch,
            rightMargin=1 * inch,
            bottomMargin=0.5 * inch,
        )
        my_doc.build(exam_flowables)
    return True


def return_bathroom_grid(cols=None, colWidths=None, rowHeights=None):
    table_data = [
        ["Student Name", "Time Out", "Time In"],
        ["", "", ""],
        ["", "", ""],
        ["", "", ""],
        ["", "", ""],
        ["", "", ""],
        ["", "", ""],
        ["", "", ""],
        ["", "", ""],
        ["", "", ""],
        ["", "", ""],
        ["", "", ""],
        ["", "", ""],
        ["", "", ""],
        ["", "", ""],
        ["", "", ""],
        ["", "", ""],
        ["", "", ""],
        ["", "", ""],
        ["", "", ""],
        ["", "", ""],
        ["", "", ""],
        ["", "", ""],
        ["", "", ""],
        ["", "", ""],
        ["", "", ""],
        ["", "", ""],
        ["", "", ""],
    ]
    colWidths = [4 * inch, 1.5 * inch, 1.5 * inch]
    t = Table(table_data, colWidths=colWidths, repeatRows=1, rowHeights=rowHeights)
    t.setStyle(
        TableStyle(
            [
                ("ALIGN", (0, 0), (100, 100), "CENTER"),
                ("VALIGN", (0, 0), (100, 100), "MIDDLE"),
                ("FONTSIZE", (0, 0), (-1, -1), 12),
                ("LEFTPADDING", (0, 0), (-1, -1), 6),
                ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                # ("ROWBACKGROUNDS", (0, 0), (-1, -1), (0xD0D0FF, None)),
                ("GRID", (0, 0), (-1, -1), 0.25, colors.black),
            ]
        )
    )
    return t


if __name__ == "__main__":
    data = {"Administration": "June2024"}
    main(data)
