import cv2
import torch
import matplotlib.pyplot as plt
from midas.dpt_depth import DPTDepthModel  # Ensure the required model architecture is available
from torchvision.transforms import Compose

# Load the MiDaS model architecture
model_path = "./dpt_large_384.pt"
midas = DPTDepthModel(
    path=model_path,
    backbone="vitl16_384",
    non_negative=True,
)

# Use GPU if available
device = torch.device("cuda") if torch.cuda.is_available() else torch.device("cpu")
midas.to(device)
midas.eval()

# Use transforms to resize and normalize the image
midas_transforms = torch.hub.load("intel-isl/MiDaS", "transforms")

transform = midas_transforms.dpt_transform

# Load the PNG image
image_path = "./image copy 2.png"
frame = cv2.imread(image_path, cv2.IMREAD_UNCHANGED)

# Ensure the image has an alpha channel and is properly loaded
if frame is None:
    raise ValueError("Image not found or unable to load image.")

# Convert image to RGB if it has an alpha channel (transparency)
if frame.shape[2] == 4:
    frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)

# Resize the image to the desired input size
#frame = cv2.resize(frame, (320, 180))

# Transform input for midas
img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
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

# Display the depth map and the original frame
cv2.imshow("Depth Map", output)
cv2.imshow("Original Image", frame)
cv2.waitKey(0)  # Wait for a key press to close the windows

cv2.destroyAllWindows()
