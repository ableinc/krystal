import pickle
from os.path import isfile, splitext

import face_recognition
from cv2 import *
from face_recognition import face_locations

from uni import TEST_FACES_DIR, TRAIN_FACES_DIR

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
unknown = 'Im not sure'


def predict(X_img_path, knn_clf=None, model_save_path=TRAIN_FACES_DIR, DIST_THRESH=.5):

    if not isfile(X_img_path) or splitext(X_img_path)[1][1:] not in ALLOWED_EXTENSIONS:
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
    cam = VideoCapture(0)  # 0 -> index of camera
    s, img = cam.read()
    if s:  # frame captured without any errors
        namedWindow("Snapshot", WINDOW_NORMAL)
        resizeWindow("Snapshot", 300, 300)
        destroyWindow("Snapshot")
        imwrite(TEST_FACES_DIR + "/{}.jpg".format(name.title()), img)  # save image


