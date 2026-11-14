/**
 * SMART POULTRY HEALTH & DISEASE-RISK SYSTEM
 * Live Camera Stream & Photo Capture Engine (camera.js)
 */

const LiveCamera = {
  stream: null,
  facingMode: 'environment', // 'environment' (rear) or 'user' (front)
  videoElement: null,

  async startCamera(videoElementId = 'liveCameraStream') {
    this.videoElement = document.getElementById(videoElementId);
    if (!this.videoElement) return false;

    // Check if browser supports mediaDevices
    if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
      showToast('Camera access is not supported on this browser. Please use gallery upload.', 'warning');
      return false;
    }

    try {
      // Stop any existing stream
      this.stopCamera();

      const constraints = {
        video: {
          facingMode: { ideal: this.facingMode },
          width: { ideal: 1280 },
          height: { ideal: 720 }
        },
        audio: false
      };

      this.stream = await navigator.mediaDevices.getUserMedia(constraints);
      this.videoElement.srcObject = this.stream;
      await this.videoElement.play();

      document.getElementById('liveCameraContainer').classList.remove('d-none');
      document.getElementById('mobUploadArea').classList.add('d-none');
      document.getElementById('mobPreviewContainer').classList.add('d-none');
      return true;
    } catch (err) {
      console.warn('Camera stream error:', err);
      let msg = 'Could not access camera. Please allow camera permissions or upload from gallery.';
      if (err.name === 'NotAllowedError' || err.name === 'PermissionDeniedError') {
        msg = 'Camera permission was denied. Please allow camera access in browser settings.';
      } else if (err.name === 'NotFoundError') {
        msg = 'No camera found on this device. Please upload from gallery.';
      }
      showToast(msg, 'danger');
      return false;
    }
  },

  captureSnapshot() {
    if (!this.videoElement || !this.stream) return null;

    const canvas = document.createElement('canvas');
    canvas.width = this.videoElement.videoWidth || 640;
    canvas.height = this.videoElement.videoHeight || 480;

    const ctx = canvas.getContext('2d');
    ctx.drawImage(this.videoElement, 0, 0, canvas.width, canvas.height);

    const dataUrl = canvas.toDataURL('image/jpeg', 0.9);

    // Stop camera stream once snapped
    this.stopCamera();

    return dataUrl;
  },

  async toggleFacingMode() {
    this.facingMode = this.facingMode === 'environment' ? 'user' : 'environment';
    showToast(`Flipped camera to ${this.facingMode === 'environment' ? 'rear' : 'front'} lens`, 'info');
    await this.startCamera();
  },

  stopCamera() {
    if (this.stream) {
      this.stream.getTracks().forEach(track => track.stop());
      this.stream = null;
    }
    if (this.videoElement) {
      this.videoElement.srcObject = null;
    }
    const container = document.getElementById('liveCameraContainer');
    if (container) container.classList.add('d-none');
  }
};
