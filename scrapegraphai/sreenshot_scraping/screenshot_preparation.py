import asyncio
from playwright.async_api import async_playwright
import numpy as np
from io import BytesIO
from PIL import Image
import os

async def take_screenshot(url:str, image_name:str="image.jpeg", quality:int=100):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto(url)
        dir_path = os.path.dirname(os.path.realpath(__file__))
        save_path = dir_path + "/saved_screenshots/" + image_name
        image_bytes = await page.screenshot(path=save_path,type="jpeg",full_page=True,quality=quality)
        await browser.close()
        return np.array(Image.open(BytesIO(image_bytes)))

# image_array=asyncio.run(take_screenshot("https://unix.stackexchange.com/questions/690233/piping-yes-when-running-scripts-from-curl"))
# print(image_array.shape)

def select_area(image_array):
    pass

def crop_image(image,TOP, BOTTOM, LEFT, RIGHT):
    return image[BOTTOM:TOP, LEFT:RIGHT, :]


