import pandas as pd
import glob
import utils

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

import labels
from reportlab.graphics import shapes

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
    print(exam_book_df)

    cr_1_08_filename = glob.glob(f"data/{administration}/1_08.csv")[0]
    cr_1_08_df = pd.read_csv(cr_1_08_filename)

    registered_students_df = cr_1_08_df[cr_1_08_df["Status"]]
    registered_students_df = registered_students_df[['StudentID','LastName','FirstName',"Course","Section"]]

    testing_accommodations_filename = glob.glob(f"data/{administration}/*Testing Accommodations*.csv")[0]

    testing_accommodations_df = pd.read_csv(testing_accommodations_filename)
    enl_students_df = testing_accommodations_df[testing_accommodations_df['ENL?']==True]
    enl_students_df = enl_students_df[['StudentID','HomeLang']].drop_duplicates()
    enl_student_ids = enl_students_df['StudentID']

    enl_exam_registrations_df = registered_students_df[registered_students_df['StudentID'].isin(enl_student_ids)]
    enl_exam_registrations_df = enl_exam_registrations_df.merge(enl_students_df, on='StudentID', how='left')
  
    enl_exam_registrations_df = enl_exam_registrations_df.merge( 
        exam_book_df, 
        left_on=["Course", "Section"],
        right_on=["Course Code", "Section"], how="left"
    )

    for (day, time, exam_title), exam_registrations_df in enl_exam_registrations_df.groupby(['Day','Time','Exam Title']):
        filename = f"output/{administration}/ENLRosters/Day{str(day).zfill(2)}_{time}_{exam_title}.pdf"
        exam_flowables = []
        for room, exam_room_registrations_df in exam_registrations_df.groupby('Room'):
            summary_pvt = pd.pivot_table(
                exam_room_registrations_df, index='HomeLang', values='StudentID', aggfunc='count'
            ).reset_index()
            summary_pvt.columns = ['HomeLang','#']
            

            paragraph = Paragraph(
                f"{exam_title} - {room} - ENL Info",
                styles["Title"],
            )
            exam_flowables.append(paragraph)


            paragraph = Paragraph(
                f"Each student shall receive access to a language glossery and home language exam when applicable. These materials are in the room or provided in the testing bag. For exams other than ELA, they may write their responses in their home language. Answers should all appear in one book. Students receive a minimum of 1.5x time accommodation - Their IEP may indicate other testing accommodations.",
                styles["Normal"],
            )
            exam_flowables.append(paragraph)

            pvt_T = return_df_as_table(summary_pvt)
            roster_T_cols = ['StudentID', 'LastName', 'FirstName',  'HomeLang', 'Type']
            roster_T = return_df_as_table(exam_room_registrations_df, cols=roster_T_cols)

            chart_style = TableStyle([('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                                    ('VALIGN', (0, 0), (-1, -1), 'TOP')])

            exam_flowables.append(Table([[roster_T,pvt_T]],
                                colWidths=[6.5 * inch,2 * inch],
                                 style=chart_style))

            # exam_flowables.append(pvt_T)
            # exam_flowables.append(roster_T)

            exam_flowables.append(PageBreak())

        my_doc = SimpleDocTemplate(
            filename,
            pagesize=landscape(letter),
            topMargin=0.50 * inch,
            leftMargin=1 * inch,
            rightMargin=1 * inch,
            bottomMargin=0.5 * inch,
        )
        my_doc.build(exam_flowables)


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

if __name__ == '__main__':
    data = {"Administration": "January2024"}
    main(data)

