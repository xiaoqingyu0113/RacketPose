import cv2
import numpy as np
import glob

def test():

    image_paths = glob.glob('data/from_bag_1/*.jpg')
    image_paths.sort()
    backSub = cv2.createBackgroundSubtractorMOG2(2,20,False)
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))

    for image_path in image_paths:
        # Read the image
        frame = cv2.imread(image_path)

        if frame is None:
            break
        
        # background sub
        fgMask = backSub.apply(frame)
        fgMask = cv2.morphologyEx(fgMask, cv2.MORPH_OPEN, kernel)

        # Apply the background subtractor
        edges = cv2.Canny(fgMask,10,150,apertureSize = 3)
        contours, _ = cv2.findContours(edges, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        contours = [cnt for cnt in contours if len(cnt) > 100]
        print(contours)
        for cnt in contours:
            ellipse = cv2.fitEllipse(cnt)
            print(ellipse)
            cv2.ellipse(frame,ellipse,(0,255,0),2)

        # Show the original image and the foreground mask
        cv2.imshow('frame', fgMask)

        keyboard = cv2.waitKey(0)
        if keyboard == ord('q') or keyboard == 27:
            break

    cv2.destroyAllWindows()

if __name__ == '__main__':
    test()
