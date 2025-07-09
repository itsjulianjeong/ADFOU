import cv2
import numpy as np
import torch
from torchvision import transforms
from PIL import ImageFont, ImageDraw, Image
import matplotlib.font_manager as fm

# EfficientNetB0에 맞춘 전처리용 transform
# RGB, 224x224, 정규화
image_transform=transforms.Compose([
    transforms.ToPILImage(),
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406],
                        std=[0.229, 0.224, 0.225])
])

# 얼굴 이미지 RGB
# -> 모델 입력 가능하도록 resize, 텐서 변환, 정규화, 배치 차원 추가
def preprocess_face_rgb(face_img):
    tensor=image_transform(face_img)
    tensor=tensor.unsqueeze(0)  # (1, 3, 224, 224)
    return tensor

# 역정규화 -> 정규화 진행한거 되돌리기
def unnormalize(img_tensor):
    mean=np.array([0.485, 0.456, 0.406])
    std=np.array([0.229, 0.224, 0.225])

    img=img_tensor.squeeze().permute(1, 2, 0).cpu().numpy()
    img=std * img + mean
    img=np.clip(img, 0, 1)
    return img

font_path="C:/Windows/Fonts/malgun.ttf"
font=ImageFont.truetype(font_path, 20)

# 예측 결과 bbox + text
def draw_prediction(image, box, label_text):
    x, y, w, h=box
    img_pil=Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
    draw=ImageDraw.Draw(img_pil)
    # 텍스트 작성
    draw.text((x, y-25), label_text, font=font, fill=(0, 255, 0))
    image=cv2.cvtColor(np.array(img_pil), cv2.COLOR_RGB2BGR)
    cv2.rectangle(image, (x, y), (x+w, y+h), (0, 255, 0), 2)

    return image