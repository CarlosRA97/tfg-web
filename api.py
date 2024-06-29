import base64
from typing import Annotated
import uuid
from fastapi import FastAPI, File, Request, Response, UploadFile
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from ai.generative.generate_image import generate_images, numpy_array_to_base64_png

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/images", StaticFiles(directory="images"), name="images")

templates = Jinja2Templates(directory="templates")

class State():
    def __init__(self) -> None:
        self.count = 0
        pass

    def increment(self):
        self.count += 1

state = State()

def contar_images():
    import os
    ruta_imagenes = "images"  # Ruta relativa a la carpeta de imágenes
    lista_imagenes = [f for f in os.listdir(ruta_imagenes) if not f.startswith('.')]
    return len(lista_imagenes)

@app.get("/")
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "countImages": contar_images()})

# Ruta principal que muestra una lista de imágenes
@app.get("/show_images")
async def mostrar_imagenes(request: Request):
    import os
    ruta_imagenes = "images"  # Ruta relativa a la carpeta de imágenes
    lista_imagenes = [f for f in os.listdir(ruta_imagenes) if not f.startswith('.')]
    return templates.TemplateResponse("visorImages.html", {"request": request, "imagenes": lista_imagenes})

@app.get("/api/root")
async def root():
    return {"message": "Hello World"}

@app.post("/ui/click")
async def click(request: Request):
    state.increment()
    return templates.TemplateResponse("button.html", {"request": request, "count": state.count})

@app.post("/scan")
async def scan(request: Request):
    try:
        # Get the raw request body
        raw_data = await request.body()

        # Extract the image data
        mimeType = request.headers.get("Content-Type")
        if mimeType == None:
            return Response(status_code=400)

        extension = mimeType.split("/")[-1]

        # Create a unique filename
        new_filename = f"{uuid.uuid4()}.{extension}"

        # Save the image to a specific directory
        with open(f"images/{new_filename}", "wb") as buffer:
            buffer.write(raw_data)

        return templates.TemplateResponse("captureMapButton.html", {"request":request, "state": ""})
        # ... your image processing logic using image_data ...
    except:
        # Handle any exceptions (e.g., invalid data format)
        return {"error": "Invalid image data"}

@app.get('/generate')
async def generatePage(request: Request):
    return templates.TemplateResponse("generateImage.html", {"request":request})

@app.post('/generate')
async def generateImage(request: Request):
    img = generate_images()
    img = numpy_array_to_base64_png(img)
    return templates.TemplateResponse("image.html", {"request":request, "image": img })