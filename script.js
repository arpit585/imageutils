const imageUpload = document.getElementById('imageUpload');
const canvas = document.getElementById('canvas');
const ctx = canvas.getContext('2d');
const widthInput = document.getElementById('width');
const heightInput = document.getElementById('height');
const resizeButton = document.getElementById('resizeButton');
const downloadLink = document.getElementById('downloadLink');

let image = new Image();

imageUpload.addEventListener('change', (e) => {
    const file = e.target.files[0];
    const reader = new FileReader();
    
    reader.onload = function(event) {
        image.onload = function() {
            widthInput.value = image.width;
            heightInput.value = image.height;
            canvas.width = image.width;
            canvas.height = image.height;
            ctx.drawImage(image, 0, 0, image.width, image.height);
            canvas.style.display = 'block';
        }
        image.src = event.target.result;
    }
    
    if (file) {
        reader.readAsDataURL(file);
    }
});

resizeButton.addEventListener('click', () => {
    const newWidth = parseInt(widthInput.value);
    const newHeight = parseInt(heightInput.value);
    
    canvas.width = newWidth;
    canvas.height = newHeight;
    ctx.drawImage(image, 0, 0, newWidth, newHeight);
    
    downloadLink.href = canvas.toDataURL('image/png');
    downloadLink.style.display = 'inline-block';
});
