from os import error
import dlib
import numpy as np
import math
import cv2

detector = dlib.get_frontal_face_detector()

#sp = dlib.shape_predictor("/usr/local/lib/python3.8/dist-packages/dlib/shape_predictor_5_face_landmarks.dat")

#facerec = dlib.face_recognition_model_v1("/usr/local/lib/python3.8/dist-packages/dlib/dlib_face_recognition_resnet_model_v1.dat")
sp = dlib.shape_predictor("/var/www/html/recognition/shape_predictor_5_face_landmarks.dat")
facerec = dlib.face_recognition_model_v1("/var/www/html/recognition/dlib_face_recognition_resnet_model_v1.dat")

def detectImage(image1: str, image2: str):
    #指定された画像取り込む
    #結果
    same = False
    error = False
    #画像アップロード
    img1 = dlib.load_rgb_image(image1)
    img2 = dlib.load_rgb_image(image2)
    

    #画像にいる顔検知
    img1_detection = detector(img1, 1)
    img2_detection = detector(img2, 1)
    try:
        #顔の位置合わせるために検知された5つの顔のランドマーク定義(左目2点、右目用2点、鼻に1点)
        img1_shape = sp(img1, img1_detection[0])
        img2_shape = sp(img2, img2_detection[0])
    except IndexError:
        error = True
        return same, 0,error
    
    #顔の位置合わせて、顔は直立して回転し、150x150ピクセルに拡大縮小される
    img1_aligned = dlib.get_face_chip(img1, img1_shape)
    img2_aligned = dlib.get_face_chip(img2, img2_shape)

    

    img1_representation = facerec.compute_face_descriptor(img1_aligned)
    img2_representation = facerec.compute_face_descriptor(img2_aligned)


    img1_representation = np.array(img1_representation)
    img2_representation = np.array(img2_representation)

    euclidean_distance = img1_representation - img2_representation
    euclidean_distance = np.sum(np.multiply(euclidean_distance, euclidean_distance))
    euclidean_distance = np.sqrt(euclidean_distance)

    threshold = 0.6 
    
    if euclidean_distance < threshold:
        same = True

    return same, euclidean_distance,error



def face_distance_to_conf(face_distance, face_match_threshold=0.6):
    if face_distance > face_match_threshold:
        range = (1.0 - face_match_threshold)
        linear_val = (1.0 - face_distance) / (range * 2.0)
        return linear_val
    else:
        range = face_match_threshold
        linear_val = 1.0 - (face_distance / (range * 2.0))
        return linear_val + ((1.0 - linear_val) * math.pow((linear_val - 0.5) * 2, 0.2))
