#!/usr/bin/env python3

import cv2, os, json, sys, numpy as np

## functions for image processing ======================================================================================

def rotate_image(image):
    height, width = image.shape[:2]
    if height > width:
        return cv2.rotate(image, cv2.ROTATE_90_CLOCKWISE)
    return image

def resize_image(image, width=640, height=480):
    return cv2.resize(image, (width, height))

def get_corner_points(mask):

    white_pixels = np.column_stack(np.where(mask == 255))
    height, width = mask.shape[:2]
    corners_coordinates = [
        (0, 0),
        (0, width - 1),
        (height - 1, width - 1),
        (height - 1, 0)
    ]
    points_list = []
    for corner_coordinates in corners_coordinates:
        distances = np.linalg.norm(white_pixels - corner_coordinates, axis=1)
        closest_index = np.argmin(distances)
        x, y = white_pixels[closest_index][::-1]
        points_list.append([x, y])
    return np.array(points_list)

def get_silver_frame_mask(image):

    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    lower_white = (0, 0, 200) 
    upper_white = (180, 55, 255)
    mask = cv2.inRange(hsv, lower_white, upper_white)

    mask = cv2.threshold(mask, 200, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3,3))
    mask = 255 - cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel, iterations=2)
    return mask

def get_area_mask(image):
    
    silver_frame_mask = get_silver_frame_mask(image)
    corner_points = get_corner_points(silver_frame_mask)

    height, width = image.shape[:2]
    mask = np.zeros((height, width), dtype=np.uint8)
    cv2.fillPoly(mask, [corner_points], color=255)

    mask = np.bitwise_xor(mask, silver_frame_mask)
    mask = cv2.medianBlur(mask, 5)

    return mask

def get_greens_mask(image):

    ## Convert to HSV
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    # limits for the 4000x3000 image
    # hsv_lower_limit = (30, 30, 80)
    # hsv_upper_limit = (70, 255, 255)

    # limits for the 640x480 image
    hsv_lower_limit = (30, 30, 10)
    hsv_upper_limit = (70, 255, 255)

    # Create binary mask for green color
    mask = cv2.inRange(hsv, hsv_lower_limit, hsv_upper_limit)

    # remove small particles in the mask - only requried when using the full 4000x3000 image
    # mask = cv2.threshold(mask, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]
    # kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1,1))
    # mask = 255 - cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel, iterations=2)

    return mask

def get_plant_coverage(image, area_mask, greens_mask):

    full_mask = np.bitwise_and(area_mask, greens_mask)
    bool_mask = full_mask > 0
    masked_image = np.zeros_like(image, np.uint8)
    masked_image[bool_mask] = image[bool_mask]

    pixels_in_area = cv2.countNonZero(area_mask)
    pixels_in_greens = np.count_nonzero(np.any(masked_image > 0, axis=2))
    coverage = pixels_in_greens * 100 / pixels_in_area
    return masked_image, coverage

def put_text(image, text):
    
    position = (5, 30)
    font = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = 4/len(text)
    color = (255, 255, 255)
    thickness = 1
    line_type = cv2.LINE_AA

    text_width, text_height = cv2.getTextSize(text, font, font_scale, thickness)[0]
    top_left = (position[0], position[1] - text_height - 5)
    bottom_right = (position[0] + text_width, position[1] + 5)

    cv2.rectangle(image, top_left, bottom_right, (0, 0, 0), -1)
    cv2.putText(image, text, position, font, font_scale, color, thickness, line_type)

def process_image(image_source):

    if os.path.isfile(image_source):
        image = cv2.imread(image_source)
    image = rotate_image(image)
    image = resize_image(image)

    area_mask = get_area_mask(image)
    greens_mask = get_greens_mask(image)

    image, coverage = get_plant_coverage(image, area_mask, greens_mask)
    put_text(image, f"{coverage:.2f}%" )

    return image, coverage


# utility functions ====================================================================================================

def get_images_list(source_dir_or_filename):

    image_filename_list = []
    if os.path.isdir(source_dir_or_filename):
        for filename in os.listdir(source_dir_or_filename):
            full_filepath = os.path.join(source_dir_or_filename, filename)
            if filename.lower().endswith('.jpg') and os.path.isfile(full_filepath):
                image_filename_list.append(full_filepath)

    elif os.path.isfile(source_dir_or_filename) and source_dir_or_filename.lower().endswith('.jpg'):

        image_filename_list.append(os.path.abspath(source_dir_or_filename))
    else:
        raise Exception(f"Location {source_dir_or_filename} is not a JPG file or a directory")

    return image_filename_list

def check_or_create_destination_dir(dest_dir):
    if not dest_dir:
        dest_dir = os.path.dirname(os.path.realpath(__file__))
        dest_dir = os.path.join(dest_dir, "coverage-results")

    dest_dir = os.path.abspath(dest_dir)
    os.makedirs(dest_dir, exist_ok=True)
    return dest_dir

def create_analytics_result(processed_images_list):

    coverages_list = [item["coverage"] for item in processed_images_list]
    results_dict = {
        "stats": {
            "count": len(coverages_list),
            "average": np.average(coverages_list),
            "std_dev": np.std(coverages_list),
            "max": np.max(coverages_list),
            "min": np.min(coverages_list),
        },
        "processed_images": processed_images_list,
    }
    return results_dict
    
def process_dir_or_image(source_dir_or_filename, dest_dir=None, limit=-1):

    dest_dir = check_or_create_destination_dir(dest_dir)

    # processing may take some time, so we count the images first to provide a progress status while processing
    image_filename_list = get_images_list(source_dir_or_filename)
    image_filename_list = image_filename_list[:limit] if 0 <= limit < len(image_filename_list) else image_filename_list

    total_files = len(image_filename_list)
    if total_files == 0:
        print("No JPG images were found or limit is 0. Nothing to do.")
        return

    processed_images_list = []
    for index, src_filepath in enumerate(image_filename_list):

        image, coverage = process_image(src_filepath)
        image_filename = os.path.basename(src_filepath)
        dest_filepath = os.path.join(dest_dir, image_filename)

        processed_images_list.append({
            "image_filename": os.path.basename(src_filepath),
            "coverage": coverage
        })
        
        cv2.imwrite(dest_filepath, image)
        print(f"\rProgress: {index+1}/{total_files}", end='', flush=True)

    
    results_dict = create_analytics_result(processed_images_list)

    with open(os.path.join(dest_dir, "_results.json"), "w") as out_file:
        json.dump(results_dict, out_file, indent=4)
    
    print(f"\nDone! - Results created in {dest_dir}")


if __name__ == "__main__":

    _args = sys.argv
    _script_name = os.path.basename(_args.pop(0))
    _usage_text = "\n".join([
        "\nProcesses one or more images from the coverage dataset",
        "",
        f"Usage: {_script_name} -s <source-dir or file> [-d <destination-dir>] [-l <limit>]",
        "\nArgs:",
        "    -s: source directory path or a single image path (required)",
        "    -d: destination directory path (optional)",
        "    -l: a limit value for the amount of images to process - useful for testing (optional)",
    ])
    
    _source_dir_or_filename = None
    _dest_dir = None
    _limit = -1

    while _args:
        arg = _args.pop(0)
        match arg:
            case "-s":
                _source_dir_or_filename = _args.pop(0)
            case "-d":
                _dest_dir = _args.pop(0)
            case "-l":
                _limit = int(_args.pop(0))
            case "-h":
                print(_usage_text)
                exit(1)
            case _:
                print("Unrecognized option: ", arg)
                print(_usage_text)
                exit(1)
    

    if _source_dir_or_filename is None:
        print("Need to specify the source file or directory")
        print(_usage_text)
        exit(1)


    process_dir_or_image(_source_dir_or_filename, _dest_dir, limit=_limit)
    

