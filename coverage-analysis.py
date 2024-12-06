#!/usr/bin/env python3

import os, time, cv2, numpy as np

from plant_coverage import coverage


dataset_base_dir = "/mnt/c/Users/charles/Desktop/MII/data/DataSet/coverage"
results_base_dir = os.path.dirname(os.path.realpath(__file__)) + "coverage-results"

for dir_name in ["240508_DW_62", "240514_DW_63", "240521_DW_84"]:

    dataset_dir = os.path.join(dataset_base_dir, dir_name)
    dest_dir = os.path.join(results_base_dir, dir_name)
    print(f"Processing dataset in {dir_name}")
    coverage.process_dir_or_image(dataset_dir, dest_dir)


