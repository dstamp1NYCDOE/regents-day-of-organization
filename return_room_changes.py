import pandas as pd  #
import glob

import utils


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

PHOTOS_DIRECTORY = "/Users/derekstampone/Library/Mobile Documents/com~apple~CloudDocs/Developer/HSFI-v2/s02M600_StudentPhotos_ALL STUDENTS"


def main(data):
    administration = data["Administration"]

    exam_book_filename = glob.glob(f"data/{administration}/*ExamBook.csv")[0]
    exam_book_df = pd.read_csv(exam_book_filename)
    exam_book_df["Day"] = exam_book_df["Day"].apply(
        utils.return_regents_day_from_date_str
    )

    cr_1_08_filename = glob.glob(f"data/{administration}/1_08.csv")[0]
    cr_1_08_df = pd.read_csv(cr_1_08_filename)
    cr_1_08_df["ExamAdministration"] = administration
    registered_students_df = cr_1_08_df[cr_1_08_df["Status"]]

    registered_students_df = registered_students_df.merge(
        exam_book_df, left_on=["Course", "Section"], right_on=["Course Code", "Section"]
    )

    room_changes_df = registered_students_df[
        registered_students_df["Room_x"] != registered_students_df["Room_y"]
    ]

    room_changes_df = room_changes_df.rename(
        columns={"Room_x": "Original\nRoom", "Room_y": "Updated\nRoom"}
    )

    cols = [
        "StudentID",
        "LastName",
        "FirstName",
        "Original\nRoom",
        "Exam Title",
        "Day",
        "Time",
        "Type",
        "Updated\nRoom",
    ]
    room_changes_df = room_changes_df[cols]
    room_changes_df = room_changes_df.sort_values(
        by=["Day", "Time", "Exam Title", "Original\nRoom"]
    )

    ## output_master_list_by_day_time_exam
    filename = f"output/{administration}/RoomChanges/{administration}_Room_Changes.pdf"

    flowables = [
        Paragraph(
            f"{administration} Room Changes",
            styles["Title"],
        ),
        utils.return_df_as_table(room_changes_df),
    ]
    my_doc = SimpleDocTemplate(
        filename,
        pagesize=letter,
        topMargin=0.50 * inch,
        leftMargin=1 * inch,
        rightMargin=1 * inch,
        bottomMargin=0.5 * inch,
    )
    my_doc.build(flowables)

    for (day, time, exam_title), changes_df in room_changes_df.groupby(
        ["Day", "Time", "Exam Title"]
    ):
        filename = f"output/{administration}/RoomChanges/{administration}_Day{str(day).zfill(2)}_{time}_{exam_title}_Room_Changes.pdf"
        flowables = [
            Paragraph(
                f"{administration} Day{day}-{time} - {exam_title} Room Changes",
                styles["Title"],
            ),
            utils.return_df_as_table(changes_df),
            PageBreak(),
        ]
        for original_room, changes_dff in changes_df.groupby("Original\nRoom"):
            flowables.extend(
                [
                    Paragraph(
                        f"Day{day}-{time} - {exam_title} Room {original_room} - Room changes",
                        styles["Title"],
                    ),
                    Paragraph(
                        f"The following students were scheduled to test in room {original_room} and have been rescheduled to a new room. Please give the students their room change slip and confirm their answer document is not in your testing materials.",
                        styles["Normal"],
                    ),
                    Spacer(0 * inch, 0.5 * inch),
                    utils.return_df_as_table(
                        changes_dff.drop(
                            columns=[
                                "Exam Title",
                                "Day",
                                "Time",
                                "Type",
                            ]
                        )
                    ),
                    PageBreak(),
                ]
            )
            for (
                LastName,
                FirstName,
                StudentID,
                new_room,
                original_room,
            ), student_room_change_df in changes_dff.groupby(
                [
                    "LastName",
                    "FirstName",
                    "StudentID",
                    "Updated\nRoom",
                    "Original\nRoom",
                ]
            ):
                flowables.extend(
                    [
                        Paragraph(
                            f"{FirstName} {LastName} ({StudentID})",
                            styles["Heading1"],
                        ),
                        Paragraph(
                            f"Day{day}-{time} - {exam_title} Room Change",
                            styles["Heading2"],
                        ),
                        Paragraph(
                            f"You have been rescheduled to take {exam_title} from room {original_room} to room {new_room}. Please report to {new_room} with this new invitation, your personal belongings, and your original test invitation. Show this letter to your proctor.",
                            styles["Normal"],
                        ),
                        Spacer(0 * inch, 0.5 * inch),
                        Image(
                            f"{PHOTOS_DIRECTORY}/{StudentID}.jpg",
                            width=4 * inch,
                            height=4 * inch,
                            kind="proportional",
                        ),
                        Spacer(0 * inch, 0.5 * inch),
                        utils.return_df_as_table(
                            student_room_change_df.drop(
                                columns=[
                                    "Exam Title",
                                    "Day",
                                    "Time",
                                    "Type",
                                ]
                            )
                        ),
                        PageBreak(),
                    ]
                )

        for updated_room, changes_dff in changes_df.groupby("Updated\nRoom"):
            flowables.extend(
                [
                    Paragraph(
                        f"Day{day}-{time} - {exam_title} Room {updated_room} - Room changes",
                        styles["Title"],
                    ),
                    Paragraph(
                        f"The following students were scheduled to test in other rooms and are now testing in room {updated_room}. Please confirm you have the student specific testing materials and if you are missing any call the testing office (x2021 x2022)",
                        styles["Normal"],
                    ),
                    utils.return_df_as_table(
                        changes_dff.drop(
                            columns=[
                                "Exam Title",
                                "Day",
                                "Time",
                                # "Type",
                            ]
                        )
                    ),
                    PageBreak(),
                ]
            )
        my_doc = SimpleDocTemplate(
            filename,
            pagesize=letter,
            topMargin=0.50 * inch,
            leftMargin=1 * inch,
            rightMargin=1 * inch,
            bottomMargin=0.5 * inch,
        )
        my_doc.build(flowables)


if __name__ == "__main__":
    data = {"Administration": "January2024"}
    main(data)
