


FROM nvcr.io/nvidia/pytorch:22.12-py3
RUN rm -rf /opt/pytorch  # remove 1.2GB dir

RUN apt update && apt install --no-install-recommends -y zip htop screen libgl1-mesa-glx
RUN mkdir -p /usr/ect/app/test/
COPY requirements.txt .

RUN python -m pip install --upgrade pip wheel
RUN pip uninstall -y Pillow torchtext torch torchvision
RUN pip install --no-cache -U pycocotools  # install --upgrade
RUN pip install --no-cache -r requirements.txt albumentations comet gsutil notebook 'opencv-python<4.6.0.66'  \
    Pillow>=9.1.0 ultralytics \
    --extra-index-url https://download.pytorch.org/whl/cu113

RUN mkdir -p /usr/src/lable-tool
WORKDIR /usr/src/lable-tool


