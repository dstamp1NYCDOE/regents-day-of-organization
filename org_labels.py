import pandas as pd
import glob
import utils

import return_bag_label

from reportlab.platypus import SimpleDocTemplate
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib.units import inch

import labels
from reportlab.graphics import shapes

PADDING = 0
specs = labels.Specification(
    215.9,
    279.4,
    3,
    10,
    66.6,
    25.2,
    corner_radius=2,
    left_margin=5,
    right_margin=5,
    top_margin=12.25,
    # bottom_margin=13,
    left_padding=PADDING,
    right_padding=PADDING,
    top_padding=PADDING,
    bottom_padding=PADDING,
    row_gap=0,
)


def main(data):
    administration = data["Administration"]

    exam_book_filename = glob.glob(f"data/{administration}/*ExamBook.csv")[0]
    exam_book_df = pd.read_csv(exam_book_filename)
    exam_book_df["Day"] = exam_book_df["Day"].apply(
        utils.return_regents_day_from_date_str
    )

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

    filename = f"output/{administration}/BagLabels/OrgLabels.pdf"
    labels_to_make = []
    for (day, time, exam_title), exam_rooms_df in exam_book_df.groupby(
        ["Day", "Time", "Exam Title"]
    ):
        section_labels = exam_rooms_df.sort_values(by=["Room"]).to_dict("records")
        labels_to_make.extend(section_labels)

        labels_to_make.append({})
        labels_to_make.append({})
        labels_to_make.append({})
    sheet = labels.Sheet(specs, draw_room_label, border=True)
    sheet.add_labels(labels_to_make)
    sheet.save(filename)


def draw_room_label(label, width, height, obj):
    exam_title = obj.get("Exam Title")
    type = obj.get("Type")
    room = obj.get("Room")
    Day = obj.get("Day")
    Time = obj.get("Time")
    Course = obj.get("Course Code")
    Section = obj.get("Section")

    if exam_title:
        label.add(
            shapes.String(4, 55, f"Day{Day}-{Time}", fontName="Helvetica", fontSize=10)
        )

        label.add(
            shapes.String(
                4,
                30,
                f"{exam_title} - {Course}/{Section}",
                fontName="Helvetica",
                fontSize=18,
            )
        )

        label.add(
            shapes.String(4, 10, f"{room} - {type}", fontName="Helvetica", fontSize=10)
        )


if __name__ == "__main__":
    data = {"Administration": "January2024"}
    main(data)
