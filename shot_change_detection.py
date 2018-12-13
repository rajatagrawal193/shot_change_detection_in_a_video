from imutils import face_utils
import numpy as np
import imutils
import cv2
import os
import sys
import shutil
import timeit
import time

def convert_to_frames(video_url):
    # To convert the input video to frames
    cmd='ffmpeg -i '+ video_url+' -filter:v scale=480:-1 '+frames_url+'/frame%3d.png'
    os.system(cmd)
    return frames_url

def list_the_frames(frames_url):
    #List all the frame images from the directory and store it in files and sort them.
    files = os.listdir(frames_url)
    files= sorted(files, key=lambda x:int(x.split('.')[0][5:]))
    # files.sort()
    print(files)

    return files

def get_subtracted_matrix(image1, image2, rows, columns):
    lLimit= 50 
    rLimit= 50
    subtracted_matrix= np.zeros((rows,columns), dtype = np.uint8)
    subtracted_matrix= abs(image2-image1)
    subtracted_matrix[subtracted_matrix>=rLimit]=255
    subtracted_matrix[subtracted_matrix<=lLimit]=0
    return subtracted_matrix

def read_the_images(files, frames_url):
    images=[]
    files_length=len(files)    
    for i in range(files_length):
        print('processing image {} of {}'.format(i+1, files_length))  

        images.append(cv2.imread(frames_url+'/'+files[i], 0))
    return images
    

def detect_shot_change(files, frames_url, difference_images_url, shots_url,stacked_matrix_url):
    
    width= 480
    stacked_matrix= np.zeros((len(files)-1, width), dtype = np.uint8)
    columns= width
    sample= imutils.resize(cv2.imread(frames_url+'/'+files[0], 0), width)
    rows= sample.shape[0]
    images= read_the_images(files, frames_url)

    files_length=len(images)
    
    for k in range (files_length-1):
        print('processing image {} of {}'.format(k+1, files_length), flush=True)
        subtracted_matrix= get_subtracted_matrix(images[k], images[k+1], rows, columns)
        # cv2.imwrite(difference_images_url+'/difference_image{}.png'.format(k), subtracted_matrix)
        stacked_matrix[k] = np.sum(subtracted_matrix, axis=0)/rows
        cv2.imwrite(stacked_matrix_url+'/stacked_matrix.png', stacked_matrix)
    
    temp_list= np.sum(stacked_matrix, axis=1)/columns
    _max=int(np.max(temp_list))

    for i in range(0, len(temp_list)-1):

        diff=((abs(int(temp_list[i+1])- int(temp_list[i]))/_max))*100
        if diff>70: 
            postShotChange =cv2.imread(frames_url+'/'+files[i+1], 1)
            cv2.imwrite(shots_url+'/'+files[i+1], postShotChange)
            i=i+1

    cv2.imshow("output", stacked_matrix)
    cv2.waitKey(0)



if __name__ == '__main__':
    if len(sys.argv)< 2:
        print('USAGE...  SOMETHING')

    video_url= sys.argv[1]
    if os.path.exists('output'):
        shutil.rmtree('output')
    os.mkdir('output')
    frames_url='output/frames'
    difference_images_url='output/difference_images'
    shots_url='output/shots'
    stacked_matrix_url='output'
    # stacked_matrix_url='output/stack'
    if os.path.exists(frames_url):
        shutil.rmtree(frames_url)
    os.mkdir(frames_url)
    if os.path.exists(difference_images_url):
        shutil.rmtree(difference_images_url)
    os.mkdir(difference_images_url)
    if os.path.exists(shots_url):
        shutil.rmtree(shots_url)
    os.mkdir(shots_url)
   
    frames_url= convert_to_frames(video_url)
    files= list_the_frames(frames_url)
    detect_shot_change(files, frames_url, difference_images_url, shots_url,stacked_matrix_url)
    