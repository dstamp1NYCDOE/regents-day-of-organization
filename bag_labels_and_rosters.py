import pandas as pd
import glob
import utils

import return_bag_label

from reportlab.platypus import SimpleDocTemplate
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib.units import inch

import labels
from reportlab.graphics import shapes


def main(data):
    administration = data["Administration"]

    exam_book_filename = glob.glob(f"data/{administration}/*ExamBook.csv")[0]
    exam_book_df = pd.read_csv(exam_book_filename)
    exam_book_df["Day"] = exam_book_df["Day"].apply(
        utils.return_regents_day_from_date_str
    )
    exam_book_df["Time Alotted"] = exam_book_df["Type"].apply(return_time_alotted)

    cr_1_08_filename = glob.glob(f"data/{administration}/1_08.csv")[0]
    cr_1_08_df = pd.read_csv(cr_1_08_filename)
    registered_students_df = cr_1_08_df[cr_1_08_df["Status"]]

    students_per_section_df = pd.pivot_table(
        registered_students_df,
        index=["Course", "Section"],
        values="StudentID",
        aggfunc="count",
    ).reset_index()
    students_per_section_df.columns = ["Course Code", "Section", "#_of_students"]

    exam_book_df = exam_book_df.merge(
        students_per_section_df, on=["Course Code", "Section"], how="left"
    ).fillna(0)
    exam_book_df["#_of_students"] = exam_book_df["#_of_students"].apply(
        lambda x: int(x)
    )

    for (day, time, exam_title), exam_rooms_df in exam_book_df.groupby(
        ["Day", "Time", "Exam Title"]
    ):
        filename = f"output/{administration}/BagLabels/Day{str(day).zfill(2)}_{time}_{exam_title}.pdf"
        exam_flowables = []
        for (room), sections_in_room_df in exam_rooms_df.groupby("Room"):
            room_flowables = return_bag_label.main(sections_in_room_df)
            exam_flowables.extend(room_flowables)

        my_doc = SimpleDocTemplate(
            filename,
            pagesize=landscape(letter),
            topMargin=0.50 * inch,
            leftMargin=1 * inch,
            rightMargin=1 * inch,
            bottomMargin=0.5 * inch,
        )
        my_doc.build(exam_flowables)

    ## prepare exam rosters

    PADDING = 1
    specs = labels.Specification(
        215.9,
        279.4,
        3,
        6,
        69,
        45,
        corner_radius=2,
        left_margin=5,
        # right_margin=5,
        top_margin=5,
        # bottom_margin=13,
        left_padding=PADDING,
        right_padding=PADDING,
        top_padding=PADDING,
        bottom_padding=PADDING,
        row_gap=0,
        column_gap=0,
    )

    registered_students_df = registered_students_df.merge(
        exam_book_df, left_on=["Course", "Section"], right_on=["Course Code", "Section"]
    )

    for (day, time, exam_title), students_df in registered_students_df.groupby(
        ["Day", "Time", "Exam Title"]
    ):
        filename = f"output/{administration}/Rosters/Day{str(day).zfill(2)}_{time}_{exam_title}.pdf"
        roster_lst = []
        for room, students_in_room_df in students_df.groupby("Room_y"):
            # filename = f"output/{administration}/Rosters/Day{str(day).zfill(2)}_{time}_{exam_title}_{room}.pdf"
            student_labels = students_in_room_df.to_dict("records")

            remainder = len(student_labels) % 18
            for i in range(18 - remainder):
                student_labels.append({})

            roster_lst.extend(student_labels)

        sheet = labels.Sheet(specs, draw_student_roster_label, border=True)
        sheet.add_labels(roster_lst)

        sheet.save(filename)


PHOTOS_DIRECTORY = "/Users/derekstampone/Library/Mobile Documents/com~apple~CloudDocs/Developer/HSFI-v2/s02M600_StudentPhotos_ALL STUDENTS"


def draw_student_roster_label(label, width, height, obj):
    LastName = obj.get("LastName", "")
    FirstName = obj.get("FirstName", "")
    StudentID = obj.get("StudentID", "")
    exam_title = obj.get("Exam Title", "")
    Type = obj.get("Type", "")
    Room = obj.get("Room_y", "")
    Time_Alotted = obj.get("Time Alotted", "")

    photo_str = f"{PHOTOS_DIRECTORY}/{StudentID}.jpg"
    # photo_str = 'banana.jpg'

    if StudentID != "":
        label.add(
            shapes.String(
                0,
                112,
                f"{FirstName}",
                fontName="Helvetica",
                fontSize=12,
            )
        )
        label.add(
            shapes.String(
                0,
                102,
                f"{LastName}",
                fontName="Helvetica",
                fontSize=12,
            )
        )

        label.add(
            shapes.String(
                0,
                90,
                f"{StudentID}",
                fontName="Helvetica",
                fontSize=12,
            )
        )

        label.add(
            shapes.String(
                0,
                75,
                f"{exam_title}",
                fontName="Helvetica",
                fontSize=11,
            )
        )

        label.add(
            shapes.String(
                0,
                60,
                f"Room {Room}",
                fontName="Helvetica",
                fontSize=11,
            )
        )

        label.add(
            shapes.String(
                0,
                45,
                f"{Type}",
                fontName="Helvetica",
                fontSize=11,
            )
        )

        label.add(
            shapes.String(
                0,
                30,
                f"{Time_Alotted}",
                fontName="Helvetica",
                fontSize=11,
            )
        )

        label.add(shapes.Image(x=95, y=0, width=90, height=90, path=photo_str))


def return_time_alotted(Type):
    if "1.5x" in Type:
        return "4.5 hours"
    if "enl" in Type:
        return "4.5 hours"
    if "2x" in Type:
        return "6 hours"
    if "SCRIBE" in Type:
        return "6 hours"
    return "3 hours"


if __name__ == "__main__":
    data = {"Administration": "January2024"}
    main(data)
