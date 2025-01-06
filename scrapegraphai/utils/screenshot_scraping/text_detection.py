"""
text_detection_module
"""


def detect_text(image, languages: list = ["en"]):
    """
    Detects and extracts text from a given image.
    Parameters:
            image (PIL Image): The input image to extract text from.
            languages (list): A list of languages to detect text in. Defaults to ["en"].
                            List of languages can be found here: https://github.com/VikParuchuri/surya/blob/master/surya/languages.py
    Returns:
            str: The extracted text from the image.
    Notes:
            Model weights will automatically download the first time you run this function.
    """

    try:
        from surya.model.detection.model import load_model as load_det_model
        from surya.model.detection.model import load_processor as load_det_processor
        from surya.model.recognition.model import load_model as load_rec_model
        from surya.model.recognition.processor import (
            load_processor as load_rec_processor,
        )
        from surya.ocr import run_ocr
    except ImportError as e:
        raise ImportError(
            "The dependencies for OCR are not installed. Please install them using `pip install scrapegraphai[ocr]`."
        ) from e

    langs = languages
    det_processor, det_model = load_det_processor(), load_det_model()
    rec_model, rec_processor = load_rec_model(), load_rec_processor()
    predictions = run_ocr(
        [image], [langs], det_model, det_processor, rec_model, rec_processor
    )
    text = "\n".join([line.text for line in predictions[0].text_lines])
    return text
