# PyTorch 공식 이미지 (CUDA 12.8 + cuDNN 9 지원)
FROM pytorch/pytorch:2.7.1-cuda12.8-cudnn9-runtime

# 작업 디렉토리 설정
WORKDIR /workspace

# 현재 프로젝트 전체 복사
COPY . /workspace

# 필수 패키지 설치
RUN pip install --upgrade pip && pip install -r requirements.txt

# 기본 쉘 실행
CMD ["bash"]

