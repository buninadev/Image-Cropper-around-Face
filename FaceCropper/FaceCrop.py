import os
import cv2


class FaceCrop:
    def __init__(self, input_folder, output_folder):
        self.face_cascade = cv2.CascadeClassifier(
            "FaceCropper/haarcascade_frontalface_default.xml"
        )
        self.input_folder = input_folder
        self.output_folder = output_folder
        self.preprocess_images = []

    def detect_faces(self):
        for filename in os.listdir(self.input_folder):
            print("Processing file: {}".format(filename))
            if not filename.endswith(".jpg") and not filename.endswith(".png"):
                print("Not an image! Skipping file: {}".format(filename))
                continue
            img = cv2.imread(os.path.join(self.input_folder, filename))
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            faces = self.face_cascade.detectMultiScale(gray, 1.2, 4)
            if len(faces) == 0:
                print("No faces detected!")
                continue
            for x, y, w, h in faces:
                roi_color = img[y : y + h, x : x + w]
                cv2.imwrite(os.path.join(self.output_folder, filename), roi_color)
                self.preprocess_images.append(
                    {"x": x, "y": y, "w": w, "h": h, "image": img, "filename": filename}
                )
                print("Face detected and cropped successfully!")
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
            x1 = 0 if width_small else int(x_center - smaller_side / 2)
            y1 = 0 if not width_small else int(y_center - smaller_side / 2)
            x2 = smaller_side - x1 if width_small else int(x_center + smaller_side / 2)
            y2 = (
                smaller_side - y1
                if not width_small
                else int(y_center + smaller_side / 2)
            )

            print(f"width: {x2-x1} | height: {y2-y1}")
            roi_color = img[y1:y2, x1:x2]
            cv2.imwrite(os.path.join(self.output_folder, "crop-" + filename), roi_color)
            print(f"{filename} cropped successfully! ")