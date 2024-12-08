#!/usr/bin/env python3

import sys, os, json, cv2, numpy as np
from os.path import join as join_path
from glob import glob
from plant_coverage import coverage
import matplotlib.pyplot as plt
from calendar import month_name as month_name_list


dataset_base_dir = None
results_base_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), "coverage-results")
dataset_dirname_list = [
    "coverage/240508_DW_62", 
    "coverage/240514_DW_63", 
    "coverage/240521_DW_84", 
    "biodiversity/240814_DW_F1_42"
]

def process_dir_list():

    for dir_name in dataset_dirname_list:

        source_path = join_path(dataset_base_dir, dir_name)
        dest_path = os.path.join(results_base_dir, dir_name)
        print(f"\nProcessing dataset in {dir_name}")
        coverage.process_dir_or_image(source_path, dest_path)

def get_stats():

    x = []
    y = []
    y_errr = []
    for dir_name in dataset_dirname_list:

        dest_path = os.path.join(results_base_dir, dir_name)
        json_filepath = glob(f"{dest_path}/*.json")[0]
        with open(json_filepath, 'r') as json_file:
            stats_dict = json.load(json_file)["stats"]
            date = os.path.basename(dir_name).split("_")[0]
            date = f"{date[:2]}-{month_name_list[int(date[2:4])]}-{date[4:]}"
            x.append(date)
            y.append(stats_dict["average"])
            y_errr.append(stats_dict["std_dev"])

    plt.scatter(x, y) # create the scatter plot
    x1,x2,y1,y2 = plt.axis()
    plt.axis((x1-0.3, x2+0.5, y1-0.3, y2+1)) # expand slightly the plot area to fit text
    plt.gca().set_ylim([0, 100]) # make the y axis show 0 and 100 values
    plt.errorbar(x, y, yerr=y_errr, fmt="o", capsize=5) # show the error lines
    for i, j in zip(range(len(x)), y):
        plt.text(i+0.1, j, f"{j:.2f}%") # add the value text next to each pont

    
    plt.grid(color='gray', linestyle='--', linewidth=0.4)
    plt.title("Plant coverage over time")
    plt.xlabel("Date")
    plt.ylabel("Coverage (%)")
    
    graph_path = join_path(results_base_dir, "stats.jpg")
    plt.savefig(graph_path)
    print(f"\nGraph created at {graph_path}")


if __name__ == "__main__":

    _args = sys.argv
    _script_name = os.path.basename(_args.pop(0))
    _usage_text = "\n".join([
        "\nProcesses a full dataset and gets the stats",
        "\nUsage:",
        f"    {_script_name} all /the/path/to/the/dataset",
        f"    {_script_name} process /the/path/to/the/dataset",
        f"    {_script_name} stats",
    ])
    
    action = _args.pop(0) if _args else None
    dataset_base_dir = _args.pop(0) if _args else None

    if not action:
        print("\nMust define an action! Options: [all, process, stats]")
        print(_usage_text)
        exit(1)
    
    if action in ["process", "all"] and not dataset_base_dir:
        print("\nMust define the path of the dataset!")
        print(_usage_text)
        exit(1)

    if action == "all":
        process_dir_list()
        get_stats()

    elif action == "process":
        process_dir_list()

    elif action == "stats":
        get_stats()

    else:
        print(f"Action '{action}' not recognized!")
        print(_usage_text)
        exit(1)
