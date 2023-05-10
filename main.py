from FaceCropper.FaceCrop import FaceCrop


if __name__ == "__main__":
    FaceCrop = FaceCrop("input_images", "output_images")
    FaceCrop.detect_faces()
    FaceCrop.crop_around_faces()
