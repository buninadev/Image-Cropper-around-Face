import math
import os
import cv2
import numpy as np


class FaceCrop:
    def __init__(self, input_folder, output_folder):
        self.face_cascade = cv2.CascadeClassifier(
            "FaceCropper/haarcascade_frontalface_alt.xml"
        )
        self.face_detector = cv2.FaceDetectorYN_create(
            "FaceCropper/face_recognizer_fast.onnx", "", (0, 0)
        )

        self.input_folder = input_folder
        self.output_folder = output_folder
        self.preprocess_images = []

        self.number_of_cropped_images = 0
        self.number_of_images = 0

    def detect_faces(self):
        for filename in os.listdir(self.input_folder):
            print("Processing file: {}".format(filename))
            if not filename.endswith(".jpg") and not filename.endswith(".png"):
                print("Not an image! Skipping file: {}".format(filename))
                continue
            img = cv2.imread(os.path.join(self.input_folder, filename))
            image_to_detect = self.enhance_images(img)
            faces = self.face_cascade.detectMultiScale(image_to_detect, 1.05, 7)
            # self.face_detector.setInputSize(
            #     (image_to_detect.shape[1], image_to_detect.shape[0])
            # )
            # faces = self.face_detector.detect(image_to_detect)
            self.number_of_images += 1
            if len(faces) == 0:
                print("No faces detected!")
                cv2.imwrite(
                    os.path.join(
                        self.output_folder, "undetected", "undetected-" + filename
                    ),
                    img,
                )
                continue
            filtered_faces = faces
            if len(faces) > 1:
                filtered_faces = self.filter_closer_to_center(faces, img)
            for i, (x, y, w, h) in enumerate(filtered_faces):
                self.preprocess_images.append(
                    {
                        "x": x,
                        "y": y,
                        "w": w,
                        "h": h,
                        "image": img,
                        "filename": f"face-{i}-" + filename,
                    }
                )
                print("Face detected!")
                if i == 2:
                    break

    def crop_around_faces(self):
        print("Cropping around faces...")
        for image in self.preprocess_images:
            x = image["x"]
            y = image["y"]
            w = image["w"]
            h = image["h"]
            img = image["image"]
            filename = image["filename"]
            # center of the face
            x_center = x + w / 2
            y_center = y + h / 2

            img_height, img_width, _ = img.shape

            smaller_side = min(img_height, img_width)
            width_small = True if smaller_side == img_width else False
            # new coordinates
            x1 = max(0, 0 if width_small else x_center - smaller_side / 2)
            y1 = max(0, 0 if not width_small else y_center - smaller_side / 2)
            x2 = max(0, smaller_side if width_small else x_center + smaller_side / 2)
            y2 = max(
                0,
                smaller_side if not width_small else y_center + smaller_side / 2,
            )

            if (x_center - smaller_side / 2) < 0:
                if x1 == 0:
                    x2 = min(img_width, x2 - (x_center - smaller_side / 2))

            if (y_center - smaller_side / 2) < 0:
                if y1 == 0:
                    y2 = min(img_height, y2 - (y_center - smaller_side / 2))

            if (x_center + smaller_side / 2) > img_width:
                if x2 == img_width:
                    x1 = max(0, x1 - (x_center + smaller_side / 2 - img_width))

            if (y_center + smaller_side / 2) > img_height:
                if y2 == img_height:
                    y1 = max(0, y1 - (y_center + smaller_side / 2 - img_height))

            y1 = int(y1)
            y2 = int(y2)
            x1 = int(x1)
            x2 = int(x2)
            roi_color = img[y1:y2, x1:x2]
            try:
                cv2.imwrite(
                    os.path.join(self.output_folder, "crop-" + filename), roi_color
                )
                print(f"{filename} cropped successfully! ")
                print(f"width: {x2-x1} | height: {y2-y1}")
                self.number_of_cropped_images += 1
            except Exception as e:
                print(f"Error: {e}")
                continue

        if self.number_of_cropped_images - self.number_of_images != 0:
            print(
                f"Number of cropped images: {self.number_of_cropped_images} / {self.number_of_images}"
            )
        else:
            print(
                f"All images cropped successfully!  {self.number_of_cropped_images} / {self.number_of_images}"
            )

    def enhance_images(self, image):
        lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
        l_channel, a, b = cv2.split(lab)

        # Applying CLAHE to L-channel
        # feel free to try different values for the limit and grid size:
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        cl = clahe.apply(l_channel)

        # merge the CLAHE enhanced L-channel with the a and b channel
        limg = cv2.merge((cl, a, b))

        # Converting image from LAB Color model to BGR color spcae
        enhanced_img = cv2.cvtColor(limg, cv2.COLOR_LAB2BGR)

        # Stacking the original image with the enhanced image

        return enhanced_img

    def filter_closer_to_center(self, faces, image):
        img_height, img_width, _ = image.shape
        center_x = img_width / 2
        center_y = img_height / 2

        faces = sorted(faces, key=lambda face: face[0] * face[1])
        faces = sorted(
            faces,
            key=lambda face: math.sqrt(
                (face[0] - center_x) ** 2 + (face[1] - center_y) ** 2
            ),
        )
        return faces
