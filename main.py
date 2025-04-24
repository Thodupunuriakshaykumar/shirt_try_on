# import os
# import cv2
# import cvzone
# import numpy as np
# import logging
# from cvzone.PoseModule import PoseDetector

# # Setup logging configuration
# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger(__name__)

# def main():
#     try:
#         # Check paths for video and resources
#         video_path = "Resources/Videos/1.mp4"
#         shirt_folder = "Resources/Shirts"
#         button_path = "Resources/button.png"
        
#         if not os.path.isfile(video_path):
#             raise FileNotFoundError(f"Video file not found: {video_path}")
#         if not os.path.isdir(shirt_folder):
#             raise FileNotFoundError(f"Shirt folder not found: {shirt_folder}")
#         if not os.path.isfile(button_path):
#             raise FileNotFoundError(f"Button image not found: {button_path}")

#         # Initialize video capture
#         cap = cv2.VideoCapture(video_path)
#         if not cap.isOpened():
#             raise Exception("Video capture could not be opened")

#         # Get the video dimensions
#         width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
#         height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
#         logger.info(f"Video resolution: {width}x{height}")
        
#         # Load navigation buttons
#         imgButtonRight = cv2.imread(button_path, cv2.IMREAD_UNCHANGED)
#         if imgButtonRight is None:
#             raise Exception("Button image could not be loaded")
#         imgButtonLeft = cv2.flip(imgButtonRight, 1)

#         # List available shirts and initialize parameters
#         listShirts = os.listdir(shirt_folder)
#         if not listShirts:
#             raise Exception("No shirt images found in the folder")
#         imageNumber = 0
#         counterRight = 0
#         counterLeft = 0
#         selectionSpeed = 10

#         # Initialize the pose detector (from CVZone)
#         detector = PoseDetector()

#         while True:
#             success, img = cap.read()
#             if not success:
#                 cap.set(cv2.CAP_PROP_POS_FRAMES, 0)  # Loop back if end is reached
#                 continue

#             # Detect human pose
#             img = detector.findPose(img)
#             lmList, bboxInfo = detector.findPosition(img, bboxWithHands=False, draw=False)

#             # Only proceed if we have a sufficient number of landmarks
#             if lmList is not None and len(lmList) >= 25:
#                 # Landmarks we use:
#                 # lm0: Nose (for vertical alignment reference)
#                 # lm11: Left Shoulder, lm12: Right Shoulder
#                 # lm23: Right Hip, lm24: Left Hip
#                 nose = lmList[0][1:3]
#                 lm11 = lmList[11][1:3]  # Left shoulder (x,y)
#                 lm12 = lmList[12][1:3]  # Right shoulder (x,y)
#                 lm23 = lmList[23][1:3]  # Right hip
#                 lm24 = lmList[24][1:3]  # Left hip

#                 # Compute the center of the shoulders
#                 shoulder_center_x = (lm11[0] + lm12[0]) // 2
#                 shoulder_center_y = (lm11[1] + lm12[1]) // 2

#                 # Estimate shoulder width and a rough torso length.
#                 # Using Euclidean distance between shoulders for width:
#                 shoulderWidth = int(np.linalg.norm(np.array(lm11) - np.array(lm12)))
#                 # Torso length: average vertical distance between shoulders and hips
#                 avgHipY = (lm23[1] + lm24[1]) / 2
#                 torsoLength = int(avgHipY - shoulder_center_y)
                
#                 # Load the current shirt image (ensure it has transparency i.e., PNG)
#                 shirtPath = os.path.join(shirt_folder, listShirts[imageNumber])
#                 imgShirt = cv2.imread(shirtPath, cv2.IMREAD_UNCHANGED)
#                 if imgShirt is None:
#                     logger.warning(f"Failed to load shirt image: {shirtPath}")
#                     continue

#                 # Resize shirt image based on the measured body dimensions
#                 # Increase width by a small factor (for natural fit)
#                 widthOfShirt = int(shoulderWidth * 1.4)
#                 # Height can be computed as a fraction of the torso length.
#                 # Here we use torso length multiplied by a factor; adjust as needed.
#                 heightOfShirt = int(torsoLength * 1.2)

#                 # Ensure minimum dimensions for visibility
#                 widthOfShirt = max(widthOfShirt, 130)
#                 heightOfShirt = max(heightOfShirt, 150)

#                 imgShirt = cv2.resize(imgShirt, (widthOfShirt, heightOfShirt))

#                 # Positioning the shirt:
#                 # Horizontal position: center it around the shoulder center.
#                 shirt_x = shoulder_center_x - widthOfShirt // 2
#                 # Vertical position: align so the shirt’s collar area (top 20% of the shirt)
#                 # meets or slightly under the shoulders.
#                 # We adjust based on the difference between nose and shoulder for a natural offset.
#                 vertical_offset = int(0.2 * heightOfShirt)
#                 shirt_y = shoulder_center_y - vertical_offset

#                 # Make sure the shirt does not go out-of-frame
#                 shirt_x = max(0, min(shirt_x, width - widthOfShirt))
#                 shirt_y = max(0, min(shirt_y, height - heightOfShirt))

#                 # Overlay the shirt image with an alpha channel using cvzone's overlayPNG
#                 img = cvzone.overlayPNG(img, imgShirt, (shirt_x, shirt_y))

#                 # Add navigation buttons (you can adjust their Y position as desired)
#                 buttonY = height // 2
#                 img = cvzone.overlayPNG(img, imgButtonRight, (width - 150, buttonY))
#                 img = cvzone.overlayPNG(img, imgButtonLeft, (50, buttonY))

#                 # Gesture handling for changing shirts based on hand (landmarks 15 and 16)
#                 # We check the x-coordinates of hand landmarks to detect "pushing" the button.
#                 # If left hand (landmark 16) is to the left side and right hand (landmark 15) is to the right side.
#                 if lmList[16][0] < width // 3:
#                     counterLeft += 1
#                     cv2.ellipse(img, (120, buttonY + 5), (60, 60), 0, 0,
#                                 counterLeft * selectionSpeed, (0, 255, 0), 15)
#                     if counterLeft * selectionSpeed > 360:
#                         counterLeft = 0
#                         imageNumber = max(0, imageNumber - 1)
#                 elif lmList[15][0] > (width * 2) // 3:
#                     counterRight += 1
#                     cv2.ellipse(img, (width - 85, buttonY + 5), (60, 60), 0, 0,
#                                 counterRight * selectionSpeed, (0, 255, 0), 15)
#                     if counterRight * selectionSpeed > 360:
#                         counterRight = 0
#                         imageNumber = min(len(listShirts) - 1, imageNumber + 1)
#                 else:
#                     counterLeft, counterRight = 0, 0

#             # Display the image
#             cv2.imshow("Virtual Shirt Try-On", img)
#             # Exit loop if 'q' is pressed
#             if cv2.waitKey(1) & 0xFF == ord('q'):
#                 break

#     except Exception as e:
#         logger.error(f"Error: {str(e)}")
#     finally:
#         if 'cap' in locals():
#             cap.release()
#         cv2.destroyAllWindows()

# if __name__ == "__main__":
#     main()      




import os
import cv2
import cvzone
import numpy as np
import logging
from cvzone.PoseModule import PoseDetector

# Setup logging configuration
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    try:
        # Check paths for video and resources
        video_path = "Resources/Videos/1.mp4"
        shirt_folder = "Resources/Shirts"
        button_path = "Resources/button.png"
        
        if not os.path.isfile(video_path):
            raise FileNotFoundError(f"Video file not found: {video_path}")
        if not os.path.isdir(shirt_folder):
            raise FileNotFoundError(f"Shirt folder not found: {shirt_folder}")
        if not os.path.isfile(button_path):
            raise FileNotFoundError(f"Button image not found: {button_path}")

        # Initialize video capture
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            raise Exception("Video capture could not be opened")

        # Get the video dimensions
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        logger.info(f"Video resolution: {width}x{height}")
        
        # Load navigation buttons
        imgButtonRight = cv2.imread(button_path, cv2.IMREAD_UNCHANGED)
        if imgButtonRight is None:
            raise Exception("Button image could not be loaded")
        imgButtonLeft = cv2.flip(imgButtonRight, 1)

        # List available shirts and initialize parameters
        listShirts = os.listdir(shirt_folder)
        if not listShirts:
            raise Exception("No shirt images found in the folder")
        imageNumber = 0
        counterRight = 0
        counterLeft = 0
        selectionSpeed = 10

        # Initialize the pose detector (from CVZone)
        detector = PoseDetector()

        while True:
            success, img = cap.read()
            if not success:
                cap.set(cv2.CAP_PROP_POS_FRAMES, 0)  # Loop back if end is reached
                continue

            # Detect human pose
            img = detector.findPose(img)
            lmList, bboxInfo = detector.findPosition(img, bboxWithHands=False, draw=False)

            # Only proceed if we have a sufficient number of landmarks
            if lmList is not None and len(lmList) >= 25:
                # Use landmarks 11 (left shoulder) and 12 (right shoulder)
                left_shoulder = np.array(lmList[11][1:3])
                right_shoulder = np.array(lmList[12][1:3])

                # Shoulder center and width
                shoulder_center = (left_shoulder + right_shoulder) / 2
                shoulder_width = int(np.linalg.norm(left_shoulder - right_shoulder))

                # Load shirt
                shirtPath = os.path.join(shirt_folder, listShirts[imageNumber])
                imgShirt = cv2.imread(shirtPath, cv2.IMREAD_UNCHANGED)
                if imgShirt is None:
                    logger.warning(f"Failed to load shirt image: {shirtPath}")
                    continue

                # Resize shirt
                widthOfShirt = int(shoulder_width * 1.6)
                heightOfShirt = int(widthOfShirt * imgShirt.shape[0] / imgShirt.shape[1])
                imgShirt = cv2.resize(imgShirt, (widthOfShirt, heightOfShirt))

                # Align shirt just below the shoulders
                shirt_x = int(shoulder_center[0] - widthOfShirt / 2)
                shirt_y = int(shoulder_center[1] - heightOfShirt * 0.25)

                # Clip values to frame size
                shirt_x = max(0, min(shirt_x, width - widthOfShirt))
                shirt_y = max(0, min(shirt_y, height - heightOfShirt))

                # Overlay shirt
                img = cvzone.overlayPNG(img, imgShirt, (shirt_x, shirt_y))

                # Draw navigation buttons
                buttonY = height // 2
                img = cvzone.overlayPNG(img, imgButtonRight, (width - 150, buttonY))
                img = cvzone.overlayPNG(img, imgButtonLeft, (50, buttonY))

                # Gesture handling
                if lmList[16][0] < width // 3:
                    counterLeft += 1
                    cv2.ellipse(img, (120, buttonY + 5), (60, 60), 0, 0,
                                counterLeft * selectionSpeed, (0, 255, 0), 15)
                    if counterLeft * selectionSpeed > 360:
                        counterLeft = 0
                        imageNumber = max(0, imageNumber - 1)
                elif lmList[15][0] > (width * 2) // 3:
                    counterRight += 1
                    cv2.ellipse(img, (width - 85, buttonY + 5), (60, 60), 0, 0,
                                counterRight * selectionSpeed, (0, 255, 0), 15)
                    if counterRight * selectionSpeed > 360:
                        counterRight = 0
                        imageNumber = min(len(listShirts) - 1, imageNumber + 1)
                else:
                    counterLeft, counterRight = 0, 0

            # Display final output
            cv2.imshow("Virtual Shirt Try-On", img)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    except Exception as e:
        logger.error(f"Error: {str(e)}")
    finally:
        if 'cap' in locals():
            cap.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
