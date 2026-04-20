from PIL import Image, ImageChops

def trim(im):
    bg = Image.new(im.mode, im.size, im.getpixel((0,0)))
    diff = ImageChops.difference(im, bg)
    diff = ImageChops.add(diff, diff, 2.0, -100)
    bbox = diff.getbbox()
    if bbox:
        return im.crop(bbox)
    return im

def make_transparent(image_path):
    img = Image.open(image_path).convert("RGBA")
    datas = img.getdata()

    new_data = []
    # Threshold for "white" - AI sometimes produces off-white
    limit = 240 
    
    for item in datas:
        if item[0] > limit and item[1] > limit and item[2] > limit:
            new_data.append((255, 255, 255, 0))
        else:
            new_data.append(item)

    img.putdata(new_data)
    # Trim padding
    img = trim(img)
    img.save(image_path, "PNG")
    print(f"✅ Favicon processed and saved to {image_path}")

if __name__ == "__main__":
    make_transparent("/Users/hugogarcia/Desktop/Vomtu/favicon.png")
