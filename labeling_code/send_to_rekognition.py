# import http.client, urllib.request, urllib.parse, urllib.error, base64
# import json
# import imageio
# import cv2
# import os
# import time

import boto3
import json
import os
import time


# CHANGE THESE
INPUT_DIR = '.../face_TP_present/'
OUTPUT_DIR = '.../rekognition_output/'


OUTPUT_FILENAME = '.../rekognition_output/face_TP_present.csv'


LM_NAMES = ['eyeLeft', 'eyeRight', 'mouthLeft', 'mouthRight', 'nose', 
'leftEyeBrowLeft', 'leftEyeBrowRight', 'leftEyeBrowUp', 
'rightEyeBrowLeft', 'rightEyeBrowRight', 'rightEyeBrowUp', 
'leftEyeLeft', 'leftEyeRight', 'leftEyeUp', 'leftEyeDown', 
'rightEyeLeft', 'rightEyeRight', 'rightEyeUp', 'rightEyeDown', 
'noseLeft', 'noseRight', 'mouthUp', 'mouthDown', 
'leftPupil', 'rightPupil', 'upperJawlineLeft', 'midJawlineLeft', 
'chinBottom', 'midJawlineRight', 'upperJawlineRight']


CSV_HEADER = "time,gender,genderConfidence," +\
       "ageRangeLower,ageRangeUpper," +\
       "angry,calm,confused,disgusted,fear,happy,sad,surprised," +\
       "smile,smileConfidence," +\
       "eyesOpen,eyesOpenConfidence," +\
       "mouthOpen,mouthOpenConfidence," +\
       "eyeglasses,eyeglassesConfidence," +\
       "sunglasses,sunglassesConfidence," +\
       "beard,beardConfidence," +\
       "mustache,mustacheConfidence," +\
       "boundingBoxWidth,boundingBoxHeight,boundingBoxLeft,boundingBoxTop," +\
       "poseRoll,poseYaw,posePitch," +\
       "qualityBrightness,qualitySharpness,"
      
lm_header_string = ""
for lm_name in LM_NAMES:
    lm_header_string = lm_header_string + lm_name + ".x," + lm_name + ".y,"
       
CSV_HEADER = CSV_HEADER + lm_header_string + "overallConfidence" + "\n"



def detect_faces_local_file(image_filename):
    client=boto3.client('rekognition')
   
    with open(image_filename, 'rb') as image:
        response = client.detect_faces(Image={'Bytes': image.read()}, Attributes=['ALL'])
      
    print("Success")
    return response


def convert_face_dict_to_csv_string(fd):
  emos = fd['Emotions']
  emoString = str([thisE['Confidence'] for thisE in emos if thisE['Type'] == 'ANGRY'][0]) + "," +\
              str([thisE['Confidence'] for thisE in emos if thisE['Type'] == 'CALM'][0]) + "," +\
              str([thisE['Confidence'] for thisE in emos if thisE['Type'] == 'CONFUSED'][0]) + "," +\
              str([thisE['Confidence'] for thisE in emos if thisE['Type'] == 'DISGUSTED'][0]) + "," +\
              str([thisE['Confidence'] for thisE in emos if thisE['Type'] == 'FEAR'][0]) + "," +\
              str([thisE['Confidence'] for thisE in emos if thisE['Type'] == 'HAPPY'][0]) + "," +\
              str([thisE['Confidence'] for thisE in emos if thisE['Type'] == 'SAD'][0]) + "," +\
              str([thisE['Confidence'] for thisE in emos if thisE['Type'] == 'SURPRISED'][0]) + ","
  lms = fd['Landmarks']
  lmString = ""
  for lm_name in LM_NAMES:
    lmString = lmString + str([thisL['X'] for thisL in lms if thisL['Type'] == lm_name][0]) + "," +\
                          str([thisL['Y'] for thisL in lms if thisL['Type'] == lm_name][0]) + ","

  csv_string =  str(fd['Gender']['Value']) + "," + str(fd['Gender']['Confidence']) + "," +\
                str(fd['AgeRange']['Low']) + "," + str(fd['AgeRange']['High']) + "," +\
                emoString +\
                str(fd['Smile']['Value']) + ","       + str(fd['Smile']['Confidence']) + "," +\
                str(fd['EyesOpen']['Value']) + ","    + str(fd['EyesOpen']['Confidence']) + "," +\
                str(fd['MouthOpen']['Value']) + ","   + str(fd['MouthOpen']['Confidence']) + "," +\
                str(fd['Eyeglasses']['Value']) + ","  + str(fd['Eyeglasses']['Confidence']) + "," +\
                str(fd['Sunglasses']['Value']) + ","  + str(fd['Sunglasses']['Confidence']) + "," +\
                str(fd['Beard']['Value']) + ","       + str(fd['Beard']['Confidence']) + "," +\
                str(fd['Mustache']['Value']) + ","    + str(fd['Mustache']['Confidence']) + "," +\
                str(fd['BoundingBox']['Width']) + "," + str(fd['BoundingBox']['Height']) + "," +\
                str(fd['BoundingBox']['Left']) + ","  + str(fd['BoundingBox']['Top']) + "," +\
                str(fd['Pose']['Roll']) + "," + str(fd['Pose']['Yaw']) + "," + str(fd['Pose']['Pitch']) + "," +\
                str(fd['Quality']['Brightness']) + "," + str(fd['Quality']['Sharpness']) + "," +\
                lmString + str(fd['Confidence'])
  return csv_string




def make_header_filename(output_filename):
    output_filename_writer=open(output_filename,'a')
    output_filename_writer.write(CSV_HEADER)
    output_filename_writer.close()


def process_and_append_results_to_output(image_filename, output_filename):
    output_filename_writer=open(output_filename,'a')
    with open(image_filename, "rb") as image:
        byte_im = image.read()
        #byte_ar = bytearray(byte_im)
    try:
        returned_data_dict = detect_faces_local_file(image_filename)
        
        for thisFace in returned_data_dict['FaceDetails']:
            csv = os.path.basename(image_filename) + "," + convert_face_dict_to_csv_string(thisFace) + "\n"
            output_filename_writer.write(csv)
        if len(returned_data_dict['FaceDetails'])==0:
            csv = os.path.basename(image_filename) + ','*96 + "\n"
            output_filename_writer.write(csv)
    except RuntimeError:
        print('something went wrong')

    output_filename_writer.close()



def main():
    make_header_filename(OUTPUT_FILENAME)
    all_images_list = os.listdir(INPUT_DIR)
    all_images_list.sort()

    for counter in range(0, len(all_images_list)):
        this_filename = all_images_list[counter]
        print("Currently on image number ", counter, " filename: ", this_filename)
        process_and_append_results_to_output(INPUT_DIR + this_filename, OUTPUT_FILENAME)
        #time.sleep(4)

    

if __name__ == "__main__":
    main()



