# CocoScan APK Builder for Google Colab

# Step 1: Install Buildozer and dependencies
!pip install buildozer
!apt-get update
!apt-get install -y \
    python3-pip build-essential git python3 python3-dev ffmpeg \
    libsdl2-dev libsdl2-image-dev libsdl2-mixer-dev libsdl2-ttf-dev \
    libportmidi-dev libswscale-dev libavformat-dev libavcodec-dev zlib1g-dev \
    libgstreamer1.0 gstreamer1.0-plugins-{bad,base,good,ugly} \
    gstreamer1.0-{tools,x} libgirepository1.0-dev libcairo2-dev pkg-config \
    libgstreamer1.0-dev libgstreamer-plugins-base1.0-dev openjdk-8-jdk autoconf libtool

# Step 2: Upload your project files and folders
from google.colab import files
import os
import shutil

print("Please upload your entire project folder (including subfolders like ui/, model/, images/):")
uploaded = files.upload()

# Step 3: Recreate project structure
os.makedirs('cocoscan/database', exist_ok=True)
os.makedirs('cocoscan/assets', exist_ok=True)
os.makedirs('cocoscan/ui', exist_ok=True)
os.makedirs('cocoscan/model', exist_ok=True)
os.makedirs('cocoscan/images', exist_ok=True)

# Step 4: Move uploaded files to correct locations
for filename in uploaded.keys():
    # Move files to their respective folders
    if filename.startswith('database/'):
        shutil.move(filename, f'cocoscan/database/{os.path.basename(filename)}')
    elif filename.startswith('assets/'):
        shutil.move(filename, f'cocoscan/assets/{os.path.basename(filename)}')
    elif filename.startswith('ui/'):
        shutil.move(filename, f'cocoscan/ui/{os.path.basename(filename)}')
    elif filename.startswith('model/'):
        shutil.move(filename, f'cocoscan/model/{os.path.basename(filename)}')
    elif filename.startswith('images/'):
        shutil.move(filename, f'cocoscan/images/{os.path.basename(filename)}')
    else:
        shutil.move(filename, f'cocoscan/{filename}')

# Step 5: Change working directory
os.chdir('cocoscan')

# Step 6: Build the APK
!buildozer android debug

# Step 7: Download the APK
import glob
apk_files = glob.glob('bin/*.apk')
if apk_files:
    from google.colab import files
    files.download(apk_files[0])
    print("✅ APK build completed successfully!")
    print("📱 You can now install the APK on your Android device")
else:
    print("❌ APK not found. Please check the build output for errors.") 