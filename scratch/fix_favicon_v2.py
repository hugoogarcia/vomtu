from PIL import Image, ImageChops

def fix_transparency(image_path):
    img = Image.open(image_path).convert("RGBA")
    
    # Create mask: anything that isn't clearly "not white" becomes transparent
    # We use a lower threshold to be more aggressive
    datas = img.getdata()
    new_data = []
    
    for item in datas:
        # If it's very light (near white) or has very low saturation (grey-ish)
        # and it's not the vibrant blue we want
        r, g, b, a = item
        
        # A simple heuristic: if it's "white-ish" (all channels high)
        if r > 200 and g > 200 and b > 200:
            new_data.append((255, 255, 255, 0))
        # Or if it's "grey-ish" and not blue enough
        elif abs(r - g) < 20 and abs(g - b) < 20 and r > 100:
             new_data.append((255, 255, 255, 0))
        else:
            new_data.append(item)
            
    img.putdata(new_data)
    
    # Trim transparency
    bg = Image.new(img.mode, img.size, (0, 0, 0, 0))
    diff = ImageChops.difference(img, bg)
    bbox = diff.getbbox()
    if bbox:
        img = img.crop(bbox)
        
    img.save(image_path, "PNG")
    print(f"✅ Favicon hard-cleaned and saved to {image_path}")

if __name__ == "__main__":
    fix_transparency("/Users/hugogarcia/Desktop/Vomtu/favicon.png")
