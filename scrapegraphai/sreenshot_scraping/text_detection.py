from PIL import Image
from surya.ocr import run_ocr
import numpy as np
from surya.model.detection.model import load_model as load_det_model, load_processor as load_det_processor
from surya.model.recognition.model import load_model as load_rec_model
from surya.model.recognition.processor import load_processor as load_rec_processor


def DetectText(image, lahguages:list = ["en"]):

    # image = Image.fromarray(image_array.astype('uint8'), 'RGB')
    langs = lahguages
    det_processor, det_model = load_det_processor(), load_det_model()
    rec_model, rec_processor = load_rec_model(), load_rec_processor()
    predictions = run_ocr([image], [langs], det_model, det_processor, rec_model, rec_processor)
    text = "\n".join([line.text for line in predictions[0].text_lines])
    return text

# print(DetectText(Image.open("scrapegraphai\sreenshot_scraping\saved_screenshots\image.jpeg").crop((936,1967,1243,2246))))