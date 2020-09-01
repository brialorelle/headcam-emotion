import http.client, urllib.request, urllib.parse, urllib.error, base64
import json
import imageio
import cv2
import os
import time


with open("azureKey.txt", "r") as key_file:
  SUBSCRIPTION_KEY = key_file.read()
SERVER_URL = 'southeastasia.api.cognitive.microsoft.com'


# CHANGE THESE
INPUT_DIR = '.../face_TP_present/'
OUTPUT_DIR = '.../azure_output/'


OUTPUT_FILENAME = '.../azure_output/face_TP_present.csv'


CSV_HEADER = "filename,faceId,gender,age,anger,contempt,disgust,fear,happiness,neutral,sadness,surprise," +\
       "smile,faceRectangleTop,faceRectangleLeft,faceRectangleWidth,faceRectangleHeight," +\
       "pupilLeft.x,pupilLeft.y,pupilRight.x,pupilRight.y,noseTip.x,noseTip.y," +\
       "mouthLeft.x,mouthLeft.y,mouthRight.x,mouthRight.y," +\
       "eyebrowLeftOuter.x,eyebrowLeftOuter.y,eyebrowLeftInner.x,eyebrowLeftInner.y," +\
       "eyeLeftOuter.x,eyeLeftOuter.y,eyeLeftTop.x,eyeLeftTop.y,eyeLeftBottom.x,eyeLeftBottom.y," +\
       "eyeLeftInner.x,eyeLeftInner.y," +\
       "eyebrowRightInner.x,eyebrowRightInner.y,eyebrowRightOuter.x,eyebrowRightOuter.y," +\
       "eyeRightInner.x,eyeRightInner.y," +\
       "eyeRightTop.x,eyeRightTop.y,eyeRightBottom.x,eyeRightBottom.y,eyeRightOuter.x,eyeRightOuter.y," +\
       "noseRootLeft.x,noseRootLeft.y,noseRootRight.x,noseRootRight.y," +\
       "noseLeftAlarTop.x,noseLeftAlarTop.y,noseRightAlarTop.x,noseRightAlarTop.y," +\
       "noseLeftAlarOutTip.x,noseLeftAlarOutTip.y,noseRightAlarOutTip.x,noseRightAlarOutTip.y," +\
       "upperLipTop.x,upperLipTop.y,upperLipBottom.x,upperLipBottom.y," +\
       "underLipTop.x,underLipTop.y,underLipBottom.x,underLipBottom.y" + "\n"

REQUEST_PARAMS = urllib.parse.urlencode({
    # Request parameters
    'returnFaceId': 'true',
    'returnFaceLandmarks': 'true',
    'returnFaceAttributes': 'age,gender,emotion,smile',
    'recognitionModel': 'recognition_01',
    'returnRecognitionModel': 'false',
    'detectionModel': 'detection_01',
})

REQUEST_HEADER = {
    'Content-Type': 'application/octet-stream',
    'Ocp-Apim-Subscription-Key': SUBSCRIPTION_KEY,
}


def doPOST(body_request, headers):
    try:
        print("Sending POST request...")
        conn = http.client.HTTPSConnection(SERVER_URL)
        conn.request("POST", "/face/v1.0/detect?%s" % REQUEST_PARAMS, body_request, headers)
        response = conn.getresponse()
        data = response.read()
        data_dict = json.loads(data)
        if len(data_dict) > 0:
            print("Success, identified ", len(data_dict), " face(s)")
        else:
            print("Did not identify any faces")
        #print("Success; data is: \n", data)
        #print(data)
        conn.close()
    except Exception as e:
        print("[Errno {0}] {1}".format(e.errno, e.strerror))

    return data

def doFaceFromURL(thisURL=None):
    if thisURL is None:
        thisURL = "https://raw.githubusercontent.com/Microsoft/Cognitive-Face-Windows/master/Data/detection1.jpg"

    body_request = json.dumps({
        "url": thisURL
    })

    return doPOST(body_request, REQUEST_HEADER)

def doFaceFromImagePath(imagepath=None):
    if imagepath is None:
        print("No image path given")
        return

    body_request = open(imagepath, 'rb').read()

    return doPOST(body_request, REQUEST_HEADER)

def doFaceFromImage(image=None):
    if image is None:
        print("No image given")
        return

    body_request = image

    return doPOST(body_request, REQUEST_HEADER)


def convert_face_dict_to_csv_string(fd):
    csv_string = fd['faceId'] + "," +\
      fd['faceAttributes']['gender'] + "," + str(fd['faceAttributes']['age']) + "," + \
      str(fd['faceAttributes']['emotion']['anger'])     + "," + str(fd['faceAttributes']['emotion']['contempt']) + "," +\
      str(fd['faceAttributes']['emotion']['disgust'])   + "," + str(fd['faceAttributes']['emotion']['fear'])     + "," +\
      str(fd['faceAttributes']['emotion']['happiness']) + "," + str(fd['faceAttributes']['emotion']['neutral'])  + "," +\
      str(fd['faceAttributes']['emotion']['sadness'])   + "," + str(fd['faceAttributes']['emotion']['surprise']) + "," +\
      str(fd['faceAttributes']['smile'])   + "," +\
      str(fd['faceRectangle']['top']) + "," + str(fd['faceRectangle']['left']) + "," +\
      str(fd['faceRectangle']['width']) + "," + str(fd['faceRectangle']['height']) + "," +\
      str(fd['faceLandmarks']['pupilLeft']['x'])         + ',' + str(fd['faceLandmarks']['pupilLeft']['y']) + ',' +\
      str(fd['faceLandmarks']['pupilRight']['x'])        + ',' + str(fd['faceLandmarks']['pupilRight']['y']) + ',' +\
      str(fd['faceLandmarks']['noseTip']['x'])           + ',' + str(fd['faceLandmarks']['noseTip']['y']) + ',' +\
      str(fd['faceLandmarks']['mouthLeft']['x'])         + ',' + str(fd['faceLandmarks']['mouthLeft']['y']) + ',' +\
      str(fd['faceLandmarks']['mouthRight']['x'])        + ',' + str(fd['faceLandmarks']['mouthRight']['y']) + ',' +\
      str(fd['faceLandmarks']['eyebrowLeftOuter']['x'])  + ',' + str(fd['faceLandmarks']['eyebrowLeftOuter']['y']) + ',' +\
      str(fd['faceLandmarks']['eyebrowLeftInner']['x'])  + ',' + str(fd['faceLandmarks']['eyebrowLeftInner']['y']) + ',' +\
      str(fd['faceLandmarks']['eyeLeftOuter']['x'])      + ',' + str(fd['faceLandmarks']['eyeLeftOuter']['y']) + ',' +\
      str(fd['faceLandmarks']['eyeLeftTop']['x'])        + ',' + str(fd['faceLandmarks']['eyeLeftTop']['y']) + ',' +\
      str(fd['faceLandmarks']['eyeLeftBottom']['x'])     + ',' + str(fd['faceLandmarks']['eyeLeftBottom']['y']) + ',' +\
      str(fd['faceLandmarks']['eyeLeftInner']['x'])      + ',' + str(fd['faceLandmarks']['eyeLeftInner']['y']) + ',' +\
      str(fd['faceLandmarks']['eyebrowRightInner']['x']) + ',' + str(fd['faceLandmarks']['eyebrowRightInner']['y']) + ',' +\
      str(fd['faceLandmarks']['eyebrowRightOuter']['x']) + ',' + str(fd['faceLandmarks']['eyebrowRightOuter']['y']) + ',' +\
      str(fd['faceLandmarks']['eyeRightInner']['x'])     + ',' + str(fd['faceLandmarks']['eyeRightInner']['y']) + ',' +\
      str(fd['faceLandmarks']['eyeRightTop']['x'])       + ',' + str(fd['faceLandmarks']['eyeRightTop']['y']) + ',' +\
      str(fd['faceLandmarks']['eyeRightBottom']['x'])    + ',' + str(fd['faceLandmarks']['eyeRightBottom']['y']) + ',' +\
      str(fd['faceLandmarks']['eyeRightOuter']['x'])     + ',' + str(fd['faceLandmarks']['eyeRightOuter']['y']) + ',' +\
      str(fd['faceLandmarks']['noseRootLeft']['x'])      + ',' + str(fd['faceLandmarks']['noseRootLeft']['y']) + ',' +\
      str(fd['faceLandmarks']['noseRootRight']['x'])     + ',' + str(fd['faceLandmarks']['noseRootRight']['y']) + ',' +\
      str(fd['faceLandmarks']['noseLeftAlarTop']['x'])   + ',' + str(fd['faceLandmarks']['noseLeftAlarTop']['y']) + ',' +\
      str(fd['faceLandmarks']['noseRightAlarTop']['x'])  + ',' + str(fd['faceLandmarks']['noseRightAlarTop']['y']) + ',' +\
      str(fd['faceLandmarks']['noseLeftAlarOutTip']['x']) + ',' + str(fd['faceLandmarks']['noseLeftAlarOutTip']['y']) + ',' +\
      str(fd['faceLandmarks']['noseRightAlarOutTip']['x']) + ',' + str(fd['faceLandmarks']['noseRightAlarOutTip']['y']) + ',' +\
      str(fd['faceLandmarks']['upperLipTop']['x'])         + ',' + str(fd['faceLandmarks']['upperLipTop']['y']) + ',' +\
      str(fd['faceLandmarks']['upperLipBottom']['x'])      + ',' + str(fd['faceLandmarks']['upperLipBottom']['y']) + ',' +\
      str(fd['faceLandmarks']['underLipTop']['x'])         + ',' + str(fd['faceLandmarks']['underLipTop']['y']) + ',' +\
      str(fd['faceLandmarks']['underLipBottom']['x'])      + ',' + str(fd['faceLandmarks']['underLipBottom']['y'])
    return csv_string



# def process_video(video_filename, output_filename):
#     #csv = CSV_HEADER
#     output_filename_writer=open(output_filename,'a')
#     output_filename_writer.write(CSV_HEADER)

#     vid = imageio.get_reader(video_filename,  'ffmpeg')
#     for num, image in enumerate(vid.iter_data()):
#         timestamp = float(num)/ vid.get_meta_data()['fps'] # @ 25 fps
#         #if (num >= 125) & (num % 5 == 0):
#         #if (num % 50 == 0):
#         if (num % 1 == 0):
#         #if (num >= 75) & (num % 1 == 0):
#             is_success, im_buf_arr = cv2.imencode(".png", image)
#             byte_im = im_buf_arr.tobytes()
#             print("num, timestamp:", num, timestamp)
#             # time.sleep(1)
#             try:
#                 returned_data_json = doFaceFromImage(byte_im)
#                 #print(returned_data_json)
#                 returned_data_dict = json.loads(returned_data_json)
#                 for thisFace in returned_data_dict:
#                     #csv = csv + str(timestamp) + "," + convert_face_dict_to_csv_string(thisFace) + "\n"
#                     csv = str(timestamp) + "," + convert_face_dict_to_csv_string(thisFace) + "\n"
#                     output_filename_writer.write(csv)
#                 if len(returned_data_dict)==0:
#                     csv = str(timestamp) + ",NA" + ','*69 + "\n"
#                     output_filename_writer.write(csv)
#             except RuntimeError:
#                 print('something went wrong')

#     output_filename_writer.close()




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
        returned_data_json = doFaceFromImage(byte_im)
        #print(returned_data_json)
        returned_data_dict = json.loads(returned_data_json)
        for thisFace in returned_data_dict:
            csv = os.path.basename(image_filename) + "," + convert_face_dict_to_csv_string(thisFace) + "\n"
            output_filename_writer.write(csv)
        if len(returned_data_dict)==0:
            csv = os.path.basename(image_filename) + ",NA" + ','*69 + "\n"
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
        time.sleep(4)



if __name__ == "__main__":
    main()





