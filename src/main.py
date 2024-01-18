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
    parser.add_argument("--nogps", action="store_true", default=False,
                        help="Run without GPS. Defaults to False.")
    parser.add_argument("--notof", action="store_true", default=False,
                        help="Run without TOF. Defaults to False.")
    parser.add_argument("--weights_path", type=str, default=f"{file_path}/../data/models/fallback_best.pt",
                        help="The path to the models weights file. Defaults to data/weights/fallback_best.pt")
    parser.add_argument("--cam_source", type=int, default=0,
                        help="The Number of the camera to use. Defaults to 0")
    parser.add_argument("--cam_width", type=int, default=1920,
                        help="The width of the camera. Defaults to 1920")
    parser.add_argument("--cam_height", type=int, default=1080,
                        help="The height of the camera. Defaults to 1080")
    parser.add_argument("--gps_node", type=str, default='/dev/tty.usbmodem1301',
                        help="The gps node where the USB is connected. Defaults to /dev/tty.usbmodem1301")

    # TODO decide to make output path optional as well
    args = parser.parse_args()
    weights_path = args.weights_path
    cam_source = args.cam_source
    cam_width = args.cam_width
    cam_height = args.cam_height
    headless = args.headless
    nogps = args.nogps
    notof = args.notof
    gps_node = args.gps_node

    # init
    detector = detection.Detection(weights_path)
    cam = camera.Camera(cam_source, cam_width, cam_height)
    counter = len([d for d in os.listdir('data/results') if os.path.isdir(os.path.join('data/results', d))])

    # main
    while True:
        if cv2.waitKey(30) == 27:  # Press Esc to stop
            break

        frame = cam.get_frame()
        pothole_detection = detector.detect_potholes(frame)
        frame = label_image(frame, pothole_detection, detector.model.names)

        if pothole_detection.confidence.size > 0 and pothole_detection.confidence[0] > 0.5:
            print("-------------STORING POTHOLE---------------")  # TODO delete later, just for Debug
            if not nogps:
                latitude, longitude = gps_module.get_gps_coordinates(gps_node)

        #   if not notof:
            tof_images = []  # = tof_camera.capture_tof_image(pothole_detection.xyxy[0]) TODO whole tof part

            # Save images and data
            create_dir(f"data/results/{counter}")
            save_image(frame, f"data/results/{counter}/frame.jpg")
            save_text(f"Pothole Confidence: {pothole_detection.confidence[0]}\n",
                      f"data/results/{counter}/result.txt")

            if not nogps:
                save_text(f"Latitude: {int(latitude[:2])}°{latitude[2:4]}.{latitude[4:]}\' N, \nLongitude: {int(longitude[:3])}°{longitude[3:5]}.{longitude[5:]}\' E\n",
                          f"data/results/{counter}/result.txt")
            else:
                save_text("Latitude: no gps\nLongitude: no gps\n",
                          f"data/results/{counter}/result.txt")
            if not notof:
                for i, tof in enumerate(tof_images):
                    #  save_image(tof, f"data/result/{counter}/tof_capture{i}.ply")
                    save_text(f"Average Pothole Depth {i}: {get_avg_pothole_depth()}\n",
                              f"data/results/{counter}/result.txt")
                    save_text(f"Max Pothole Depth {i}: {get_max_pothole_depth()}\n",
                              f"data/results/{counter}/result.txt")
                    save_text(f"Pothole Size {i}: {get_pothole_size()}\n",
                              f"data/results/{counter}/result.txt")
            else:
                save_text("Average Pothole Depth: no tof\nMax Pothole Depth: no tof\nPothole Size: no tof",
                          f"data/results/{counter}/result.txt")
            counter += 1

        if not headless:
            cv2.imshow("Pothole Detection", frame)


if __name__ == "__main__":
    main()
