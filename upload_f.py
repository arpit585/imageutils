from flask import Flask, render_template, request, redirect, url_for, send_file
from PIL import Image
from io import BytesIO
from google.cloud import storage
from google.oauth2 import service_account
from google_c import upload_image_on_cloud, download_image_from_cloud

app = Flask(__name__)

# Path to your service account key file
SERVICE_ACCOUNT_FILE = 'my_flask_app/credential.json'

# Initialize a Google Cloud Storage client
credentials = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE)
client = storage.Client(credentials=credentials)
bucket = client.bucket('imageutils')

@app.route('/')
def home():
    # Render the form to upload and resize images
    return render_template('index.html', active_page='home')

@app.route('/upload', methods=['POST'])
def upload_image_to_cloud():
    if 'image' not in request.files or not request.files['image'].filename:
        return redirect(url_for('home'))

    file = request.files['image']
    if file:
        # Read image from the request as a BytesIO object
        img = Image.open(file)

        # Resize the image
        width = int(request.form['width'])
        height = int(request.form['height'])
        img_resized = img.resize((width, height))

        # Save resized image to a BytesIO object (in memory)
        img_io = BytesIO()
        img_resized.save(img_io, format=img.format)  # Save in the same format as uploaded image
        img_io.seek(0)  # Go back to the start of the BytesIO object

        # Define the destination blob name in the cloud
        resized_filename = f'resized_{file.filename}'
        cloud_destination = f'resize/{resized_filename}'

        # Upload the in-memory image to Google Cloud Storage
        image_url = upload_image_on_cloud(img_io, cloud_destination)

        # Pass the URL of the uploaded image to the template
        return render_template('index.html', active_page='home', image_url=image_url, download_filename=resized_filename)
    
    return redirect(url_for('home'))

@app.route('/download/<filename>')
def download_image(filename):
    # Fetch image from Google Cloud Storage
    file_io = download_image_from_cloud(f'resize/{filename}')
    if file_io:
        return send_file(file_io, as_attachment=True, download_name=filename)
    else:
        return f"File {filename} not found in cloud storage!", 404
        

@app.route('/crop_image', methods=['GET', 'POST'])
def crop_image():
    return render_template('crop_image.html', active_page='crop_image')

@app.route('/image_compress', methods=['GET', 'POST'])
def image_compress():
    if request.method == 'POST':
        target_size_kb = int(request.form['size'])  # Get target size in KB from user
        if 'image' not in request.files or not request.files['image'].filename:
            return redirect(url_for('image_compress'))
        file = request.files['image']

        # Save image to a BytesIO object
        file_io = BytesIO(file.read())
        file_io.seek(0)  # Reset BytesIO stream position
        
        # Compress the image
        img = Image.open(file_io)
        compressed_filename = f"compressed_{file.filename}"
        compressed_file_io = BytesIO()
        compress_image(img, compressed_file_io, target_size_kb)
        
        # Upload compressed image to Google Cloud Storage
        compressed_cloud_destination = f'compressed/{compressed_filename}'
        upload_image_on_cloud(compressed_file_io, compressed_cloud_destination)

        # Redirect to display the compressed image
        return redirect(url_for('display_compressed_image', filename=compressed_filename))
    
    return render_template('image_compress.html', active_page='image_compress')

@app.route('/display_compressed/<filename>')
def display_compressed_image(filename):
    file_url = f"https://storage.googleapis.com/imageutils/compressed/{filename}"
    return render_template('display_image.html', image_url=file_url, filename=filename)

@app.route('/download_compressed/<filename>')
def download_compressed_image(filename):
    # Fetch compressed image from Google Cloud Storage
    file_io = download_image_from_cloud(f'compressed/{filename}')
    if file_io:
        return send_file(file_io, as_attachment=True, download_name=filename)
    else:
        return f"File {filename} not found in cloud storage!", 404

def compress_image(image, output_io, target_size_kb):
    """
    Compress the image to the target size in KB.
    """
    img_format = image.format if image.format else "JPEG"  # Preserve the format, default to JPEG if unknown
    quality = 95  # Start with high quality
    target_size_bytes = target_size_kb * 1024  # Convert target size from KB to Bytes
    
    while True:
        output_io.seek(0)  # Reset output stream
        image.save(output_io, format=img_format, quality=quality)
        img_size = output_io.tell()  # Get the file size
        
        if img_size <= target_size_bytes or quality <= 10:
            break
        
        quality -= 5

    output_io.seek(0)  # Reset output stream position
    print(f"Compressed image ready.")
    print(f"File size: {img_size} bytes")

@app.route('/rotate_image', methods=['GET', 'POST'])
def rotate_image():
    if request.method == 'POST':
        angle = int(request.form['angle'])  # Get rotation angle from user
        if 'image' not in request.files or not request.files['image'].filename:
            return redirect(url_for('rotate_image'))
        
        file = request.files['image']

        # Save image to a BytesIO object
        file_io = BytesIO(file.read())
        file_io.seek(0)  # Reset BytesIO stream position

        # Rotate image
        img = Image.open(file_io)
        rotated_filename = f"rotated_{file.filename}"
        rotated_file_io = BytesIO()
        img_rotated = img.rotate(angle, expand=True)  # Rotate image
        img_rotated.save(rotated_file_io, format=img.format)
        rotated_file_io.seek(0)  # Go back to the start of the BytesIO object

        # Upload rotated image to Google Cloud Storage
        rotated_cloud_destination = f'rotated/{rotated_filename}'
        upload_image_on_cloud(rotated_file_io, rotated_cloud_destination)
        
        return redirect(url_for('display_rotated_image', filename=rotated_filename))
    
    return render_template('rotate_image.html', active_page='rotate_image')

@app.route('/display_rotated/<filename>')
def display_rotated_image(filename):
    file_url = f"https://storage.googleapis.com/imageutils/rotated/{filename}"
    return render_template('display_image.html', image_url=file_url, filename=filename)

if __name__ == '__main__':
    app.run(debug=True)
