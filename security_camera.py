import cv2
import numpy as np
from imutils.video import VideoStream
import argparse
import imutils
import time
import cv2
from datetime import datetime
import os
import bot
import threading
import secrets

MIN_AREA = 4000

# opencv code from: https://www.pyimagesearch.com/2015/05/25/basic-motion-detection-and-tracking-with-python-and-opencv/

SECONDS_TO_CLEAR_COUNTER = 5
SECONDS_TO_EMAIL_AFTER_ARRIVAL = 10
SECONDS_TO_RESET_BACKGROUND = 2
SAVING_VISITOR_IMAGES = True
EMAIL_ENABLED = True
SECONDS_TO_SAVE_VISITOR_IMAGES = 1
DISPLAY = False

LINK = secrets.LINK_WITHOUT_PASSWORD

frame = None

def main():
    global frame
    print('Starting security camera')
    visitedCount = 0
    lastTimeVisitedCountCleared = datetime.now()
    visitorFirstArrived = None
    visitorMostRecentlySeen = None
    lastTimeBackgroundReset = datetime.now()
    savingVisitorImage = datetime.now()


    vs = cv2.VideoCapture(secrets.LINK_WITH_PASSWORD)
    if vs is None or not vs.isOpened():
        print('Unable to open security camera', vs)
        exit()


    backGround = None
    emailedAboutVisitor = False

    while(True):

        if visitedCount > 0 and (datetime.now() - lastTimeVisitedCountCleared).seconds > SECONDS_TO_CLEAR_COUNTER:
            print("Lost visitor, resetting counter...")
            lastTimeVisitedCountCleared = datetime.now()
            visitedCount = 0
            visitorFirstArrived = None
            visitorMostRecentlySeen = None
            emailedAboutVisitor = False


        text = "No one's here :("
        ret, frame = vs.read()
        frame = cv2.resize(frame,None,fx=.4,fy=.4)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (21, 21), 0)

        if backGround is None or (datetime.now() - lastTimeBackgroundReset).seconds >= SECONDS_TO_RESET_BACKGROUND:
            backGround = gray
            lastTimeBackgroundReset = datetime.now()
            continue

        frameDelta = cv2.absdiff(backGround, gray)
        thresh = cv2.threshold(frameDelta, 25, 255, cv2.THRESH_BINARY)[1]
        thresh = cv2.dilate(thresh, None, iterations=2)
        cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL,
            cv2.CHAIN_APPROX_SIMPLE)
        cnts = imutils.grab_contours(cnts)

        height, width, _ = frame.shape

        foundVisitor = False
        for c in cnts:
            # if the contour is too small, ignore it
            if cv2.contourArea(c) < MIN_AREA:
                continue

            foundVisitor = True

            # compute the bounding box for the contour, draw it on the frame,
            # and update the text
            (x, y, w, h) = cv2.boundingRect(c)
            #cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 1)
            text = "There's a Visitor! :)"
            
        cv2.putText(frame, "Room Status: {}".format(text), (10, 20),
            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
        
        if foundVisitor:
            lastTimeVisitedCountCleared = datetime.now()
            visitedCount += 1
            if visitorFirstArrived == None:
                print("Visitor first arrived now")
                visitorFirstArrived = datetime.now()
            else:
                visitorMostRecentlySeen = datetime.now()
            
            if SAVING_VISITOR_IMAGES and (datetime.now() - savingVisitorImage).seconds >= SECONDS_TO_SAVE_VISITOR_IMAGES:
                now = datetime.now()
                savingVisitorImage = now
                folder = str(now.month) + '-' + str(now.day) + '-' + str(now.year)
                if not os.path.isdir(folder):
                    os.mkdir(folder)
                fileName = str(now)
                mostRecentFile = folder + '/' + fileName + '.jpg'
                cv2.imwrite(mostRecentFile, frame)

        if EMAIL_ENABLED and visitorFirstArrived != None and visitorMostRecentlySeen != None:
            diff = (visitorMostRecentlySeen - visitorFirstArrived).seconds
            if diff >= SECONDS_TO_EMAIL_AFTER_ARRIVAL and (not emailedAboutVisitor):
                emailedAboutVisitor = True
                print("Notifying now")

                msg = 'There\'s an animal at the door!\n'

                if bot.ready:
                    bot.send("There\'s an animal at the door!")
                    bot.sendFile(getMostRecentFile())

        if DISPLAY:
            cv2.imshow("Security Feed", frame)
            #cv2.imshow("Background", backGround)
            #cv2.imshow("Thresh", thresh)
            #cv2.imshow("Frame Delta", frameDelta)

            #cv2.imshow('frame',gray)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    vs.release()
    cv2.destroyAllWindows()
    exit()

def getMostRecentFile():
    paths = []
    for path in os.listdir():
        if os.path.isdir(path) and path.count('-') == 2:
            paths.append(path)
        print('Path is ', paths)
    paths = sorted(paths, key=compare)
    fileNames = []
    if len(paths) > 0:
        folder = paths[0]
        for filePath in os.listdir(folder):
            fileNames.append(datetime.strptime(filePath.replace('.jpg', ''), '%Y-%m-%d %H:%M:%S.%f'))
        if len(fileNames) > 0:
            fileNames = sorted(fileNames)
            return folder + '/' + str(fileNames[len(fileNames) - 1]) + '.jpg'
        return None
    else:
        return None

def getNow():
    cv2.imwrite('now.jpg', frame)
    return 'now.jpg'

def compare(dir1):
    month1, day1, year1 = dir1.split('-')
    return year1 + month1 + day1
    
threading.Thread(target=main).start()