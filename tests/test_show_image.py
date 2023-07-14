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

    ind = 0
    N = len(image_paths)
    while ind < N:
        # Read the image
        frame = cv2.imread(image_paths[ind])

        if frame is None:
            break

        # Show the original image and the foreground mask
        cv2.imshow('FG Mask', frame)
            
        keyboard = cv2.waitKey(0)
        if keyboard == ord('q') or keyboard == 27:
            break
        if keyboard == 97:
            ind -=1
        elif keyboard == 100:
            ind +=1
        print(keyboard)

        
    cv2.destroyAllWindows()

if __name__ == '__main__':
    test()