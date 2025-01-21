import pandas as pd  #
import glob

import utils
import labels
import return_SAR_flowables

from reportlab.graphics import shapes

from reportlab.platypus import SimpleDocTemplate
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib.units import inch

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
    cr_1_08_df["ExamAdministration"] = administration
    registered_students_df = cr_1_08_df[cr_1_08_df["Status"]]

    registered_students_df = registered_students_df.merge(
        exam_book_df, left_on=["Course", "Section"], right_on=["Course Code", "Section"]
    )

    exam_sections_df = registered_students_df.drop_duplicates(subset=['Course','Section'])

    
    for (day, time, exam_title), exam_sections_by_exam_df in exam_sections_df.groupby(
        ["Day", "Time", "Exam Title"]
    ):
        
        day_as_str = pd.to_datetime(day).strftime("%Y-%m-%d")
        filename = (
            f"output/{administration}/FolderLabels/{day_as_str}_{time}_{exam_title}_FolderLabels.pdf"
        )

        labels_to_make = []
        for room, sections_in_room_df in exam_sections_by_exam_df.groupby('Room_x'):

            room_label = {
                'Day':sections_in_room_df.iloc[0]['Day'],
                'Type':sections_in_room_df.iloc[0]['Type'],
                'Time':sections_in_room_df.iloc[0]['Time'],
                'Course':sections_in_room_df.iloc[0]['Course'],
                'Sections':sections_in_room_df['Section'].to_list(),
                'Room':sections_in_room_df.iloc[0]['Room_y'],
                'ExamAdministration':administration,
            }
            labels_to_make.append(room_label)
            labels_to_make.append(room_label)


        sheet = labels.Sheet(specs, draw_label, border=True)
        sheet.add_labels(labels_to_make)
        sheet.save(filename)

    return True


def draw_label(label, width, height, obj):
    exam_title = return_exam_name(obj["Course"])
    type = obj.get("Type")
    room = obj.get("Room")
    Day = obj.get("Day")
    Time = obj.get("Time")

    

    label.add(
        shapes.String(4, 52, f"{exam_title}", fontName="Helvetica", fontSize=18)
    )    
    label.add(
        shapes.String(125, 55, f"{Day}-{Time}", fontName="Helvetica", fontSize=10)
    )



    label.add(
        shapes.String(4, 4, f"{room}", fontName="Helvetica", fontSize=40)
    )
    label.add(
        shapes.String(125, 4, f"{type}", fontName="Helvetica", fontSize=7)
    )

    label.add(
            shapes.String(
                4, 38, f"Sections: {obj['Sections']}", fontName="Helvetica", fontSize=11
            )
        )



def return_exam_name(course):
    exam_code = course[0:4]
    exam_dict = {
        "SXRP": "Physics",
        "EXRC": "ELA",
        "SXRK": "LivEnv",
        "HXRC": "Global Hist",
        "HXRK": "USH",
        "MXRC": "Algebra I",
        "MXRF": "Algebra I",
        "SXRX": "Chemistry",
        "SXRU": "Earth Sci",
        "MXRK": "Geometry",
        "MXRN": "AlgII Trig",
        "FXTS": "Spanish",
    }
    return exam_dict.get(exam_code)



if __name__ == "__main__":
    data = {"Administration": "June2024"}
    main(data)
