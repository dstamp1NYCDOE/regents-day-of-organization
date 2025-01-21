import pandas as pd

import exam_proctor_labels_and_grid
import bag_labels_and_rosters
import student_exam_labels
import return_enl_rosters
import return_bathroom_passes
import folder_labels


def main(data):
    exam_proctor_labels_and_grid.main(data)
    bag_labels_and_rosters.main(data)
    student_exam_labels.main(data)
    return_enl_rosters.main(data)
    return_bathroom_passes.main(data)
    folder_labels.main(data)
    return True


if __name__ == "__main__":
    data = {"Administration": "January2025"}
    main(data)
