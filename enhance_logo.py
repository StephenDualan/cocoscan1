#!/usr/bin/env python3
"""
Logo Enhancement Script for CocoScan
This script can be used to enhance the logo image with better styling
"""

import os
from PIL import Image, ImageEnhance, ImageFilter

def enhance_logo():
    """Enhance the logo image with better styling"""
    logo_path = "assets/cocoscan.png"
    
    if not os.path.exists(logo_path):
        print("❌ Logo file not found!")
        return
    
    try:
        # Open the original logo
        with Image.open(logo_path) as img:
            print(f"📸 Original logo: {img.size} pixels")
            
            # Create enhanced versions
            enhanced_versions = {}
            
            # 1. Brightness enhanced
            enhancer = ImageEnhance.Brightness(img)
            enhanced_versions['bright'] = enhancer.enhance(1.2)
            
            # 2. Contrast enhanced
            enhancer = ImageEnhance.Contrast(img)
            enhanced_versions['contrast'] = enhancer.enhance(1.3)
            
            # 3. Sharpness enhanced
            enhancer = ImageEnhance.Sharpness(img)
            enhanced_versions['sharp'] = enhancer.enhance(1.5)
            
            # 4. Combined enhancement
            combined = img.copy()
            combined = ImageEnhance.Brightness(combined).enhance(1.1)
            combined = ImageEnhance.Contrast(combined).enhance(1.2)
            combined = ImageEnhance.Sharpness(combined).enhance(1.3)
            enhanced_versions['combined'] = combined
            
            # Save enhanced versions
            for name, enhanced_img in enhanced_versions.items():
                output_path = f"assets/cocoscan_{name}.png"
                enhanced_img.save(output_path, "PNG")
                print(f"✅ Saved {name} version: {output_path}")
            
            print("\n🎨 Logo enhancement completed!")
            print("💡 You can now use any of these enhanced versions in your app:")
            for name in enhanced_versions.keys():
                print(f"   - assets/cocoscan_{name}.png")
            
    except Exception as e:
        print(f"❌ Error enhancing logo: {e}")

def create_logo_variants():
    """Create different logo variants for different use cases"""
    logo_path = "assets/cocoscan.png"
    
    if not os.path.exists(logo_path):
        print("❌ Logo file not found!")
        return
    
    try:
        with Image.open(logo_path) as img:
            # Create different sizes
            sizes = {
                'small': (64, 64),
                'medium': (128, 128),
                'large': (256, 256),
                'xlarge': (512, 512)
            }
            
            for size_name, size in sizes.items():
                resized = img.resize(size, Image.Resampling.LANCZOS)
                output_path = f"assets/cocoscan_{size_name}.png"
                resized.save(output_path, "PNG")
                print(f"✅ Created {size_name} logo: {output_path}")
            
            print("\n📏 Logo variants created!")
            
    except Exception as e:
        print(f"❌ Error creating logo variants: {e}")

if __name__ == "__main__":
    print("🎨 CocoScan Logo Enhancement Tool")
    print("=" * 40)
    
    print("\n1. Enhance logo quality")
    enhance_logo()
    
    print("\n2. Create logo variants")
    create_logo_variants()
    
    print("\n✨ Logo enhancement completed!") 