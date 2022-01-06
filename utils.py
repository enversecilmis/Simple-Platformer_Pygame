from os import listdir
from typing import List, Tuple
from pygame import Surface
from pygame.image import load
from pygame.transform import scale


def loadImageSurfaceArray(path, scaleTimes = 1, scaleXY = (-1,-1)):
    """Return images in the path as list of surfaces"""

    surface_list: List[Surface]
    surface_list = []

    if(scaleXY != (-1,-1)):
        for img in listdir(path):
            img_surface = scale(load(path + '/' + img),(scaleXY[0],scaleXY[1])).convert_alpha()
            surface_list.append(img_surface)
    else:
        for img in listdir(path):
            img_surface = load(path + '/' + img)
            img_width = img_surface.get_rect().width
            img_height = img_surface.get_rect().height
            img_surface = scale(img_surface, (img_width * scaleTimes, img_height * scaleTimes)).convert_alpha()
            surface_list.append(img_surface)

    return surface_list



def loadAnimationSprites(path, scaleXY=(-1,-1), scaleTimes=1):
    """
    Takes a relative folder path (animations folder that have sub folders containing sprites)

    Returns sprites in sub-folders in a dictionary with folder names as keys
    """
    animations: dict[str,list]
    animations = dict()


    # Add animation keys to dictionary
    keys = listdir(path)
    for key in keys:
        animations[key] = []

    # Load images in the folders to keys values
    for animation in animations.keys():
        animations[animation] = loadImageSurfaceArray(path + animation, scaleXY=scaleXY,scaleTimes=scaleTimes)
        
    return animations



def interpolate(x, baseRange: Tuple, targetRange: Tuple) -> int | float:
    """
    Takes a value x in base range (a,b), returns it as in target range (c,d) -> y
    """
    # (y-c)/(d-c) = (x-a)/(b-a)
    # y = (x-a) * (d-c) / (b-a) + c
    return ((x-baseRange[0])*(targetRange[1]-targetRange[0])) / (baseRange[1] - baseRange[0]) + targetRange[0] 
