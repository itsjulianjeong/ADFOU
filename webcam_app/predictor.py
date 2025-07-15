# 모델 로드 + 얼굴 탐지 + 예측

# 라이브러리 및 CUDA 세팅 ===============================================================
import os
import numpy as np
import cv2
import mediapipe as mp
import torch
import torchvision.models as models
import torch.nn as nn
from webcam_app.utils.image_utils import preprocess_face_rgb, draw_prediction

# CDUA
device=torch.device("cuda" if torch.cuda.is_available() else "cpu")


# 모델 부분 ============================================================================
# EfficientNetB0 기반 모델 정의
class EfficientNetB0MultiLabel(nn.Module):
    def __init__(self, num_classes):
        super(EfficientNetB0MultiLabel, self).__init__()
        self.base_model=models.efficientnet_b0(pretrained=True)
        in_features=self.base_model.classifier[1].in_features
        self.base_model.classifier[1]=nn.Linear(in_features, num_classes)

    def forward(self, x):
        return self.base_model(x)

# 클래스
LABEL_COLS=["male","female","0s","10s","20s","30s","40s","50s","60+"]

# 모델 로딩
model=EfficientNetB0MultiLabel(num_classes=len(LABEL_COLS)).to(device)

BASE_DIR=os.path.dirname(os.path.abspath(__file__))  # webcam_app/
model_path=os.path.join(BASE_DIR, "..", "src", "models", "09_efficientnetb0_best.pth")
model_path=os.path.normpath(model_path)
# map_location: 모델 로딩 시 저장된 장치(GPU/CPU)와 무관하게 현재 사용 중인 장치로 매핑
# 이걸 설정해주면, GPU에서 저장한 모델을 CPU에서 불러올 때 오류 안나게 해줌
model.load_state_dict(torch.load(model_path, map_location=device))
model.eval()


# 얼굴 탐지 ============================================================================
# MediaPipe Face Detection 사용
mp_face_detection=mp.solutions.face_detection

# model_selection=1: 정밀한 얼굴 감지 모델 사용 -> 멀리서 찍힌 얼굴도 잘 인식
# 0: 빠르지만 가까운 얼굴에만 정확
# 1: 느리지만 먼 거리 얼굴도 인식 가능
# min_detection_confidence=0.6: 얼굴로 인식할 최소 신뢰도 -> 0~1 사이 값
# 높을수록 더 확실한 얼굴만 탐지
face_detection=mp_face_detection.FaceDetection(model_selection=1, min_detection_confidence=0.6)

# 얼굴 영역 추출
def detect_faces(image):
    img_rgb=cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    results=face_detection.process(img_rgb)
    
    bboxes=[]
    h, w, _=image.shape

    if results.detections:  
        for detection in results.detections:
            bbox=detection.location_data.relative_bounding_box  # 이미지 너비/높이를 기준으로 비율(0~1)로 제공되므로 -> w, h 곱해서 실제 좌표로 바꿔서 crop
            x=int(bbox.xmin * w)
            y=int(bbox.ymin * h)
            w_box=int(bbox.width * w)
            h_box=int(bbox.height * h)

            # 경계 넘는 부분 처리
            x=max(0, x)
            y=max(0, y)
            bboxes.append((x, y, w_box, h_box))
    
    return bboxes


# 클래스 예측 ==========================================================================
# -> image_utils
def predict_face(image):
    bboxes=detect_faces(image)
    has_face=bool(bboxes)  # 얼굴 탐지 여부

    # 예측값 return용
    predictions=[]

    for box in bboxes:
        x, y, w_box, h_box=box
        face=image[y:y+h_box, x:x+w_box]
        if face.size == 0:
            continue
        
        # 전처리 및 예측
        input_tensor=preprocess_face_rgb(face).to(device)
        with torch.no_grad():
            outputs=model(input_tensor)
            preds=torch.sigmoid(outputs).cpu().numpy()[0]

        # 성별 예측
        sex_preds=preds[:2]
        sex_label=np.argmax(sex_preds)
        sex_text="male" if sex_label==0 else "female"

        # 연령대 예측
        age_preds=preds[2:]
        age_label=np.argmax(age_preds)
        age_text=LABEL_COLS[2:][age_label]

        # 저장
        label_text=f"{'남성' if sex_text == 'male' else '여성'}, {age_text}대"
        predictions.append((sex_text, age_text, label_text))  # 튜플로 저장
        image=draw_prediction(image, box, label_text)

    if predictions:
        sex, age, label=predictions[0]
        return image, sex, age, label, has_face
    else:
        return image, "Unknown", "Unknown", "Unknown", False
