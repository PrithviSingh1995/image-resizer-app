// Image Resizer Application JavaScript

document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('imageForm');
    const fileInput = document.getElementById('imageFile');
    const targetSizeInput = document.getElementById('targetSize');
    const processBtn = document.getElementById('processBtn');
    const preview = document.getElementById('preview');
    const originalPreview = document.getElementById('originalPreview');
    const processedPreview = document.getElementById('processedPreview');
    const originalSize = document.getElementById('originalSize');
    const processedSize = document.getElementById('processedSize');
    const downloadLink = document.getElementById('downloadLink');
    const error = document.getElementById('error');
    const errorMessage = document.getElementById('errorMessage');
    const spinner = processBtn.querySelector('.spinner-border');

    // Show file preview when selected
    fileInput.addEventListener('change', function(e) {
        const file = e.target.files[0];
        if (file) {
            // Show original image preview
            const reader = new FileReader();
            reader.onload = function(e) {
                originalPreview.src = e.target.result;
                originalSize.textContent = formatFileSize(file.size);
                preview.classList.remove('d-none');
                hideError();
            };
            reader.readAsDataURL(file);
        }
    });

    // Handle form submission
    form.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        const file = fileInput.files[0];
        const targetSize = parseInt(targetSizeInput.value);
        
        if (!file) {
            showError('Please select an image file.');
            return;
        }
        
        if (targetSize < 10 || targetSize > 1000) {
            showError('Target size must be between 10 and 1000 KB.');
            return;
        }
        
        // Show loading state
        setLoading(true);
        hideError();
        
        try {
            const formData = new FormData();
            formData.append('file', file);
            formData.append('size', targetSize);
            
            const response = await fetch('https://image-resizer-backend-ehcz.onrender.com/process-image/', {
                method: 'POST',
                body: formData
            });
            
            if (!response.ok) {
                // Try to get error details from response
                let errorText = `HTTP error! status: ${response.status}`;
                try {
                    const errorData = await response.text();
                    if (errorData) {
                        errorText = `Server error: ${errorData}`;
                    }
                } catch (e) {
                    // If we can't read the error text, use the status
                    errorText = `Server error (${response.status}): ${response.statusText}`;
                }
                throw new Error(errorText);
            }
            
            // Get the processed image blob
            const blob = await response.blob();
            
            // Create preview of processed image
            const processedImageUrl = URL.createObjectURL(blob);
            processedPreview.src = processedImageUrl;
            processedSize.textContent = formatFileSize(blob.size);
            
            // Set up download link
            downloadLink.href = processedImageUrl;
            downloadLink.download = `processed_${file.name}`;
            
            // Show success message
            showSuccess('Image processed successfully!');
            
        } catch (error) {
            console.error('Error:', error);
            
            // Try to get more detailed error information
            let errorMessage = 'Failed to process image. Please try again.';
            
            if (error.message) {
                errorMessage = `Error: ${error.message}`;
            }
            
            // If it's a network error, provide more specific message
            if (error.name === 'TypeError' && error.message.includes('fetch')) {
                errorMessage = 'Cannot connect to server. Please make sure the backend is running on port 8000.';
            }
            
            showError(errorMessage);
        } finally {
            setLoading(false);
        }
    });

    // Helper functions
    function setLoading(loading) {
        if (loading) {
            processBtn.disabled = true;
            spinner.classList.remove('d-none');
            processBtn.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Processing...';
        } else {
            processBtn.disabled = false;
            spinner.classList.add('d-none');
            processBtn.innerHTML = 'Process Image';
        }
    }

    function showError(message) {
        errorMessage.textContent = message;
        error.classList.remove('d-none');
        preview.classList.add('d-none');
    }

    function hideError() {
        error.classList.add('d-none');
    }

    function showSuccess(message) {
        // You can add a success toast or notification here
        console.log(message);
    }

    function formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }

    // Add some nice animations
    const card = document.querySelector('.card');
    card.style.opacity = '0';
    card.style.transform = 'translateY(20px)';
    
    setTimeout(() => {
        card.style.transition = 'all 0.5s ease';
        card.style.opacity = '1';
        card.style.transform = 'translateY(0)';
    }, 100);
}); 