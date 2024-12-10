#!/usr/bin/env python3

import sys, os, json, cv2, numpy as np
from os.path import join as join_path
from os.path import abspath
from glob import glob
from plant_coverage import coverage
import matplotlib.pyplot as plt
from calendar import month_name as month_name_list




dataset_dirname_list = [
    "coverage/240508_DW_62", 
    "coverage/240514_DW_63", 
    "coverage/240521_DW_84", 
    "biodiversity/240814_DW_F1_42"
]

def batch_process_single_dir(source_dir, dest_dir, limit=-1):

    source_dir = abspath(source_dir)
    if not os.path.isdir(source_dir):
        print(f"Source path '{source_dir}' is not a directory")
        return
    
    dest_dir = abspath(dest_dir)
    os.makedirs(dest_dir, exist_ok=True)

    # processing may take some time, so we count the images first to provide a progress status while processing
    image_filename_list = [
        join_path(source_dir, filename) for filename in os.listdir(source_dir) 
            if filename.lower().endswith(".jpg") and os.path.isfile(join_path(source_dir, filename))
    ]
    image_filename_list = image_filename_list[:limit] if 0 <= limit < len(image_filename_list) else image_filename_list

    print(f"\nProcessing dataset in {source_dir}")
    total_files = len(image_filename_list)
    if total_files == 0:
        print("No JPG images were found in the source directory or limit is 0. Nothing to do.")
        return

    processed_images_list = []
    for index, src_image_filepath in enumerate(image_filename_list):

        image, coverage_val = coverage.process_image(src_image_filepath)
        image_filename = os.path.basename(src_image_filepath)
        dest_image_filepath = join_path(dest_dir, image_filename)

        processed_images_list.append({
            "image_filename": image_filename,
            "coverage": coverage_val
        })
        
        cv2.imwrite(dest_image_filepath, image)
        print(f"\rProgress: {index+1}/{total_files}", end='', flush=True)

    
    coverage_list = [item["coverage"] for item in processed_images_list]
    results_dict = {
        "stats": {
            "count": len(coverage_list),
            "average": np.average(coverage_list),
            "std_dev": np.std(coverage_list),
            "max": np.max(coverage_list),
            "min": np.min(coverage_list),
        },
        "processed_images": processed_images_list,
    }

    with open(join_path(dest_dir, "_results.json"), "w") as json_file:
        json.dump(results_dict, json_file, indent=4)
    
    print(f"\nDone! - Results created in {dest_dir}")

def batch_process_dataset(dataset_root_dir, results_root_dir):

    for dir_name in dataset_dirname_list:

        source_path = join_path(dataset_root_dir, dir_name)
        dest_path = join_path(results_root_dir, dir_name)
        batch_process_single_dir(source_path, dest_path)

def create_stats(results_root_dir):

    x_values = []
    y_values = []
    y_errr = []
    for dir_name in dataset_dirname_list:

        dest_path = join_path(results_root_dir, dir_name)
        json_filepath = glob(f"{dest_path}/*.json")
        if not json_filepath:
            continue

        json_filepath = json_filepath[0]
        with open(json_filepath, 'r') as json_file:
            stats_dict = json.load(json_file)["stats"]
            date = os.path.basename(dir_name).split("_")[0]
            date = f"{date[:2]}-{month_name_list[int(date[2:4])]}-{date[4:]}"
            x_values.append(date)
            y_values.append(stats_dict["average"])
            y_errr.append(stats_dict["std_dev"])
    if not x_values:
        print("\nNo data was found to generate stats")
        return
    plt.scatter(x_values, y_values) # create the scatter plot
    x1,x2,y1,y2 = plt.axis()
    plt.axis((x1-0.3, x2+0.5, y1-0.3, y2+1)) # expand slightly the plot area to fit text
    plt.gca().set_ylim([0, 100]) # make the y axis show 0 and 100 values
    plt.errorbar(x_values, y_values, yerr=y_errr, fmt="o", capsize=5) # show the error lines
    for i, j in zip(range(len(x_values)), y_values):
        plt.text(i+0.1, j, f"{j:.2f}%") # add the value text next to each pont

    plt.grid(color='gray', linestyle='--', linewidth=0.4)
    plt.title("Plant coverage over time")
    plt.xlabel("Date")
    plt.ylabel("Coverage (%)")
    
    graph_path = join_path(results_root_dir, "stats.jpg")
    plt.savefig(graph_path)
    print(f"\nGraph created at {graph_path}")

if __name__ == "__main__":

    _args = sys.argv.copy()
    _script_name = os.path.basename(_args.pop(0))
    
    _action = _args.pop(0) if _args else None

    if _action == "batch":
        _dataset_root_dir = _args.pop(0) if _args else None
        if not _dataset_root_dir:
            print("Need to input dataset root dir!")
            exit(1)

        _results_root_dir = _args.pop(0) if _args else None
        if not _results_root_dir:
            print("Need to input results root dir!")
            exit(1)
        batch_process_dataset(_dataset_root_dir, _results_root_dir)
        create_stats(_results_root_dir)
    
    elif _action == "stats":
        _results_root_dir = _args.pop(0) if _args else None
        if not _results_root_dir:
            print("Need to input results root dir!")
            exit(1)
        create_stats(_results_root_dir)
        
    else:
        print(f"Action '{_action}' not recognized.")
        exit(1)


