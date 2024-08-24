import asyncio
from playwright.async_api import async_playwright

from io import BytesIO
from PIL import Image, ImageGrab
import os


async def take_screenshot(url:str, image_name:str=None, quality:int=100):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto(url)
        save_path=None
        if image_name is not None:
            dir_path = os.path.abspath('')
            save_path = dir_path + "/scrapegraphai/sreenshot_scraping/saved_screenshots/" + image_name
        image_bytes = await page.screenshot(path=save_path,type="jpeg",full_page=True,quality=quality)
        await browser.close()
        return Image.open(BytesIO(image_bytes))


def select_area_with_opencv(image):
    import cv2 as cv
    import numpy as np

    fullscreen_screenshot = ImageGrab.grab()
    dw, dh=fullscreen_screenshot.size

    def draw_selection_rectanlge(event, x, y, flags, param):
        global ix,iy,drawing,overlay ,img
        if event == cv.EVENT_LBUTTONDOWN:
            drawing = True
            ix,iy = x,y
        elif event == cv.EVENT_MOUSEMOVE:
            if drawing == True:
                cv.rectangle(img, (ix, iy), (x, y), (41, 215, 162), -1)
                cv.putText(img, 'PRESS ANY KEY TO SELECT THIS AREA', (ix, iy-10), cv.FONT_HERSHEY_SIMPLEX, 1.5, (55,46,252), 5)
                img=cv.addWeighted(overlay, alpha, img, 1 - alpha, 0)
        elif event == cv.EVENT_LBUTTONUP:
            global LEFT,TOP,RIGHT,BOTTOM
            
            drawing = False
            if ix<x:
                LEFT=int(ix)
                RIGHT=int(x)
            else:
                LEFT=int(x)
                RIGHT=int(ix)
            if iy<y:
                TOP=int(iy)
                BOTTOM=int(y)
            else:
                TOP=int(y)
                BOTTOM=int(iy)

    global drawing,ix,iy,overlay,img
    drawing = False
    ix,iy = -1,-1

    img =np.array(image)
    img = cv.cvtColor(img, cv.COLOR_RGB2BGR)

    img=cv.rectangle(img, (0, 0), (image.size[0], image.size[1]), (0,0,255), 10)
    img=cv.putText(img, 'SELECT AN AREA', (int(image.size[0]*0.3), 100), cv.FONT_HERSHEY_SIMPLEX, 2, (0,0,255), 5)
    
    overlay = img.copy()
    alpha = 0.3

    while True:
        cv.namedWindow('SELECT AREA', cv.WINDOW_KEEPRATIO) 
        cv.setMouseCallback('SELECT AREA', draw_selection_rectanlge)
        cv.resizeWindow('SELECT AREA', int(image.size[0]/(image.size[1]/dh)), dh) 
        
        cv.imshow('SELECT AREA',img)

        if cv.waitKey(20) > -1:
            break
        
    cv.destroyAllWindows()
    return LEFT, TOP, RIGHT, BOTTOM

def select_area_with_ipywidget(image):
    import matplotlib.pyplot as plt
    import numpy as np
    from ipywidgets import interact, IntSlider
    import ipywidgets as widgets
    from PIL import Image


    # Load an image
    # image_path = 'piping-yes-when-running-scripts-from-curl.jpeg'  # Replace with your image path
    # image = Image.open(image_path)
    img_array = np.array(image)

    print(img_array.shape)

    def update_plot(top_bottom,left_right,image_size):
        plt.figure(figsize = (image_size,image_size))
        plt.imshow(img_array)
        plt.axvline(x=left_right[0], color='blue', linewidth=1)
        plt.text(left_right[0]+1,-25,'LEFT',rotation=90,color='blue')
        plt.axvline(x=left_right[1], color='red', linewidth=1)
        plt.text(left_right[1]+1,-25,'RIGHT',rotation=90, color='red')


        plt.axhline(y=img_array.shape[0]-top_bottom[0], color='green', linewidth=1)
        plt.text(-100,img_array.shape[0]-top_bottom[0]+1,'BOTTOM', color='green')
        plt.axhline(y=img_array.shape[0]-top_bottom[1], color='darkorange', linewidth=1)
        plt.text(-100,img_array.shape[0]-top_bottom[1]+1,'TOP', color='darkorange')
        plt.axis('off')  # Hide axes
        plt.show()


    top_bottom_slider=widgets.IntRangeSlider(
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

    left_right_slider=widgets.IntRangeSlider(
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
    image_size_bt=widgets.BoundedIntText(
        value=10,
        min=2,
        max=20,
        step=1,
        description='Image size:',
        disabled=False
    )

    interact(update_plot,top_bottom= top_bottom_slider ,left_right=left_right_slider ,image_size=image_size_bt)

def crop_image(image,TOP=None, BOTTOM=None, LEFT=None, RIGHT=None, save:bool=True):
    return image.crop((LEFT, TOP, RIGHT, BOTTOM))


# image=asyncio.run(take_screenshot("https://unix.stackexchange.com/questions/690233/piping-yes-when-running-scripts-from-curl"))
# print(select_area_with_opencv(image))