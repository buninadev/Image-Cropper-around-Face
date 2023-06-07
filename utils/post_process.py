import os
import numpy as np

import skimage.io as io

# output_image has name "crop-face-x-<id>-FirstName-LastName.jpg"
# input_image has name "<id>-FirstName-LastName.jpg"


# function to get the id from the image name
def get_id_from_image_name(image_name):
    return image_name.split("-")[0]


# function to get the cropped image name from the image name
def get_id_from_cropped_image_name(image_name):
    return image_name.split("-")[3]


# function to cross check the cropped images with the original images
def get_corresponding_cropped_image(images, cropped_images):
    dict_images = {}
    for image in images:
        # find corresponding cropped image
        id_image = get_id_from_image_name(image)
        cropped_image = [
            cropped_image
            for cropped_image in cropped_images
            if get_id_from_cropped_image_name(cropped_image) == id_image
        ]
        if len(cropped_image) == 0:
            dict_images[get_id_from_image_name(image)] = {
                "image": image,
                "cropped_image": None,
            }
            continue
        else:
            cropped_image = cropped_image[0]

        dict_images[get_id_from_image_name(image)] = {
            "image": image,
            "cropped_image": cropped_image,
        }

    return dict_images


def write_image(read_folder, post_processed_folder, value, value_name):
    image = io.imread(os.path.join(read_folder, value[value_name]))
    io.imsave(os.path.join(post_processed_folder, value["image"]), image)


if __name__ == "__main__":
    # Path to the folder containing the input images
    input_folder = "input_images"
    # Path to the folder of the cropped images
    output_folder = "output_images"
    # Path to the post-processed images
    post_processed_folder = "post_processed_images"

    # try make dir for post processed else clearing the post_processed_folder
    try:
        os.mkdir(post_processed_folder)
    except:
        try:
            for image in os.listdir(post_processed_folder):
                os.remove(os.path.join(post_processed_folder, image))
        except:
            print("Error clearing post_processed_folder")

    # get all images in the input folder
    images = [
        image
        for image in os.listdir(input_folder)
        if image.endswith(".jpg") or image.endswith(".png")
    ]
    number_of_images = len(images)
    # get all images in the output folder
    cropped_images = [
        image
        for image in os.listdir(output_folder)
        if image.endswith(".jpg") or image.endswith(".png")
    ]
    name_of_images_not_cropped = []
    # get the corresponding cropped images
    dict_images = get_corresponding_cropped_image(images, cropped_images)

    # loop through the images , if there is no cropped image, then copy the image to the post_processed_folder
    number_of_cropped_images = 0
    for key, value in dict_images.items():
        try:
            if value["cropped_image"] == None:
                write_image(input_folder, post_processed_folder, value, "image")
                name_of_images_not_cropped.append(value["image"])
                continue
            # if there is a cropped image, then copy the cropped image to the post_processed_folder
            write_image(output_folder, post_processed_folder, value, "cropped_image")
            number_of_cropped_images += 1
        except Exception as e:
            print(value["image"])
            name_of_images_not_cropped.append(value["image"])

            print("Error: ", e)
            # copy the image to the post_processed_folder without using cv2
            os.system(
                "cp "
                + os.path.join(input_folder, value["image"])
                + " "
                + os.path.join(post_processed_folder, value["image"])
            )
            continue

    print(
        "Number of images: ",
        number_of_images,
        "Number of cropped images: ",
        number_of_cropped_images,
        "Number of images without cropped images: ",
        number_of_images - number_of_cropped_images,
    )
    print("Require manual treatment:")
    for name in name_of_images_not_cropped:
        name = name.split(".")[0]
        name = name.split("-")
        name = name[1] + " " + name[2]
        print(name)

    # final check, check if the number of images in the post_processed_folder is equal to the number of images in the input folder
    post_processed_images = [
        image
        for image in os.listdir(post_processed_folder)
        if image.endswith(".jpg") or image.endswith(".png")
    ]
    if len(post_processed_images) == number_of_images:
        print("Post processed images are correct")
    else:
        print("Post processed images are not correct")
        print("Number of images in post_processed_folder: ", len(post_processed_images))
