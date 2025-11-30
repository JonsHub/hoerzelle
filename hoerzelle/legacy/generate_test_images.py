from PIL import Image, ImageDraw, ImageFont
import os

def create_countdown_image(number, size=(800, 600)):
    # Create a new image with a black background
    image = Image.new('RGB', size, 'black')
    draw = ImageDraw.Draw(image)
    
    # Try to use a system font, fallback to default if not found
    try:
        font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 200)
    except:
        font = ImageFont.load_default()
    
    # Draw the number in white
    text = str(number)
    # Get text size
    text_bbox = draw.textbbox((0, 0), text, font=font)
    text_width = text_bbox[2] - text_bbox[0]
    text_height = text_bbox[3] - text_bbox[1]
    
    # Calculate center position
    x = (size[0] - text_width) // 2
    y = (size[1] - text_height) // 2
    
    # Draw the text
    draw.text((x, y), text, fill='white', font=font)
    
    return image

def generate_test_images():
    # Create slideshow directory if it doesn't exist
    os.makedirs('slideshow', exist_ok=True)
    
    # Generate images for countdown from WAITING_TIME to 0
    from program import WAITING_TIME
    
    for i in range(WAITING_TIME, -1, -1):
        image = create_countdown_image(i)
        image.save(f'slideshow/{i}.png')
        print(f'Generated image {i}.png')

if __name__ == '__main__':
    generate_test_images() 