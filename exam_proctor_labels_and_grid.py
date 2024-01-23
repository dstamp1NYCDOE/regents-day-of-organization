import pandas as pd
import glob
import utils

import labels
from reportlab.graphics import shapes


PADDING = 1
specs = labels.Specification(
    215.9,
    279.4,
    3,
    10,
    66.675,
    25.2,
    corner_radius=2,
    left_margin=5,
    right_margin=5,
    top_margin=12.75,
    # bottom_margin=13,
    left_padding=PADDING,
    right_padding=PADDING,
    top_padding=PADDING,
    bottom_padding=PADDING,
    row_gap=0.05,
)


def main(data):
    administration = data["Administration"]

    proctor_assignments_filename = f"data/{administration}/ProctorAssignments.xlsx"
    proctor_assignments_df = pd.read_excel(proctor_assignments_filename)

    proctor_schedule_filename = f"data/{administration}/ProctorSchedule.xlsx"
    proctor_schedule_df = pd.read_excel(proctor_schedule_filename)

    exam_book_filename = glob.glob(f"data/{administration}/*ExamBook.csv")[0]
    exam_book_df = pd.read_csv(exam_book_filename)
    exam_book_df["Day"] = exam_book_df["Day"].apply(
        utils.return_regents_day_from_date_str
    )

    proctor_assignments_df = proctor_assignments_df.sort_values(by=["Proctor"])
    proctor_assignments_df = proctor_assignments_df.merge(
        exam_book_df[["Day", "Time", "Room", "Type"]], on=["Day", "Time", "Room"]
    ).drop_duplicates(subset=["Day", "Time", "Room","Proctor"])
    print(proctor_assignments_df)

    ## proctor labels
    for (day, time), proctors_df in proctor_assignments_df.groupby(["Day", "Time"]):
        proctors_df = proctors_df.sort_values(by=["Proctor"])
        proctors_lst = proctors_df.to_dict("records")

        sub_proctors_lst = proctor_schedule_df[
            (proctor_schedule_df["Day"] == day)
            & (proctor_schedule_df["Assignment"] == "SUB PROCTOR")
        ].to_dict("records")

        proctors_lst.extend(sub_proctors_lst)
        sheet = labels.Sheet(specs, draw_proctor_label, border=True)
        sheet.add_labels(proctors_lst)
        filename = f"output/{administration}/ProctorLabels/Day{str(day).zfill(2)}_{time}_ProctorLabels.pdf"
        sheet.save(filename)

    ## proctor_assignment_grid

    for (day, time, course), exam_rooms_df in exam_book_df.drop_duplicates(
        subset=["Course Code", "Room"]
    ).groupby(["Day", "Time", "Course Code"]):
        rooms_lst = exam_rooms_df.sort_values(by=["Room"], ascending=False).to_dict("records")
        labels_lst = []
        for room in rooms_lst:
            labels_lst.append(room)

            proctors_lst = proctor_assignments_df[
                (proctor_assignments_df["Course"] == course)
                & (proctor_assignments_df["Room"] == room["Room"])
            ].to_dict("records")
            if len(proctors_lst) == 0:
                proctors_lst.append({})
                proctors_lst.append({})

            if len(proctors_lst) == 3:
                proctors_lst.insert(2, {})
                proctors_lst.append({})

            labels_lst.extend(proctors_lst)
        sheet = labels.Sheet(specs, draw_room_label, border=True)
        sheet.add_labels(labels_lst)
        filename = f"output/{administration}/RoomGrids/Day{str(day).zfill(2)}_{time}_{course}_RoomGrids.pdf"
        sheet.save(filename)

    return True


def draw_room_label(label, width, height, obj):
    exam_title = obj.get("Exam Title")
    type = obj.get("Type")
    room = obj.get("Room")
    Day = obj.get("Day")
    Time = obj.get("Time")

    Proctor = obj.get("Proctor")

    if exam_title:
        label.add(
            shapes.String(4, 55, f"Day{Day}-{Time}", fontName="Helvetica", fontSize=10)
        )

        label.add(
            shapes.String(4, 30, f"{exam_title}", fontName="Helvetica", fontSize=18)
        )

        label.add(
            shapes.String(4, 10, f"{room} - {type}", fontName="Helvetica", fontSize=10)
        )
    if Proctor:
        label.add(
            shapes.String(4, 55, f"Day{Day}-{Time}", fontName="Helvetica", fontSize=10)
        )

        label.add(shapes.String(4, 30, f"{Proctor}", fontName="Helvetica", fontSize=18))

        label.add(
            shapes.String(4, 10, f"{room} - {type}", fontName="Helvetica", fontSize=10)
        )


def draw_proctor_label(label, width, height, obj):
    Type = obj.get("Type", "SUB PROCTOR")
    nickname = obj.get("Proctor")
    Time = obj.get("Time")
    Day = obj.get("Day")
    Room = obj.get("Room", "")

    label.add(
        shapes.String(4, 55, f"Day{Day}-{Time}", fontName="Helvetica", fontSize=10)
    )

    label.add(shapes.String(4, 30, f"{nickname}", fontName="Helvetica", fontSize=18))

    label.add(shapes.String(4, 10, f"{Type} {Room}", fontName="Helvetica", fontSize=10))


if __name__ == "__main__":
    data = {"Administration": "January2024"}
    main(data)
