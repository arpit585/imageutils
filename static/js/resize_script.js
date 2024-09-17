document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('resize-form');
    const imageDisplay = document.getElementById('image-display');
    const resizedImage = document.getElementById('resized-image');
    const downloadLink = document.getElementById('download-resized');

    form.addEventListener('submit', async function(e) {
        e.preventDefault();

        // Disable the submit button to prevent multiple submissions
        const submitButton = form.querySelector('button[type="submit"]');
        submitButton.disabled = true;

        const formData = new FormData(form);

        try {
            // Show a loading message or spinner (optional)
            imageDisplay.innerHTML = "<p>Processing image, please wait...</p>";

            const response = await fetch('/upload', {
                method: 'POST',
                body: formData
            });

            if (!response.ok) {
                throw new Error('Image upload failed');
            }

            const data = await response.json();

            if (data.image_url && data.download_filename) {
                // Update the image source and the download link
                resizedImage.src = data.image_url;
                downloadLink.href = data.image_url;
                downloadLink.download = data.download_filename;

                // Display the resized image section
                imageDisplay.style.display = 'block';
            } else {
                // Display an error if the image was not processed correctly
                imageDisplay.innerHTML = "<p>Failed to resize the image. Please try again.</p>";
            }
        } catch (error) {
            console.error('Error:', error);
            imageDisplay.innerHTML = `<p>Error: ${error.message}</p>`;
        } finally {
            // Re-enable the submit button
            submitButton.disabled = false;
        }
    });
});
