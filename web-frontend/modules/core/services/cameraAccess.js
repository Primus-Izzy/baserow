/**
 * Camera access service for mobile file uploads
 * Handles camera permissions, photo capture, and file processing
 */

export class CameraAccessService {
  constructor() {
    this.stream = null
    this.isSupported = this.checkSupport()
  }

  /**
   * Check if camera access is supported
   */
  checkSupport() {
    return !!(
      navigator.mediaDevices &&
      navigator.mediaDevices.getUserMedia &&
      'MediaRecorder' in window
    )
  }

  /**
   * Request camera permissions
   */
  async requestCameraPermission() {
    if (!this.isSupported) {
      throw new Error('Camera access not supported on this device')
    }

    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        video: {
          facingMode: 'environment', // Use back camera by default
          width: { ideal: 1920 },
          height: { ideal: 1080 }
        }
      })
      
      this.stream = stream
      return stream
    } catch (error) {
      if (error.name === 'NotAllowedError') {
        throw new Error('Camera permission denied')
      } else if (error.name === 'NotFoundError') {
        throw new Error('No camera found on this device')
      } else {
        throw new Error(`Camera access failed: ${error.message}`)
      }
    }
  }

  /**
   * Capture photo from camera stream
   */
  async capturePhoto(videoElement, options = {}) {
    if (!this.stream) {
      throw new Error('Camera stream not available')
    }

    const {
      width = 1920,
      height = 1080,
      quality = 0.8,
      format = 'image/jpeg'
    } = options

    return new Promise((resolve, reject) => {
      try {
        const canvas = document.createElement('canvas')
        const context = canvas.getContext('2d')
        
        canvas.width = width
        canvas.height = height
        
        // Draw current video frame to canvas
        context.drawImage(videoElement, 0, 0, width, height)
        
        // Convert to blob
        canvas.toBlob((blob) => {
          if (blob) {
            resolve(blob)
          } else {
            reject(new Error('Failed to capture photo'))
          }
        }, format, quality)
      } catch (error) {
        reject(error)
      }
    })
  }

  /**
   * Access device photo library
   */
  async accessPhotoLibrary(options = {}) {
    const {
      multiple = false,
      accept = 'image/*'
    } = options

    return new Promise((resolve, reject) => {
      const input = document.createElement('input')
      input.type = 'file'
      input.accept = accept
      input.multiple = multiple
      input.capture = 'environment' // Prefer camera on mobile

      input.onchange = (event) => {
        const files = Array.from(event.target.files)
        if (files.length > 0) {
          resolve(files)
        } else {
          reject(new Error('No files selected'))
        }
      }

      input.onerror = () => {
        reject(new Error('File selection failed'))
      }

      // Trigger file picker
      input.click()
    })
  }

  /**
   * Process captured image (resize, compress, etc.)
   */
  async processImage(file, options = {}) {
    const {
      maxWidth = 1920,
      maxHeight = 1080,
      quality = 0.8,
      format = 'image/jpeg'
    } = options

    return new Promise((resolve, reject) => {
      const img = new Image()
      
      img.onload = () => {
        try {
          const canvas = document.createElement('canvas')
          const ctx = canvas.getContext('2d')
          
          // Calculate new dimensions
          let { width, height } = img
          
          if (width > maxWidth || height > maxHeight) {
            const ratio = Math.min(maxWidth / width, maxHeight / height)
            width *= ratio
            height *= ratio
          }
          
          canvas.width = width
          canvas.height = height
          
          // Draw and compress
          ctx.drawImage(img, 0, 0, width, height)
          
          canvas.toBlob((blob) => {
            if (blob) {
              resolve(new File([blob], file.name, { type: format }))
            } else {
              reject(new Error('Image processing failed'))
            }
          }, format, quality)
        } catch (error) {
          reject(error)
        }
      }
      
      img.onerror = () => {
        reject(new Error('Failed to load image'))
      }
      
      img.src = URL.createObjectURL(file)
    })
  }

  /**
   * Stop camera stream
   */
  stopCamera() {
    if (this.stream) {
      this.stream.getTracks().forEach(track => track.stop())
      this.stream = null
    }
  }

  /**
   * Switch camera (front/back)
   */
  async switchCamera(facingMode = 'user') {
    this.stopCamera()
    
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        video: {
          facingMode,
          width: { ideal: 1920 },
          height: { ideal: 1080 }
        }
      })
      
      this.stream = stream
      return stream
    } catch (error) {
      throw new Error(`Failed to switch camera: ${error.message}`)
    }
  }

  /**
   * Get available cameras
   */
  async getAvailableCameras() {
    if (!this.isSupported) return []

    try {
      const devices = await navigator.mediaDevices.enumerateDevices()
      return devices.filter(device => device.kind === 'videoinput')
    } catch (error) {
      console.error('Failed to get available cameras:', error)
      return []
    }
  }

  /**
   * Check camera permissions status
   */
  async checkPermissionStatus() {
    if (!('permissions' in navigator)) {
      return 'unknown'
    }

    try {
      const permission = await navigator.permissions.query({ name: 'camera' })
      return permission.state // 'granted', 'denied', or 'prompt'
    } catch (error) {
      return 'unknown'
    }
  }
}

export default CameraAccessService