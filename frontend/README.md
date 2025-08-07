# Image Resizer Frontend

A simple, modern web interface for the Image Resizer application built with Bootstrap 5.

## Features

- 🎨 **Modern UI**: Clean, responsive design with Bootstrap 5
- 📱 **Mobile Friendly**: Works perfectly on all devices
- 🖼️ **Image Preview**: See original and processed images side by side
- ⚡ **Real-time Processing**: Instant feedback with loading states
- 💾 **Easy Download**: One-click download of processed images

## Setup

1. **Start the Backend Server**:
   ```bash
   cd backend/venv
   python main.py
   ```
   The backend will run on `http://localhost:8000`

2. **Open the Frontend**:
   - Simply open `index.html` in your web browser
   - Or serve it with a local server:
     ```bash
     # Using Python
     python -m http.server 3000
     
     # Using Node.js
     npx serve .
     ```

## Usage

1. **Select Image**: Click "Choose File" to select an image
2. **Set Target Size**: Enter the desired file size in KB (10-1000)
3. **Process**: Click "Process Image" to resize
4. **Download**: Click "Download Processed Image" to save

## File Structure

```
frontend-new/
├── index.html      # Main HTML file
├── style.css       # Custom CSS styles
├── script.js       # JavaScript functionality
└── README.md       # This file
```

## Browser Compatibility

- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

## API Endpoint

The frontend communicates with the backend at:
- **URL**: `http://localhost:8000/process-image/`
- **Method**: POST
- **Parameters**: 
  - `file`: Image file
  - `size`: Target size in KB

## Customization

You can easily customize the appearance by modifying `style.css`:
- Change colors in the CSS variables
- Modify gradients and animations
- Adjust responsive breakpoints 