이 폴더는 AI Hub에서 제공된 얼굴 이미지 데이터를 저장하는 용도입니다.  
데이터를 사용하려면 AI Hub에서 직접 다운로드해 `data/raw/` 디렉토리에 넣어야 합니다.  

# 구조

- T_image_data
- V_image_data

# 데이터 선정

데이터의 전체 구조는 [AI HUB - 가족 관계가 알려진 얼굴 이미지 데이터](https://www.aihub.or.kr/aihubdata/data/view.do?currMenu=115&topMenu=100&dataSetSn=528)를 참고하세요.

## 원천(이미지) 데이터

- 가족사진 6,900 장
- **각도 별 개인 사진** 49,800 장
- 기간별 나이 사진 24,000 장

각도 별 개인 사진 중 `CAM` 이 포함된 이미지와 정면(0)을 제외한 45도 90도 사진을 제외했습니다.  

# 데이터 전처리
전처리 이후 training 과 validation 으로 나누지 않고, 한 폴더에서 train/val/test를 나눴습니다.