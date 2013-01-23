from imagekit.specs import ImageSpec 
from imagekit import processors 

class Resize50(processors.Resize): 
    width = 50 
    height = 50 
    quality = 50
    crop = True

class Resize125(processors.Resize): 
    width = 125 
    height = 125 
    quality = 50
    crop = True

class ResizeThumb(processors.Resize): 
    width = 80 
    height = 80 
    crop = True

class ResizeProfile(processors.Resize): 
    width = 150
    height = 150
    crop = True

class ResizeOriginal(processors.Resize): 
    width = 600
    quality = 50
    upscale = False

    
class Thumb(ImageSpec): 
    access_as = 'thumb' 
    pre_cache = False
    processors = [ResizeThumb]

class Original(ImageSpec):
    access_as = 'original'
    pre_cache = True
    processors = [ResizeOriginal]

class Profile(ImageSpec):
    access_as = 'profile'
    pre_cache = False
    processors = [ResizeProfile]

class Prof50(ImageSpec):
    access_as = 'prof50'
    pre_cache = True
    processors = [Resize50]

class Prof125(ImageSpec):
    access_as = 'prof125'
    pre_cache = True
    processors = [Resize125]
    
