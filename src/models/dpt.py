import torch
from midas.dpt_depth import DPTDepthModel
from torchvision.transforms import Compose
import numpy as np
import cv2
from PIL import Image, UnidentifiedImageError
from io import BytesIO

# Load the MiDaS model architecture
model_path = "./models/pretrained/dpt_large_384.pt"
midas = DPTDepthModel(
    path=model_path,
    backbone="vitl16_384",
    non_negative=True,
)

# Use GPU if available
device = torch.device("cuda") if torch.cuda.is_available() else torch.device("cpu")
midas.to(device)
midas.eval()

print(device)

# Use transforms to resize and normalize the image
midas_transforms = torch.hub.load("intel-isl/MiDaS", "transforms")
transform = midas_transforms.dpt_transform

def process_depth_image(img):
    # Transform input for midas
    imgbatch = transform(img).to(device)

    # Make a prediction
    with torch.no_grad():
        prediction = midas(imgbatch)
        prediction = torch.nn.functional.interpolate(
            prediction.unsqueeze(1),
            size=img.shape[:2],
            mode="bicubic",
            align_corners=False,
        ).squeeze()

        output = prediction.cpu().numpy()

    # Normalize the output for visualization
    output = cv2.normalize(output, None, 0, 255, cv2.NORM_MINMAX, cv2.CV_8U)

    return output
