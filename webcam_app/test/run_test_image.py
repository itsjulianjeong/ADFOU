import os
import cv2
from webcam_app.predictor import predict_face

# 경로 설정
IMAGE_DIR="webcam_app/test/image"
RESULT_DIR="webcam_app/test/result"
os.makedirs(RESULT_DIR, exist_ok=True)

# 이미지 파일 목록 가져오기 (JPG, PNG 등)
image_files=[f for f in os.listdir(IMAGE_DIR) if f.lower().endswith((".jpg", ".jpeg", ".png"))]

if not image_files:
    print("이미지가 존재하지 않습니다.")
    exit()

for filename in image_files:
    input_path=os.path.join(IMAGE_DIR, filename)
    base_name=os.path.splitext(filename)[0]
    output_img_path=os.path.join(RESULT_DIR, f"{base_name}_result.jpg")
    output_txt_path=os.path.join(RESULT_DIR, f"{base_name}_prediction.txt")
    
    image=cv2.imread(input_path)
    if image is None:
        print(f"이미지 불러오기 실패! {input_path}")
        continue

    # 예측 수행
    result_img, label_texts, has_face=predict_face(image)

    # 예측 이미지 저장
    cv2.imwrite(output_img_path, result_img)
    print(f"예측 결과 이미지 저장 완료! {output_img_path}")

    # 예측 텍스트 저장
    with open(output_txt_path, "w", encoding="utf-8") as f:
        f.write("예측 결과:\n")
        for i, text in enumerate(label_texts, 1):
            f.write(f"{i}. {text}\n")
    print(f"예측 텍스트 저장 완료! {output_txt_path}\n")