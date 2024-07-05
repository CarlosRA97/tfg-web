import os
import torch
import segmentation_models_pytorch as smp
import cv2
import numpy as np
import matplotlib.pyplot as plt
from .SegmentationModel import SegmentationModel



from PIL import Image
from torchvision import transforms
import torch
import io

def bytes_to_tensor(image_bytes) -> torch.Tensor:
    """Convierte una imagen en bytes a un tensor de PyTorch."""

    # Abrir la imagen desde los bytes
    image = Image.open(io.BytesIO(image_bytes))

    # Aplicar transformaciones (opcional, pero recomendado)
    transform = transforms.Compose([
        transforms.ToTensor(),  # Convertir a tensor de PyTorch
        # Otras transformaciones como redimensionar, normalizar, etc.
    ])
    tensor = transform(image)

    return tensor



def getDevice():
    device = torch.device('cpu')
    if torch.backends.mps.is_available():
        device = torch.device("mps")
    # elif torch.backends.cuda.is_available():
        # device = torch.device("cuda")
    return device


ratio=0.2
MODEL = "Linknet"
ENCODER = "resnet50"
PATH = f"./ai/segmentation/model/{MODEL}/{ENCODER}/"

def predict_mask(image: torch.Tensor) -> torch.Tensor:
    device = getDevice()
    model = SegmentationModel().to(device)
    model.load_state_dict(torch.load(PATH + os.listdir(PATH)[-1]))

    logits_mask=model(image.to(device, dtype=torch.float32).unsqueeze(0))
    pred_mask=torch.sigmoid(logits_mask)
    pred_mask=(pred_mask > ratio)*1.0

    pred_mask_image = pred_mask.detach().cpu().squeeze(0).permute(1, 2, 0)

    return pred_mask_image

def generate_contour(imageBytes: bytes):
    image = bytes_to_tensor(imageBytes)
    pred_mask = predict_mask(image)
    return