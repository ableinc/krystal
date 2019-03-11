"""

AUTHOR: GITHUB: ageitgey - creator the face_recognition software used in Krystal

"""

import pickle
import sys
import warnings
from math import sqrt
from os import listdir, environ
from os.path import isdir, join

import face_recognition
from cv2 import *
from face_recognition import face_locations
from face_recognition.cli import image_files_in_folder
from sklearn import neighbors

from root import TRAIN_FACES_DIR, TEST_FACES_DIR

environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
warnings.filterwarnings('ignore', '', category=RuntimeWarning)
warnings.filterwarnings('ignore', '', category=FutureWarning)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}


def train(train_dir, model_save_path="", n_neighbors=None, knn_algo='ball_tree', verbose=False):
    X = []
    y = []
    for class_dir in listdir(train_dir):
        if not isdir(join(train_dir, class_dir)):
            continue
        for img_path in image_files_in_folder(join(train_dir, class_dir)):
            image = face_recognition.load_image_file(img_path)
            faces_bboxes = face_locations(image)
            if len(faces_bboxes) != 1:
                if verbose:
                    print("image {} not fit for training: {}".format(img_path, "didn't find a face" if len(faces_bboxes) < 1 else "found more than one face"))
                continue
            X.append(face_recognition.face_encodings(image, known_face_locations=faces_bboxes)[0])
            y.append(class_dir)

    if n_neighbors is None:
        n_neighbors = int(round(sqrt(len(X))))
        if verbose:
            print("Chose n_neighbors automatically as:", n_neighbors)

    knn_clf = neighbors.KNeighborsClassifier(n_neighbors=n_neighbors, algorithm=knn_algo, weights='distance')
    knn_clf.fit(X, y)

    if model_save_path != "":
        with open(model_save_path, 'wb') as f:
            pickle.dump(knn_clf, f)


if __name__ == "__main__":
    sys.stdout.write('Started Training')
    train(train_dir=TRAIN_FACES_DIR, model_save_path=TEST_FACES_DIR, n_neighbors=3)
    sys.stdout.write('Finished training')


