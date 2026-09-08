import React, { useState, useRef, useCallback } from 'react';
import { useNavigate } from 'react-router-dom'; // 1. Import useNavigate
import Webcam from 'react-webcam';

export default function Scan() {
  const [selectedImage, setSelectedImage] = useState(null);
  const [imageFile, setImageFile] = useState(null);
  const [isCameraOpen, setIsCameraOpen] = useState(false);
  const [loading, setLoading] = useState(false);

  const webcamRef = useRef(null);
  const fileInputRef = useRef(null);
  const navigate = useNavigate(); // 2. Initialize navigate hook

  const dataURLtoFile = (dataurl, filename) => {
    const arr = dataurl.split(',');
    const mime = arr[0].match(/:(.*?);/)[1];
    const bstr = atob(arr[1]);
    let n = bstr.length;
    const u8arr = new Uint8Array(n);
    while (n--) {
      u8arr[n] = bstr.charCodeAt(n);
    }
    return new File([u8arr], filename, { type: mime });
  };

  const capturePhoto = useCallback(() => {
    const imageSrc = webcamRef.current.getScreenshot();
    if (imageSrc) {
      setSelectedImage(imageSrc);
      const file = dataURLtoFile(imageSrc, 'captured_leaf.jpg');
      setImageFile(file);
      setIsCameraOpen(false);
    }
  }, [webcamRef]);

  const handleFileUpload = (e) => {
    const file = e.target.files[0];
    if (file) {
      setImageFile(file);
      setSelectedImage(URL.createObjectURL(file));
      setIsCameraOpen(false);
    }
  };

  // 3. Updated handler to process image and navigate to results screen
  const handleAnalyze = async () => {
    if (!imageFile && !selectedImage) return;

    setLoading(true);

    try {
      /* OPTION A: If you send image to a backend API first:
      const formData = new FormData();
      formData.append('image', imageFile);
      const response = await fetch('YOUR_API_ENDPOINT', { method: 'POST', body: formData });
      const resultData = await response.json();
      
      // Navigate to results page and pass the API response data
      navigate('/result', { state: { result: resultData, image: selectedImage } });
      */

      // OPTION B: Direct navigation passing image preview state to result screen
      navigate('/result', { state: { image: selectedImage } });
    } catch (error) {
      console.error('Error during analysis:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={styles.container}>
      <h2>Scan Plant Leaf</h2>
      <p style={styles.subtitle}>
        Upload a clear photo of the leaf or use your camera to analyze for diseases
      </p>

      <div style={styles.card}>
        {isCameraOpen ? (
          <div style={styles.cameraWrapper}>
            <Webcam
              audio={false}
              ref={webcamRef}
              screenshotFormat="image/jpeg"
              width="100%"
              videoConstraints={{ facingMode: 'environment' }}
              style={styles.webcam}
            />
            <div style={styles.buttonGroup}>
              <button onClick={capturePhoto} style={styles.captureBtn}>
                📸 Take Photo
              </button>
              <button onClick={() => setIsCameraOpen(false)} style={styles.cancelBtn}>
                Cancel
              </button>
            </div>
          </div>
        ) : selectedImage ? (
          <div style={styles.previewWrapper}>
            <img src={selectedImage} alt="Leaf preview" style={styles.previewImg} />
            <div style={styles.buttonGroup}>
              <button
                onClick={() => {
                  setSelectedImage(null);
                  setImageFile(null);
                }}
                style={styles.secondaryBtn}
              >
                Remove / Retake
              </button>
            </div>
          </div>
        ) : (
          <div style={styles.dropzone}>
            <div style={styles.iconContainer}>📷</div>
            <p style={styles.dropzoneText}>Choose an option to scan your leaf</p>

            <div style={styles.buttonGroup}>
              <button onClick={() => setIsCameraOpen(true)} style={styles.primaryBtn}>
                Open Camera
              </button>

              <button onClick={() => fileInputRef.current.click()} style={styles.secondaryBtn}>
                Upload from Gallery
              </button>
            </div>

            <input
              type="file"
              accept="image/*"
              ref={fileInputRef}
              onChange={handleFileUpload}
              style={{ display: 'none' }}
            />
          </div>
        )}
      </div>

      <button
        onClick={handleAnalyze}
        disabled={!selectedImage || loading}
        style={{
          ...styles.analyzeBtn,
          backgroundColor: selectedImage ? '#4CAF50' : '#a5d6a7',
          cursor: selectedImage ? 'pointer' : 'not-allowed',
        }}
      >
        {loading ? 'Analyzing...' : 'Analyze Leaf'}
      </button>
    </div>
  );
}

const styles = {
  container: {
    maxWidth: '500px',
    margin: '40px auto',
    padding: '20px',
    textAlign: 'center',
    fontFamily: 'sans-serif',
  },
  subtitle: {
    color: '#666',
    fontSize: '14px',
    marginBottom: '20px',
  },
  card: {
    border: '2px dashed #ccc',
    borderRadius: '12px',
    padding: '20px',
    backgroundColor: '#fafafa',
    minHeight: '280px',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
  },
  dropzone: {
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    gap: '12px',
  },
  iconContainer: {
    fontSize: '40px',
  },
  dropzoneText: {
    color: '#555',
    margin: '8px 0',
  },
  cameraWrapper: {
    width: '100%',
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
  },
  webcam: {
    borderRadius: '8px',
    width: '100%',
    maxHeight: '300px',
    objectFit: 'cover',
  },
  previewWrapper: {
    width: '100%',
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
  },
  previewImg: {
    width: '100%',
    maxHeight: '300px',
    objectFit: 'contain',
    borderRadius: '8px',
  },
  buttonGroup: {
    display: 'flex',
    gap: '10px',
    marginTop: '15px',
    justifyContent: 'center',
  },
  primaryBtn: {
    padding: '10px 18px',
    backgroundColor: '#2e7d32',
    color: '#fff',
    border: 'none',
    borderRadius: '6px',
    cursor: 'pointer',
    fontWeight: 'bold',
  },
  secondaryBtn: {
    padding: '10px 18px',
    backgroundColor: '#fff',
    color: '#333',
    border: '1px solid #ccc',
    borderRadius: '6px',
    cursor: 'pointer',
  },
  captureBtn: {
    padding: '10px 20px',
    backgroundColor: '#2196F3',
    color: '#fff',
    border: 'none',
    borderRadius: '6px',
    cursor: 'pointer',
    fontWeight: 'bold',
  },
  cancelBtn: {
    padding: '10px 16px',
    backgroundColor: '#f44336',
    color: '#fff',
    border: 'none',
    borderRadius: '6px',
    cursor: 'pointer',
  },
  analyzeBtn: {
    marginTop: '20px',
    width: '100%',
    padding: '14px',
    color: '#fff',
    border: 'none',
    borderRadius: '8px',
    fontSize: '16px',
    fontWeight: 'bold',
    transition: 'background-color 0.2s',
  },
};