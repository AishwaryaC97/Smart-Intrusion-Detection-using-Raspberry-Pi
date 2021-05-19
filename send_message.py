import requests
from gpiozero import MotionSensor
from picamera import PiCamera 
from signal import pause 
import boto3
import io
from PIL import Image, ImageDraw, ExifTags, ImageColor, ImageFont
from botocore.exceptions import ClientError
import logging
import datetime from date

def display_image(bucket,photo,response):
    # Load image from S3 bucket
    s3_connection = boto3.resource('s3')

    s3_object = s3_connection.Object(bucket,photo)
    s3_response = s3_object.get()

    stream = io.BytesIO(s3_response['Body'].read())
    image=Image.open(stream)

    # Ready image to draw bounding boxes on it.
    imgWidth, imgHeight = image.size
    draw = ImageDraw.Draw(image)

    # calculate and display bounding boxes for each detected custom label
    print('Detected custom labels for ' + photo)
    for customLabel in response['CustomLabels']:
        print('Label ' + str(customLabel['Name']))
        print('Confidence ' + str(customLabel['Confidence']))
        if 'Geometry' in customLabel:
            box = customLabel['Geometry']['BoundingBox']
            left = imgWidth * box['Left']
            top = imgHeight * box['Top']
            width = imgWidth * box['Width']
            height = imgHeight * box['Height']

            fnt = ImageFont.truetype('/Library/Fonts/Arial.ttf', 50)
            draw.text((left,top), customLabel['Name'], fill='#00d400', font=fnt)

            print('Left: ' + '{0:.0f}'.format(left))
            print('Top: ' + '{0:.0f}'.format(top))
            print('Label Width: ' + "{0:.0f}".format(width))
            print('Label Height: ' + "{0:.0f}".format(height))

            points = (
                (left,top),
                (left + width, top),
                (left + width, top + height),
                (left , top + height),
                (left, top))
            draw.line(points, fill='#00d400', width=5)

    image.show()

def send_alert(imagelink):

       
    url = 'https://maker.ifttt.com/trigger/trigger/with/key/ilSs5GtSYH4Omfj7jBuUD7_G9k6asBWfilSvnMVW3sA'
    obj = {'value1' :imagelink.url}
       
    r = requests.post(url, data=obj)
    if r.status_code == 200:
        print('Alert Sent')
    else:
        print('Error')

def upload_image(bucket):

	date = datetime.now().strftime("%Y_%m_%d-%I:%M:%S_%p")
	#todaydate = date.today
	#print(f"filename_{date}") 
	imagename = "image_" + str(date) + ".jpg"
    camera.capture(imagename) 
    
    file_name = '/Users/nikhilvijayakumar/Desktop/Images/' + str(imagename)

    s3_client = boto3.client('s3')
    
    imagelink = 'https://testimagebucket123.s3.amazonaws.com/' + str(imagename)
    try:
        response = s3_client.upload_file(file_name, bucket, imagename)
    except ClientError as e:
        logging.error(e)
        return False
    return True, imagelink

def correctgesture(response, bucket, object, imagelink):

    for customLabel in response['CustomLabels']:
        if customLabel['Name'] == 'V hand gesture' and customLabel['Confidence'] > 90:
            #print("This is the correct gesture")
            send_alert(imagelink)
            
            


def show_custom_labels(model,bucket,min_confidence):
    client=boto3.client('rekognition')

	response, imagelink = upload_image(bucket):

    #Call DetectCustomLabels
    response = client.detect_custom_labels(Image={'S3Object': {'Bucket': bucket, 'Name': photo}},
        MinConfidence=min_confidence,
        ProjectVersionArn=model)

    # For object detection use case, uncomment below code to display image.
    #display_image(bucket,photo,response)

    correctgesture(response, bucket, photo, imagelink)

    print(response)

    return len(response['CustomLabels'])

   

def send_alert(imagelink):

       
    url = 'https://maker.ifttt.com/trigger/trigger/with/key/ilSs5GtSYH4Omfj7jBuUD7_G9k6asBWfilSvnMVW3sA'
    obj = {'value1' :imagelink.url}
       
    r = requests.post(url, data=obj)
    if r.status_code == 200:
        print('Alert Sent')
    else:
        print('Error')
        
def main():
	
	camera = PiCamera() 
	camera.resolution = (1920, 1080)

    bucket='testimagebucket123'
    #photo='test1.jpg'
    model='arn:aws:rekognition:us-east-1:503117904809:project/customlabeltest/version/customlabeltest.2021-05-09T15.02.37/1620590557459'
    min_confidence=90

    label_count=show_custom_labels(model,bucket,min_confidence)
    print("Custom labels detected: " + str(label_count))
    
    pir = MotionSensor(4)
	if pir.when_motion():
		label_count=show_custom_labels(model,bucket,min_confidence)
	


if __name__ == "__main__":
    main()