"""
screenshot_preparation module
"""
import asyncio
from io import BytesIO
from playwright.async_api import async_playwright
import numpy as np
from io import BytesIO

async def take_screenshot(url: str, save_path: str = None, quality: int = 100):
    """
    Takes a screenshot of a webpage at the specified URL and saves it if the save_path is specified.
    Parameters:
        url (str): The URL of the webpage to take a screenshot of.
        save_path (str): The path to save the screenshot to. Defaults to None.
        quality (int): The quality of the jpeg image, between 1 and 100. Defaults to 100.
    Returns:
        PIL.Image: The screenshot of the webpage as a PIL Image object.
    """
    try:
        from PIL import Image
    except:
        raise ImportError("The dependencies for screenshot scraping are not installed. Please install them using `pip install scrapegraphai[screenshot_scraper]`.")

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto(url)
        image_bytes = await page.screenshot(path=save_path, 
                                            type="jpeg", 
                                            full_page=True, 
                                            quality=quality)
        await browser.close()
        return Image.open(BytesIO(image_bytes))

def select_area_with_opencv(image):
    """
    Allows you to manually select an image area using OpenCV.
    It is recommended to use this function if your project is on your computer,
    otherwise use select_area_with_ipywidget().
    Parameters:
        image (PIL.Image): The image from which to select an area.
    Returns:
        A tuple containing the LEFT, TOP, RIGHT, and BOTTOM coordinates of the selected area.
    """

    try:
        import cv2 as cv
        from PIL import ImageGrab
    except ImportError:
        raise ImportError("The dependencies for screenshot scraping are not installed. Please install them using `pip install scrapegraphai[screenshot_scraper]`.")


    fullscreen_screenshot = ImageGrab.grab()
    dw, dh = fullscreen_screenshot.size

    def draw_selection_rectanlge(event, x, y, flags, param):
        global ix, iy, drawing, overlay, img
        if event == cv.EVENT_LBUTTONDOWN:
            drawing = True
            ix, iy = x, y
        elif event == cv.EVENT_MOUSEMOVE:
            if drawing == True:
                cv.rectangle(img, (ix, iy), (x, y), (41, 215, 162), -1)
                cv.putText(img, 'PRESS ANY KEY TO SELECT THIS AREA', (ix,
                           iy-10), cv.FONT_HERSHEY_SIMPLEX, 1.5, (55, 46, 252), 5)
                img = cv.addWeighted(overlay, alpha, img, 1 - alpha, 0)
        elif event == cv.EVENT_LBUTTONUP:
            global LEFT, TOP, RIGHT, BOTTOM

            drawing = False
            if ix < x:
                LEFT = int(ix)
                RIGHT = int(x)
            else:
                LEFT = int(x)
                RIGHT = int(ix)
            if iy < y:
                TOP = int(iy)
                BOTTOM = int(y)
            else:
                TOP = int(y)
                BOTTOM = int(iy)

    global drawing, ix, iy, overlay, img
    drawing = False
    ix, iy = -1, -1

    img = np.array(image)
    img = cv.cvtColor(img, cv.COLOR_RGB2BGR)

    img = cv.rectangle(
        img, (0, 0), (image.size[0], image.size[1]), (0, 0, 255), 10)
    img = cv.putText(img, 'SELECT AN AREA', (int(
        image.size[0]*0.3), 100), cv.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255), 5)

    overlay = img.copy()
    alpha = 0.3

    while True:
        cv.namedWindow('SELECT AREA', cv.WINDOW_KEEPRATIO)
        cv.setMouseCallback('SELECT AREA', draw_selection_rectanlge)
        cv.resizeWindow('SELECT AREA', int(
            image.size[0]/(image.size[1]/dh)), dh)

        cv.imshow('SELECT AREA', img)

        if cv.waitKey(20) > -1:
            break

    cv.destroyAllWindows()
    return LEFT, TOP, RIGHT, BOTTOM


def select_area_with_ipywidget(image):
    """
    Allows you to manually select an image area using ipywidgets. 
    It is recommended to use this function if your project is in Google Colab, 
    Kaggle or other similar platform, otherwise use  select_area_with_opencv().
    Parameters:
        image (PIL Image): The input image.
    Returns:
        None
    """

    import matplotlib.pyplot as plt
    import numpy as np
    try:
        from ipywidgets import interact, IntSlider
        import ipywidgets as widgets
    except:
        raise ImportError("The dependencies for screenshot scraping are not installed. Please install them using `pip install scrapegraphai[screenshot_scraper]`.")

    from PIL import Image

    img_array = np.array(image)

    print(img_array.shape)

    def update_plot(top_bottom, left_right, image_size):
        plt.figure(figsize=(image_size, image_size))
        plt.imshow(img_array)
        plt.axvline(x=left_right[0], color='blue', linewidth=1)
        plt.text(left_right[0]+1, -25, 'LEFT', rotation=90, color='blue')
        plt.axvline(x=left_right[1], color='red', linewidth=1)
        plt.text(left_right[1]+1, -25, 'RIGHT', rotation=90, color='red')

        plt.axhline(y=img_array.shape[0] -
                    top_bottom[0], color='green', linewidth=1)
        plt.text(-100, img_array.shape[0] -
                 top_bottom[0]+1, 'BOTTOM', color='green')
        plt.axhline(y=img_array.shape[0]-top_bottom[1],
                    color='darkorange', linewidth=1)
        plt.text(-100, img_array.shape[0] -
                 top_bottom[1]+1, 'TOP', color='darkorange')
        plt.axis('off')
        plt.show()

    top_bottom_slider = widgets.IntRangeSlider(
        value=[int(img_array.shape[0]*0.25), int(img_array.shape[0]*0.75)],
        min=0,
        max=img_array.shape[0],
        step=1,
        description='top_bottom:',
        disabled=False,
        continuous_update=True,
        orientation='vertical',
        readout=True,
        readout_format='d',
    )

    left_right_slider = widgets.IntRangeSlider(
        value=[int(img_array.shape[1]*0.25), int(img_array.shape[1]*0.75)],
        min=0,
        max=img_array.shape[1],
        step=1,
        description='left_right:',
        disabled=False,
        continuous_update=True,
        orientation='horizontal',
        readout=True,
        readout_format='d',
    )
    image_size_bt = widgets.BoundedIntText(
        value=10,
        min=2,
        max=20,
        step=1,
        description='Image size:',
        disabled=False
    )

    interact(update_plot, top_bottom=top_bottom_slider,
             left_right=left_right_slider, image_size=image_size_bt)
    
    return left_right_slider, top_bottom_slider


def crop_image(image, LEFT=None, TOP=None, RIGHT=None, BOTTOM=None,  save_path: str = None):
    """
    Crop an image using the specified coordinates.
    Parameters:
        image (PIL.Image): The image to be cropped.
        LEFT (int, optional): The x-coordinate of the left edge of the crop area. Defaults to None.
        TOP (int, optional): The y-coordinate of the top edge of the crop area. Defaults to None.
        RIGHT (int, optional): The x-coordinate of 
        the right edge of the crop area. Defaults to None.
        BOTTOM (int, optional): The y-coordinate of the bottom edge of the crop area. Defaults to None.
        save_path (str, optional): The path to save the cropped image. Defaults to None.
    Returns:
        PIL.Image: The cropped image.
    Notes:
        If any of the coordinates (LEFT, TOP, RIGHT, BOTTOM) is None, 
        it will be set to the corresponding edge of the image.
        If save_path is specified, the cropped image will be saved as a JPEG file at the specified path.
    """

    if LEFT is None:
        LEFT = 0
    if TOP is None:
        TOP = 0
    if RIGHT is None:
        RIGHT = image.size[0]
    if BOTTOM is None:
        BOTTOM = image.size[1]

    croped_image = image.crop((LEFT, TOP, RIGHT, BOTTOM))
    if save_path is not None:
        from pathlib import Path
        croped_image.save(save_path, "JPEG")

    return image.crop((LEFT, TOP, RIGHT, BOTTOM))
