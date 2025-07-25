from PIL import Image, ImageStat, ImageFilter

BRIGHTNESS_THRESHOLD = 40   # minimum átlag fényerő
BLUR_THRESHOLD = 40        # minimum élkontraszt

def is_good_training_image(image_path):
    try:
        image = Image.open(image_path).convert('L')  # grayscale
        stat = ImageStat.Stat(image)
        brightness = stat.mean[0]

        # Blur (élesség) értékelése élkontraszttal
        edge_image = image.filter(ImageFilter.FIND_EDGES)
        edge_stat = ImageStat.Stat(edge_image)
        edge_contrast = edge_stat.stddev[0]

        return brightness >= BRIGHTNESS_THRESHOLD and edge_contrast >= BLUR_THRESHOLD
    except Exception as e:
        print(f"[HIBA] is_good_training_image: {e}")
        return False
