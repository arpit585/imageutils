from flask import Flask, render_template, request, redirect, url_for, send_file
from PIL import Image
import os
from io import BytesIO

app = Flask(__name__)
UPLOAD_FOLDER = '/Users/arpit/Desktop/Project/uploads'
RESIZED_FOLDER = '/Users/arpit/Desktop/Project/resized'
COMPRESSED_FOLDER = '/Users/arpit/Desktop/Project/compressed'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['RESIZED_FOLDER'] = RESIZED_FOLDER
app.config['COMPRESSED_FOLDER'] = COMPRESSED_FOLDER

# Ensure directories exist
for folder in [UPLOAD_FOLDER, RESIZED_FOLDER, COMPRESSED_FOLDER]:
    if not os.path.exists(folder):
        os.makedirs(folder)

@app.route('/')
def home():
    return render_template('index.html', active_page='home')

@app.route('/upload', methods=['POST'])
def upload_image():
    if 'image' not in request.files:
        return redirect(url_for('home'))
    
    file = request.files['image']
    if file.filename == '':
        return redirect(url_for('home'))
    
    if file:
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(filepath)
        
        # Open image and resize
        width = int(request.form['width'])
        height = int(request.form['height'])
        img = Image.open(filepath)
        img_resized = img.resize((width, height))
        
        # Save the resized image
        resized_path = os.path.join(app.config['RESIZED_FOLDER'], f'resized_{file.filename}')
        img_resized.save(resized_path)
        
        return redirect(url_for('display_image', filename=f'resized_{file.filename}'))

@app.route('/display/<filename>')
def display_image(filename):
    file_url = os.path.join(app.config['RESIZED_FOLDER'], filename)
    
    # Check if file exists
    if not os.path.isfile(file_url):
        return f"File {filename} not found!", 404
    
    return render_template('display_image.html', image_url=url_for('static', filename=os.path.join('resized', filename)), filename=filename)

@app.route('/download/<filename>')
def download_image(filename):
    file_path = os.path.join(app.config['RESIZED_FOLDER'], filename)
    
    # Check if file exists
    if not os.path.isfile(file_path):
        return f"File {filename} not found!", 404
    
    return send_file(file_path, as_attachment=True, download_name=filename)

@app.route('/crop_image', methods=['GET', 'POST'])
def crop_image():
    return render_template('crop_image.html', active_page='crop_image')

@app.route('/image_compress', methods=['GET', 'POST'])
def image_compress():
    if request.method == 'POST':
        target_size_kb = int(request.form['size'])  # Get target size in KB from user
        if 'image' not in request.files:
            return redirect(url_for('image_compress'))
        
        file = request.files['image']
        if file.filename == '':
            return redirect(url_for('image_compress'))
        
        if file:
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(filepath)
            
            # Compress the image to the target size
            img = Image.open(filepath)
            compressed_filename = f"compressed_{file.filename}"
            compressed_filepath = os.path.join(app.config['COMPRESSED_FOLDER'], compressed_filename)
            
            compress_image(img, compressed_filepath, target_size_kb)
            
            return redirect(url_for('display_compressed_image', filename=compressed_filename))

    return render_template('image_compress.html', active_page='image_compress')

@app.route('/display_compressed/<filename>')
def display_compressed_image(filename):
    file_url = os.path.join(app.config['COMPRESSED_FOLDER'], filename)
    
    # Check if file exists
    if not os.path.isfile(file_url):
        return f"File {filename} not found!", 404
    
    return render_template('display_image.html', image_url=url_for('static', filename=os.path.join('compressed', filename)), filename=filename)

@app.route('/download_compressed/<filename>')
def download_compressed_image(filename):
    file_path = os.path.join(app.config['COMPRESSED_FOLDER'], filename)
    
    # Check if file exists
    if not os.path.isfile(file_path):
        return f"File {filename} not found!", 404
    
    return send_file(file_path, as_attachment=True, download_name=filename)

def compress_image(image, output_path, target_size_kb):
    """
    Compress the image to the target size in KB.
    """
    img_format = image.format if image.format else "JPEG"  # Preserve the format, default to JPEG if unknown
    quality = 95  # Start with high quality
    target_size_bytes = target_size_kb * 1024  # Convert target size from KB to Bytes
    
    while True:
        img_io = BytesIO()  # Use BytesIO for in-memory processing
        image.save(img_io, format=img_format, quality=quality)
        img_size = img_io.tell()  # Get the file size
        
        if img_size <= target_size_bytes or quality <= 10:
            break
        
        quality -= 5
    
    with open(output_path, 'wb') as f:
        f.write(img_io.getvalue())

@app.route('/rotate_image', methods=['GET', 'POST'])
def rotate_image():
    if request.method == 'POST':
        angle = int(request.form['angle'])  # Get rotation angle from user
        if 'image' not in request.files:
            return redirect(url_for('rotate_image'))
        
        file = request.files['image']
        if file.filename == '':
            return redirect(url_for('rotate_image'))
        
        if file:
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(filepath)
            
            # Open image and rotate
            img = Image.open(filepath)
            rotated_filename = f"rotated_{file.filename}"
            rotated_filepath = os.path.join(app.config['RESIZED_FOLDER'], rotated_filename)
            img_rotated = img.rotate(angle, expand=True)  # Rotate image
            
            img_rotated.save(rotated_filepath)
            
            return redirect(url_for('display_rotated_image', filename=rotated_filename))
    
    return render_template('rotate_image.html', active_page='rotate_image')

@app.route('/display_rotated/<filename>')
def display_rotated_image(filename):
    file_url = os.path.join(app.config['RESIZED_FOLDER'], filename)
    
    # Check if file exists
    if not os.path.isfile(file_url):
        return f"File {filename} not found!", 404
    
    return render_template('display_image.html', image_url=url_for('static', filename=os.path.join('resized', filename)), filename=filename)

if __name__ == '__main__':
    app.run(debug=True)
