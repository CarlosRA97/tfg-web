# -*- coding: utf-8 -*-
"""224_buena_modificacion6.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1qYnQ4Rv5xI3ljFg2h6t8FYYycaXBbUQb
"""

#%matplotlib inline

import base64
import io
import cv2
import torch
import torch.nn.parallel
import torch.utils.data
import torchvision.utils as vutils
import numpy as np
from PIL import Image
from .Generator import Generator
from .hiper import nz

def getDevice():
    device = torch.device('cpu')
    if torch.backends.mps.is_available():
        device = torch.device("mps")
    # elif torch.backends.cuda.is_available():
        # device = torch.device("cuda")
    return device

def normalize(tensor):
    def norm_ip(img, low, high):
        img.clamp_(min=low, max=high)
        img.sub_(low).div_(max(high - low, 1e-5))

    def norm_range(t, value_range):
        if value_range is not None:
            norm_ip(t, value_range[0], value_range[1])
        else:
            norm_ip(t, float(t.min()), float(t.max()))

    norm_range(tensor, None)
    return tensor

def generate_images(n_images = 1, file_model = "./ai/generative/model/dc_224_generador.pth"):
    device = getDevice()

    load_model = torch.load(file_model, map_location=device, weights_only=False)

    # load generator model
    netG = Generator().to(device)
    netG.load_state_dict(load_model)

    # create random noise
    noise = torch.randn(n_images, nz, 1, 1, device=device)
    fake = netG(noise).detach().cpu()
    
    if n_images > 1:
        img = vutils.make_grid(fake, padding=2, normalize=True)
    else:
        img = normalize(fake[0])
    
    return np.transpose(img.mul(255).type(torch.uint8).numpy(),(1,2,0))
      
def generate_image_to_file():
    img = generate_images()

    cv2.imwrite("gen.png", cv2.cvtColor(img, cv2.COLOR_RGB2BGR))

def numpy_array_to_base64_png(img_array):
    """Convierte un array NumPy a una cadena Base64 PNG.

    Args:
        img_array: Array NumPy que representa la imagen.

    Returns:
        Cadena Base64 de la imagen en formato PNG.
    """

    # Asegurar que el array tenga el tipo de datos correcto (uint8)
    img_array = img_array.astype(np.uint8)

    # Crear una imagen PIL a partir del array
    img = Image.fromarray(img_array)

    # Crear un buffer en memoria para almacenar la imagen PNG
    buffered = io.BytesIO()

    # Guardar la imagen en el buffer como PNG
    img.save(buffered, format="PNG")

    # Codificar el contenido del buffer a Base64
    img_base64 = base64.b64encode(buffered.getvalue()).decode("utf-8")

    return img_base64