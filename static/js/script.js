const uploadBox = document.querySelector('.upload-box');
const fileInput = document.querySelector('#file-input');

uploadBox.addEventListener('dragover', (e) => {
    e.preventDefault();
    uploadBox.style.backgroundColor = '#cccccc';
});

uploadBox.addEventListener('dragleave', (e) => {
    e.preventDefault();
    uploadBox.style.backgroundColor = '#e0e0e0';
});

uploadBox.addEventListener('drop', (e) => {
    e.preventDefault();
    fileInput.files = e.dataTransfer.files;
    uploadBox.style.backgroundColor = '#e0e0e0';
});
