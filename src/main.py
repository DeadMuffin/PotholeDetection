import argparse
import cv2
import os
import subprocess
import time
# local imports
import camera
import detection
import gps_module
from utils.image_utils import save_image, label_image
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

        if not headless:
            cv2.imshow("Pothole Detection", frame)

        if pothole_detection.confidence.size > 0 and pothole_detection.confidence[0] > 0.5:
            print("-------------STORING POTHOLE---------------")

            # Save images and data
            create_dir(f"data/results/{counter}")
            save_image(frame, f"data/results/{counter}/frame.jpg")
            save_text(f"Pothole Confidence: {pothole_detection.confidence[0]}\n", f"data/results/{counter}/result.txt")

            if not nogps:
                latitude, longitude = gps_module.get_gps_coordinates(gps_node)  # TODO maybe multithreading
                save_text(f"Latitude: {int(latitude[:2])}°{latitude[2:4]}.{latitude[4:]}\' N, "
                          f"\nLongitude: {int(longitude[:3])}°{longitude[3:5]}.{longitude[5:]}\' E\n",
                          f"data/results/{counter}/result.txt")
            else:
                save_text("Latitude: no gps\nLongitude: no gps\n", f"data/results/{counter}/result.txt")

            if not notof:
                # Befehl zum Aktivieren der virtuellen Umgebung
                activate_cmd = 'venv\\Scripts\\activate'
                camera_is_connected = True
                for i, xyxy in enumerate(pothole_detection.xyxy):
                    p1x = "--p1x " + str(xyxy[0]) + " "
                    p1y = "--p1y " + str(xyxy[1]) + " "
                    p2x = "--p2x " + str(xyxy[2]) + " "
                    p2y = "--p2y " + str(xyxy[3]) + " "
                    storageDir = "--dir " + f"data/results/{counter}" + " "
                    counterAttribute = "--counter " + str(counter) + " "
                    angle = "--angle 45 "
                    index = "--index " + str(i) + " "
                    script_cmd = "python.exe main.py " + p1x + p1y + p2x + p2y + counterAttribute + storageDir + angle + index

                    # first pothole in one image will trigger the camera, every later one will just reuse the tof image
                    if i == 0 or not camera_is_connected:
                        script_cmd += "--create_rrf "
                    combined_cmd = f'{activate_cmd} && {script_cmd}'
                    subprocess.run(combined_cmd, shell=True)
                print("Tof analysis done")
            else:
                save_text("Average Pothole Depth: no tof\nMax Pothole Depth: no tof",
                      f"data/results/{counter}/result.txt")
                time.sleep(1)  # anti-spam for test purpose only if tof deactivates
            counter += 1


if __name__ == "__main__":
    main()
