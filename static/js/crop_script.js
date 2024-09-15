const cropFileInput = document.querySelector('#crop-file-input');
const cropContainer = document.querySelector('#crop-container');
const imageToCrop = document.querySelector('#image-to-crop');
const cropButton = document.querySelector('#crop-button');
const croppedImageContainer = document.querySelector('#cropped-image-container');
const croppedImage = document.querySelector('#cropped-image');
const croppedImageDataInput = document.querySelector('#croppedImageData');
let cropper;

// Handle file input
cropFileInput.addEventListener('change', (e) => {
    const file = e.target.files[0];
    if (file) {
        const reader = new FileReader();
        reader.onload = () => {
            imageToCrop.src = reader.result;
            imageToCrop.style.display = 'block';

            // Initialize Cropper.js
            if (cropper) {
                cropper.destroy();  // Destroy previous cropper instance if any
            }
            cropper = new Cropper(imageToCrop, {
                aspectRatio: 16 / 9,  // Change aspect ratio as needed
                viewMode: 1,
            });
        };
        reader.readAsDataURL(file);
    }
});

// Handle Crop Button Click
cropButton.addEventListener('click', () => {
    if (cropper) {
        const canvas = cropper.getCroppedCanvas();
        const croppedImageData = canvas.toDataURL('image/png');
        
        // Set the base64 image data in the hidden form input
        croppedImageDataInput.value = croppedImageData;
        
        // Submit the form using AJAX
        fetch('/crop_image', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: new URLSearchParams(new FormData(document.querySelector('#cropForm')))
        })
        .then(response => response.json())
        .then(data => {
            if (data.image) {
                croppedImage.src = data.image;
                croppedImageContainer.style.display = 'block';  // Show cropped image
            }
        })
        .catch(error => console.error('Error:', error));
    }
});
