import pandas as pd

import exam_proctor_labels_and_grid
import bag_labels_and_rosters
import student_exam_labels
import return_enl_rosters
import return_bathroom_passes

def main(data):
    exam_proctor_labels_and_grid.main(data)
    bag_labels_and_rosters.main(data)
    student_exam_labels.main(data)
    return_enl_rosters.main(data)
    return_bathroom_passes.main(data)
    return True


if __name__ == "__main__":
    data = {"Administration": "June2024"}
    main(data)
