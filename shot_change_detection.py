
from imutils import face_utils
import numpy as np
import imutils
import cv2
import os
import sys


def convert_to_frames(video_url):
    # To convert the input video to frames
    frames_url= 'frames'
    cmd='ffmpeg -i '+ video_url+' -r 20 '+frames_url+'/frame%3d.png'
    os.system(cmd)
    return frames_url

def list_the_frames(frames_url):
    #List all the frame images from the directory and store it in files and sort them.
    files = os.listdir(frames_url)
    files.sort()
    print(files)
    return files

def detect_shot_change(files):

    #define the width of the desired frames
    width= 500

    #initialize a matrix 
    stacked_matrix= np.zeros((len(files)-1, width), dtype = np.uint8)
    # temp_list= np.zeros(len(files)-1)
    # define the width of the final image
    columns= width
    sample= cv2.imread('frames/'+files[0], 0)
    print(sample)
    sample= imutils.resize(sample, width)
    
    # sample= imutils.resize(cv2.imread('frames/'+files[0], 0), width= 500)
    rows= sample.shape[0]

    # Read all the images from the files
    for k in range (len(files)-1):
        print('processing image {} of {}'.format(k, len(files)))
        # Read the images from the files and resize it
        image1 =cv2.imread('frames/'+files[k], 0)
        image1 = imutils.resize(image1, width=500)
        image2 =cv2.imread('frames/'+files[k+1], 0)
        image2 = imutils.resize(image2, width=500)
        
        #initialize a subtracted matrix
        subtracted_matrix= np.zeros((rows,columns), dtype = np.uint8)
        lLimit= 5 
        rLimit= 20
        for i in range(rows):
            for j in range(columns):
                percenteageDiff= (abs(int(image2[i,j])-int(image1[i,j]))/255)*100
                if percenteageDiff<lLimit:
                    subtracted_matrix[i,j]=0
                elif percenteageDiff>rLimit:
                    subtracted_matrix[i,j]=255 
                else:
                 subtracted_matrix[i,j]= image2[i,j]- image1[i,j]

        cv2.imwrite('difference_images/difference_image{}.png'.format(k), subtracted_matrix)
        stacked_matrix[k] = np.sum(subtracted_matrix, axis=0)/rows


    temp_list= np.sum(stacked_matrix, axis=1)/columns
    print(np.max(temp_list))
    print(temp_list)
    print(np.sort(temp_list))

    for i in range(len(temp_list)-1):
        diff=(abs(int(temp_list[i+1])- int(temp_list[i]))/255)*100
        if diff>45: 
            # print(i)
            cv2.imread(files[i+1])
            preShotChange =cv2.imread('frames/'+files[i+1], 1)
            cv2.imwrite('shots/'+files[i+1], preShotChange)

    cv2.imshow("output", stacked_matrix)
    cv2.waitKey(0)

if __name__ == '__main__':
    if len(sys.argv)< 2:
        print('USAGE...  SOMETHING')
    video_url= sys.argv[1]
    # frames_url= convert_to_frames(video_url)
    files= list_the_frames('frames')
    detect_shot_change(files)
    