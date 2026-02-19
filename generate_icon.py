#!/usr/bin/env python3
"""
Generate a proper icon file for the SEO Crawler app
Run this once to generate icon files
"""

def create_icon_svg():
    """Create SVG icon file"""
    svg = '''<?xml version="1.0" encoding="UTF-8"?>
<svg width="256" height="256" viewBox="0 0 256 256" xmlns="http://www.w3.org/2000/svg">
  <!-- Background -->
  <rect width="256" height="256" fill="#1f6aa5"/>
  
  <!-- Magnifying glass circle -->
  <circle cx="95" cy="95" r="65" fill="none" stroke="white" stroke-width="8"/>
  
  <!-- Magnifying glass handle -->
  <line x1="145" y1="145" x2="220" y2="220" stroke="white" stroke-width="8" stroke-linecap="round"/>
  
  <!-- "SEO" text -->
  <text x="128" y="180" font-size="48" font-weight="bold" fill="white" text-anchor="middle" font-family="Arial">SEO</text>
</svg>'''
    
    with open('/Users/aslan/Documents/AIO NLP/icon.svg', 'w') as f:
        f.write(svg)
    print("✓ icon.svg created!")

def create_icon_png():
    """Create PNG icon file"""
    try:
        from PIL import Image, ImageDraw
        
        # Create 256x256 icon
        img = Image.new('RGB', (256, 256), color='#1f6aa5')
        draw = ImageDraw.Draw(img)
        
        # Draw magnifying glass shape
        draw.ellipse([30, 30, 150, 150], outline='white', width=8)  # Circle
        draw.line([(145, 145), (220, 220)], fill='white', width=8)  # Handle
        
        # Draw "SEO" text
        try:
            draw.text((128, 170), "SEO", fill='white', anchor='mm', font=None)
        except:
            pass
        
        img.save('/Users/aslan/Documents/AIO NLP/icon.png')
        print("✓ icon.png created!")
    except ImportError:
        print("⚠ Pillow not installed. Install with: pip install Pillow")

if __name__ == "__main__":
    print("🎨 Generating SEO Crawler icons...\n")
    create_icon_svg()
    try:
        create_icon_png()
    except Exception as e:
        print(f"⚠ PNG creation skipped: {e}")
    print("\n✅ Icon files ready!")
