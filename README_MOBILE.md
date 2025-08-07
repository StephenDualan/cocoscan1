# CocoScan Mobile App Builder

This guide will help you convert your CocoScan desktop application into a mobile Android app.

## 🚀 Quick Start Options

### Option 1: Google Colab (Recommended - Free & Easy)

1. **Go to Google Colab**: Visit [colab.research.google.com](https://colab.research.google.com)

2. **Create a new notebook**

3. **Copy and paste the contents** of `build_apk_colab.py` into a cell

4. **Run the cell** - it will:
   - Install all required dependencies
   - Ask you to upload your project files
   - Build the APK automatically
   - Download the APK to your computer

5. **Install on your Android device**:
   - Enable "Install from unknown sources" in Android settings
   - Transfer the APK to your device
   - Install the APK

### Option 2: WSL (Windows Subsystem for Linux)

1. **Install WSL**:
   ```powershell
   wsl --install
   ```

2. **Restart your computer**

3. **Open WSL terminal** and navigate to your project:
   ```bash
   cd /mnt/c/Users/steph/OneDrive/Desktop/cocoscan
   ```

4. **Install Buildozer**:
   ```bash
   sudo apt-get update
   sudo apt-get install -y python3-pip buildozer
   ```

5. **Build the APK**:
   ```bash
   buildozer android debug
   ```

6. **Find your APK** in the `bin/` folder

### Option 3: Linux Virtual Machine

1. **Download and install VirtualBox**
2. **Install Ubuntu** in the VM
3. **Follow the WSL instructions** inside the VM

## 📱 What's Included in the Mobile App

✅ **Welcome Screen** with CocoScan logo  
✅ **Login/Signup** functionality  
✅ **Home Dashboard** with capture options  
✅ **Camera Integration** for leaf scanning  
✅ **File Upload** for existing images  
✅ **Local Database** (SQLite) for scan history  
✅ **Mobile-optimized UI**  

## 🔧 Configuration Changes Made

- **Database**: Changed from MySQL to SQLite for mobile compatibility
- **Permissions**: Added camera and storage permissions
- **App Info**: Updated title, package name, and domain
- **Dependencies**: Added required mobile libraries

## 📋 Requirements

- **Android device** with API level 21+ (Android 5.0+)
- **Internet connection** for initial setup
- **Camera permission** for leaf scanning
- **Storage permission** for saving images

## 🛠 Troubleshooting

### Common Issues:

1. **"Install from unknown sources" error**:
   - Go to Settings > Security > Unknown sources
   - Enable for your file manager

2. **App crashes on startup**:
   - Check that all permissions are granted
   - Restart the app

3. **Camera not working**:
   - Grant camera permission in app settings
   - Make sure no other app is using the camera

4. **Build fails in Colab**:
   - Try running the cell again
   - Check that all files were uploaded correctly

## 📞 Support

If you encounter any issues:
1. Check the troubleshooting section above
2. Verify all project files are present
3. Try the Google Colab option for the most reliable build

## 🎉 Success!

Once you have your APK installed, you'll have a fully functional mobile version of CocoScan that can:
- Capture leaf images with your phone's camera
- Upload existing images from your gallery
- Store scan history locally on your device
- Work offline without internet connection 