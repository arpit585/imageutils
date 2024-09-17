from flask import Flask, render_template, request, redirect, url_for, send_file, jsonify
from PIL import Image
import base64
from io import BytesIO
import logging

app = Flask(__name__)
logging.basicConfig(level=logging.DEBUG)


# Dictionary to hold in-memory image data
image_storage = {}

@app.route('/')
def home():
    return render_template('index.html', active_page='home')
    
@app.route('/upload', methods=['POST'])
def upload_image():
    if 'image' not in request.files:
        app.logger.error("No image file in request")
        return jsonify({'error': 'No image file in request'}), 400
    
    file = request.files['image']
    
    if file.filename == '':
        app.logger.error("No selected file")
        return jsonify({'error': 'No selected file'}), 400
    
    if file:
        try:
            img = Image.open(file.stream)
            width = int(request.form['width'])
            height = int(request.form['height'])

            # Resize the image
            img_resized = img.resize((width, height))

            # Prepare image for immediate display and download (PNG format)
            img_io = BytesIO()
            img_resized.save(img_io, format='PNG')
            img_io.seek(0)

            # Convert the image to base64 for display
            base64_image = base64.b64encode(img_io.getvalue()).decode('utf-8')
            img_data_url = f"data:image/png;base64,{base64_image}"

            # Store the image data for download
            download_filename = f"resized_{file.filename.rsplit('.', 1)[0]}.png"
            image_storage[download_filename] = img_io.getvalue()

            app.logger.info(f"Image processed successfully: {download_filename}")
            return jsonify({
                'image_url': img_data_url,
                'download_filename': download_filename
            })
        
        except Exception as e:
            app.logger.error(f"Error processing image: {str(e)}")
            return jsonify({'error': str(e)}), 500
    
    app.logger.error("Invalid request")
    return jsonify({'error': 'Invalid request'}), 400

@app.route('/download/<filename>')
def download_image(filename):
    if filename in image_storage:
        try:
            return send_file(
                BytesIO(image_storage[filename]),
                as_attachment=True,
                download_name=filename,
                mimetype='image/png'
            )
        except Exception as e:
            app.logger.error(f"Error sending file: {str(e)}")
            return jsonify({'error': 'Error sending file'}), 500
    
    app.logger.error(f"File not found: {filename}")
    return redirect(url_for('home'))


@app.route('/image_compress', methods=['GET', 'POST'])
def image_compress():
    if request.method == 'POST':
        target_size_kb = int(request.form['size'])
        if 'image' not in request.files or not request.files['image'].filename:
            return redirect(url_for('image_compress'))
        image_storage.clear()

        file = request.files['image']
        img = Image.open(file.stream)
        compressed_image_io = compress_image(img, target_size_kb)
        compressed_image_io.seek(0)

        # Convert compressed image to base64 for immediate display
        base64_image = base64.b64encode(compressed_image_io.getvalue()).decode('utf-8')
        img_data_url = f"data:image/{file.mimetype.split('/')[1]};base64,{base64_image}"
        
        return jsonify(img_data_url)

    return render_template('image_compress.html', active_page='image_compress')

def compress_image(image, target_size_kb):
    img_format = image.format if image.format else "JPEG"
    quality = 95
    target_size_bytes = target_size_kb * 1024

    img_io = BytesIO()
    while True:
        img_io.seek(0)
        image.save(img_io, format=img_format, quality=quality)
        img_size = img_io.tell()

        if img_size <= target_size_bytes or quality <= 10:
            break
        
        quality -= 5

    img_io.seek(0)
    return img_io

@app.route('/rotate_image', methods=['GET', 'POST'])
def rotate_image():
    if request.method == 'POST':
        angle = int(request.form['angle'])
        if 'image' not in request.files or not request.files['image'].filename:
            return redirect(url_for('rotate_image'))
        
        file = request.files['image']
        img = Image.open(file.stream)
        img_rotated = img.rotate(angle, expand=True)
        img_io = BytesIO()
        img_rotated.save(img_io, format=img.format)
        img_io.seek(0)

        # Convert rotated image to base64 for immediate display
        base64_image = base64.b64encode(img_io.getvalue()).decode('utf-8')
        img_data_url = f"data:image/{img.format.lower()};base64,{base64_image}"

        # Save the image to memory for download
        download_filename = f"rotated_{file.filename}"
        image_storage[download_filename] = img_io.getvalue()

        return render_template('rotate_image.html',
                               active_page='rotate_image',
                               image_url=img_data_url,
                               download_filename=download_filename)
    
    return render_template('rotate_image.html', active_page='rotate_image')

    
@app.route('/crop_image', methods=['GET', 'POST'])
def crop_image():
    if request.method == 'POST':
        data_url = request.form.get('croppedImageData')
        if not data_url:
            return redirect(url_for('crop_image'))

        image_data = data_url.split(",")[1]
        image_bytes = base64.b64decode(image_data)
        img = Image.open(BytesIO(image_bytes))

        img_io = BytesIO()
        img.save(img_io, format='PNG')
        img_io.seek(0)

        base64_image = base64.b64encode(img_io.getvalue()).decode('utf-8')
        return jsonify({'image': f"data:image/png;base64,{base64_image}"})

    return render_template('crop_image.html', active_page='crop_image')

if __name__ == '__main__':
    app.run(debug=True)
