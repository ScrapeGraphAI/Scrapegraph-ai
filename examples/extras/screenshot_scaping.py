"""
example of scraping with screenshots
"""
import asyncio
from scrapegraphai.utils.screenshot_scraping import (take_screenshot,
                                                     select_area_with_opencv,
                                                     crop_image, detect_text)

# STEP 1: Take a screenshot
image = asyncio.run(take_screenshot(
    url="https://colab.google/",
    save_path="Savedscreenshots/test_image.jpeg",
    quality = 50
))

# STEP 2 (Optional): Select an area of the image which you want to use for text detection.
LEFT, TOP, RIGHT, BOTTOM = select_area_with_opencv(image)
print("LEFT: ", LEFT, " TOP: ", TOP, " RIGHT: ", RIGHT, " BOTTOM: ", BOTTOM)

# STEP 3 (Optional): Crop the image.
# Note: If any of the coordinates (LEFT, TOP, RIGHT, BOTTOM) is None, 
# it will be set to the corresponding edge of the image.
cropped_image = crop_image(image, LEFT=LEFT, RIGHT=RIGHT,TOP=TOP,BOTTOM=BOTTOM)

# STEP 4: Detect text
TEXT = detect_text(
    cropped_image,          # The image to detect text from
    languages = ["en"]       # The languages to detect text in
)

print("DETECTED TEXT: ")
print(TEXT)
