import cv2
import numpy as np
import glob



'''
not good, especially racket overlap with human, the racket will be substructed.
'''

def test():
    # List of image paths
    image_paths = glob.glob('data/from_bag_1/*.jpg')
    image_paths.sort()

    # Initialize the background subtractor
    backSub = cv2.createBackgroundSubtractorMOG2(20,10,False)
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))

    for image_path in image_paths:
        # Read the image
        frame = cv2.imread(image_path)

        if frame is None:
            break

        # Apply the background subtractor
        fgMask = backSub.apply(frame)
        fgMask = cv2.morphologyEx(fgMask, cv2.MORPH_OPEN, kernel)

        # Show the original image and the foreground mask
        cv2.imshow('FG Mask', frame)
            
        keyboard = cv2.waitKey(0)
        if keyboard == ord('q') or keyboard == 27:
            break

    cv2.destroyAllWindows()

if __name__ == '__main__':
    test()