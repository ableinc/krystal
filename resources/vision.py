import os.path
import pickle
import time
import warnings
from os import environ

import cv2
import face_recognition
import imutils
import numpy as np
from face_recognition import face_locations
from imutils.video import FPS
from imutils.video import VideoStream

from root import DET_MODEL, DET_PROTOTXT
from root import TEST_FACES_DIR, TRAIN_FACES_DIR

environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
warnings.filterwarnings('ignore', '', category=RuntimeWarning)
warnings.filterwarnings('ignore', '', category=FutureWarning)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
unknown = 'Im not sure'


def Detection():
    # initialize the list of class labels MobileNet SSD was trained to
    # detect, then generate a set of bounding box colors for each class
    CLASSES = ["background", "aeroplane", "bicycle", "bird", "boat",
               "bottle", "bus", "car", "cat", "chair", "cow", "diningtable",
               "dog", "horse", "motorbike", "person", "pottedplant", "sheep",
               "sofa", "train", "tvmonitor"]
    COLORS = np.random.uniform(0, 255, size=(len(CLASSES), 3))

    # load our serialized models from disk
    net = cv2.dnn.readNetFromCaffe(DET_PROTOTXT, DET_MODEL)

    # initialize the video stream, allow the cammera sensor to warmup,
    # and initialize the FPS counter

    vs = VideoStream(src=0).start()
    time.sleep(2.0)
    fps = FPS().start()

    # loop over the frames from the video stream
    while True:
        # grab the frame from the threaded video stream and resize it
        # to have a maximum width of 400 pixels
        frame = vs.read()
        frame = imutils.resize(frame, width=400)

        # grab the frame dimensions and convert it to a blob
        (h, w) = frame.shape[:2]
        blob = cv2.dnn.blobFromImage(cv2.resize(frame, (600, 600)),
                                     0.007843, (300, 300), 127.5)

        # pass the blob through the network and obtain the detections and
        # predictions
        net.setInput(blob)
        detections = net.forward()

        # loop over the detections
        for i in np.arange(0, detections.shape[2]):
            # extract the confidence (i.e., probability) associated with
            # the prediction
            confidence = detections[0, 0, i, 2]

            # filter out weak detections by ensuring the `confidence` is
            # greater than the minimum confidence
            if confidence > 0.2:
                # extract the index of the class label from the
                # `detections`, then compute the (x, y)-coordinates of
                # the bounding box for the object
                idx = int(detections[0, 0, i, 1])
                box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
                (startX, startY, endX, endY) = box.astype("int")
                calc = confidence * 100

                if calc > 99.0:
                    return ''.join(CLASSES[idx])


def predict(X_img_path, knn_clf=None, model_save_path=TRAIN_FACES_DIR, DIST_THRESH=.5):

    if not os.path.isfile(X_img_path) or os.path.splitext(X_img_path)[1][1:] not in ALLOWED_EXTENSIONS:
        raise Exception("invalid image path: {}".format(X_img_path))

    if knn_clf is None and model_save_path == "":
        raise Exception("must supply knn classifier either thourgh knn_clf or model_save_path")

    if knn_clf is None:
        with open(model_save_path, 'rb') as f:
            knn_clf = pickle.load(f)

    X_img = face_recognition.load_image_file(X_img_path)
    X_faces_loc = face_locations(X_img)
    if len(X_faces_loc) == 0:
        return []

    faces_encodings = face_recognition.face_encodings(X_img, known_face_locations=X_faces_loc)

    closest_distances = knn_clf.kneighbors(faces_encodings, n_neighbors=3)

    is_recognized = [closest_distances[0][i][0] <= DIST_THRESH for i in range(len(X_faces_loc))]
    # predict classes and cull classifications that are not with high confidence
    # return [(pred, loc) if rec else ("N/A", loc) for pred, loc, rec in
            # zip(knn_clf.predict(faces_encodings), X_faces_loc, is_recognized)]
    final = ''.join([pred if rec else unknown for pred, rec in zip(knn_clf.predict(faces_encodings), is_recognized)])
    return final


def snapshot():
    print('Taking a look at you.')
    name = 'snapshot'
    cam = cv2.VideoCapture(0)  # 0 -> index of camera
    s, img = cam.read()
    if s:  # frame captured without any errors
        cv2.namedWindow("Snapshot", cv2.WINDOW_NORMAL)
        cv2.resizeWindow("Snapshot", 300, 300)
        cv2.destroyWindow("Snapshot")
        cv2.imwrite(TEST_FACES_DIR + "/{}.jpg".format(name.title()), img)  # save image


def signInWithFace():
    print('Please look at the camera. Adjust for great lighting')
    cam = cv2.VideoCapture(0)
    seconds = time.strftime("%S")
    while cam.isOpened():
        frame, img = cam.read()
        if frame:
            return 'Feature coming soon'
