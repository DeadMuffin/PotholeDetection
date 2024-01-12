import argparse
import cv2
import os
# local imports
import camera
import detection
import gps_module
from utils.image_utils import save_image, label_image
from utils.tof_utils import get_pothole_size, get_avg_pothole_depth, get_max_pothole_depth
from utils.utils import save_text, create_dir


def main():
    print(f"\nPRESS ESC or ctr-c in headless to Stop\n")
    file_path = os.path.dirname(__file__)
    parser = argparse.ArgumentParser(description="Pothole detection.")
    parser.add_argument("--headless", action="store_true", default=False,
                        help="Run without Video? Defaults to False.")
    parser.add_argument("--weights_path", type=str, default=f"{file_path}/../data/models/fallback_best.pt",
                        help="The path to the models weights file. Defaults to data/weights/fallback_best.pt")
    parser.add_argument("--cam_source", type=int, default=0,
                        help="The Number of the camera to use. Defaults to 0")
    parser.add_argument("--cam_width", type=int, default=1920,
                        help="The width of the camera. Defaults to 1920")
    parser.add_argument("--cam_height", type=int, default=1080,
                        help="The height of the camera. Defaults to 1080")

    # TODO decide to make output path optional as well
    args = parser.parse_args()
    weights_path = args.weights_path
    cam_source = args.cam_source
    cam_width = args.cam_width
    cam_height = args.cam_height
    headless = args.headless

    # init
    detector = detection.Detection(weights_path)
    cam = camera.Camera(cam_source, cam_width, cam_height)
    counter = 0

    # main
    while True:
        if cv2.waitKey(30) == 27:  # Press Esc to stop
            break

        frame = cam.get_frame()
        pothole_detection = detector.detect_potholes(frame)
        frame = label_image(frame, pothole_detection, detector.model.names)

        if pothole_detection.confidence.size > 0 and pothole_detection.confidence[0] > 0.5:
            print("-------------STORING POTHOLE---------------")  # TODO delete later, just for Debug
            gps_coordinates = gps_module.read_gps_coordinates()

            # tof_image = tof_camera.capture_tof_image(pothole_detection.xyxy[0]) TODO whole tof part

            # Save images and data
            create_dir(f"data/results/{counter}")
            # save_image(tof_image, f"data/result/{counter}/tof_capture.ply")
            save_image(frame, f"data/results/{counter}/frame.jpg")
            save_text(f"Latitude: {gps_coordinates[0]}\nLongitude: {gps_coordinates[1]}\n",
                      f"data/results/{counter}/result.txt")
            save_text(f"Average Pothole Depth: {get_avg_pothole_depth()}\n",
                      f"data/results/{counter}/result.txt")
            save_text(f"Max Pothole Depth: {get_max_pothole_depth()}\n",
                      f"data/results/{counter}/result.txt")
            save_text(f"Pothole Size: {get_pothole_size()}\n",
                      f"data/results/{counter}/result.txt")

            counter += 1

        if not headless:
            cv2.imshow("Pothole Detection", frame)


if __name__ == "__main__":
    main()
