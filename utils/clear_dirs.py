import os


IMAGE_EXTENSIONS = ["jpg", "png", "jpeg"]


def list_of_files_in_folder_recursive(folder: str):
    list_of_files = []
    for root, dirs, files in os.walk(folder):
        for file in files:
            # remove folder from root and remove / from the beginning of the string
            list_of_files.append((root, file))
    return list_of_files


def clear_images_from_folder(folder: str):
    try:
        list_images_in_folder = filter(
            lambda f: f[1].split(".")[1] in IMAGE_EXTENSIONS,
            list_of_files_in_folder_recursive(folder),
        )
        for root, image in list_images_in_folder:
            os.remove(os.path.join(root, image))
    except:
        print("Error clearing folder %s" % folder)


def clear_folders(folders: list[str]):
    for folder in folders:
        clear_images_from_folder(folder)


if __name__ == "__main__":
    # Path to the folder containing the input images
    input_folder = "input_images"
    # Path to the folder of the cropped images
    output_folder = "output_images"
    # Path to the post-processed images
    post_processed_folder = "post_processed_images"

    clear_folders([input_folder, output_folder, post_processed_folder])
