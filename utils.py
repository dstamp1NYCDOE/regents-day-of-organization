from reportlab.platypus import Table,TableStyle
from reportlab.lib import colors


def return_df_as_table(df, cols=None, colWidths=None, rowHeights=None):
    if cols:
        table_data = df[cols].values.tolist()
    else:
        cols = df.columns
        table_data = df.values.tolist()
    table_data.insert(0, cols)
    t = Table(table_data, colWidths=colWidths, repeatRows=1, rowHeights=rowHeights)
    PADDING = 2
    t.setStyle(
        TableStyle(
            [
                ("ALIGN", (0, 0), (100, 100), "CENTER"),
                ("VALIGN", (0, 0), (100, 100), "MIDDLE"),
                ("FONTSIZE", (0, 0), (-1, -1), 9),
                ("LEFTPADDING", (0, 0), (-1, -1), 5* PADDING),
                ("RIGHTPADDING", (0, 0), (-1, -1), 5 * PADDING),
                ("BOTTOMPADDING", (0, 0), (-1, -1), PADDING),
                ("TOPPADDING", (0, 0), (-1, -1), PADDING),
                ("ROWBACKGROUNDS", (0, 0), (-1, -1), (0xD0D0FF, None)),
                ("GRID", (0, 0), (-1, -1), 0.25, colors.black),
            ]
        )
    )
    return t


def return_assignment_difficulty(exam):
    Course = exam["Course Code"]
    Time = exam["Time"]
    Type = exam["Type"]

    difficulty = 1

    if "2x" in Type:
        if Time == "AM":
            difficulty = difficulty * 2
        elif Time == "PM":
            difficulty = difficulty * 1.25
    elif "1.5x" in Type:
        if Time == "AM":
            difficulty = difficulty * 1.5
        elif Time == "PM":
            difficulty = difficulty * 1.25
    elif "enl" in Type:
        if Time == "AM":
            difficulty = difficulty * 1.5
        elif Time == "PM":
            difficulty = difficulty * 1.25
    elif "SCRIBE" in Type:
        if Time == "AM":
            difficulty = difficulty * 1.5
        elif Time == "PM":
            difficulty = difficulty * 1.25

    if "QR" in Type:
        if Course[0] in ["E"]:
            difficulty = difficulty * 3
        if Course[0] in ["H"]:
            difficulty = difficulty * 2
        else:
            difficulty = difficulty * 1.5

    return difficulty


def return_number_of_proctors_needed(room):
    assignment_difficulty = room["assignment_difficulty"]
    Type = room["Type"]
    Time = room["Type"]
    Active = room["Active"]
    if "scribe" in Type.lower():
        return Active * 2

    if Time == "PM":
        return 2
    elif "QR" in Type:
        return 3
    else:
        if "2x" in Type:
            return 3
        else:
            return 2


import re

day_regex = re.compile(r"Day0(\d)")


def return_regents_day(col_str):
    mo = day_regex.search(col_str)
    if mo:
        return int(mo.group(1))
    return col_str


def return_regents_day_from_date_str(date_str):
    if date_str == "1/23/2024":
        return 1
    if date_str == "1/24/2024":
        return 2
    if date_str == "1/25/2024":
        return 3
    if date_str == "1/26/2024":
        return 4
