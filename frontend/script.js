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

    // Image Converter elements
    const convertForm = document.getElementById('convertForm');
    const convertFileInput = document.getElementById('convertFile');
    const convertFormatInput = document.getElementById('convertFormat');
    const convertBtn = document.getElementById('convertBtn');
    const convertSpinner = convertBtn ? convertBtn.querySelector('.spinner-border') : null;
    const convertResult = document.getElementById('convertResult');
    const convertedPreview = document.getElementById('convertedPreview');
    const convertedDownload = document.getElementById('convertedDownload');
    const convertError = document.getElementById('convertError');
    const convertErrorMessage = document.getElementById('convertErrorMessage');

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

    // Handle form submission (Resizer)
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
        
        // Show uploading state
        setLoading('uploading');
        hideError();
        
        try {
            const formData = new FormData();
            formData.append('file', file);
            formData.append('size', targetSize);
            
            // Show processing state just before fetch
            setLoading('processing');

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
            let errorMessage = 'Failed to process image. Please try again.';
            if (error.message) {
                errorMessage = `Error: ${error.message}`;
            }
            if (error.name === 'TypeError' && error.message.includes('fetch')) {
                errorMessage = 'Cannot connect to server. Please make sure the backend is running on port 8000.';
            }
            showError(errorMessage);
        } finally {
            setLoading(false);
        }
    });

    // Handle form submission (Converter)
    if (convertForm) {
      convertForm.addEventListener('submit', async function(e) {
        e.preventDefault();
        const file = convertFileInput.files[0];
        const format = convertFormatInput.value;
        if (!file) {
          showConvertError('Please select an image file.');
          return;
        }
        setConvertLoading('uploading');
        hideConvertError();
        convertResult.classList.add('d-none');
        try {
          const formData = new FormData();
          formData.append('file', file);
          formData.append('format', format);
          setConvertLoading('processing');
          const response = await fetch('https://image-resizer-backend-ehcz.onrender.com/convert-image/', {
            method: 'POST',
            body: formData
          });
          if (!response.ok) {
            let errorText = `HTTP error! status: ${response.status}`;
            try {
              const errorData = await response.text();
              if (errorData) {
                errorText = `Server error: ${errorData}`;
              }
            } catch (e) {
              errorText = `Server error (${response.status}): ${response.statusText}`;
            }
            throw new Error(errorText);
          }
          const blob = await response.blob();
          const convertedImageUrl = URL.createObjectURL(blob);
          convertedPreview.src = convertedImageUrl;
          convertedPreview.classList.remove('d-none');
          convertedDownload.href = convertedImageUrl;
          // Set download filename with correct extension
          let ext = format.toLowerCase();
          if (ext === 'jpg') ext = 'jpeg';
          convertedDownload.download = `converted.${ext}`;
          convertResult.classList.remove('d-none');
        } catch (error) {
          console.error('Error:', error);
          let errorMessage = 'Failed to convert image. Please try again.';
          if (error.message) {
            errorMessage = `Error: ${error.message}`;
          }
          showConvertError(errorMessage);
        } finally {
          setConvertLoading(false);
        }
      });
    }

    // Helper functions
    function setLoading(state) {
        if (state === 'uploading') {
            processBtn.disabled = true;
            spinner.classList.remove('d-none');
            processBtn.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Uploading...';
        } else if (state === 'processing') {
            processBtn.disabled = true;
            spinner.classList.remove('d-none');
            processBtn.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Processing...';
        } else {
            processBtn.disabled = false;
            spinner.classList.add('d-none');
            processBtn.innerHTML = 'Process Image';
        }
    }
    function setConvertLoading(state) {
      if (!convertBtn || !convertSpinner) return;
      if (state === 'uploading') {
        convertBtn.disabled = true;
        convertSpinner.classList.remove('d-none');
        convertBtn.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Uploading...';
      } else if (state === 'processing') {
        convertBtn.disabled = true;
        convertSpinner.classList.remove('d-none');
        convertBtn.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Processing...';
      } else {
        convertBtn.disabled = false;
        convertSpinner.classList.add('d-none');
        convertBtn.innerHTML = 'Convert Image';
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
    function showConvertError(message) {
      convertErrorMessage.textContent = message;
      convertError.classList.remove('d-none');
    }
    function hideConvertError() {
      convertError.classList.add('d-none');
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