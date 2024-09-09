const cropFileInput = document.querySelector('#crop-file-input');
const cropContainer = document.querySelector('#crop-container');
const imageToCrop = document.querySelector('#image-to-crop');
const cropButton = document.querySelector('#crop-button');
const croppedImageContainer = document.querySelector('#cropped-image-container');
const croppedImage = document.querySelector('#cropped-image');
const downloadCropped = document.querySelector('#download-cropped');
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
                cropper.destroy();
            }
            cropper = new Cropper(imageToCrop, {
                aspectRatio: 16 / 9, // You can change aspect ratio as needed
                viewMode: 1,
            });
        };
        reader.readAsDataURL(file);
    }
});

// Handle Crop Button Click
cropButton.addEventListener('click', () => {
    const canvas = cropper.getCroppedCanvas();
    const croppedImageURL = canvas.toDataURL('image/png');
    croppedImage.src = croppedImageURL;
    croppedImageContainer.style.display = 'block';

    // Set the download link for the cropped image
    downloadCropped.href = croppedImageURL;
});
