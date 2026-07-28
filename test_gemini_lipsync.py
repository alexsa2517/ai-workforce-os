#!/usr/bin/env python3
"""
Test script for Gemini Lip-sync Provider
"""
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent / "backend"))

load_dotenv()

def test_gemini_lipsync():
    """Test Gemini Lip-sync integration"""
    print("\n" + "="*60)
    print("Testing Gemini Lip-sync Provider")
    print("="*60 + "\n")
    
    # Check API Key
    api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
    if api_key:
        print("✓ Google API Key found")
        print(f"  Key: {api_key[:20]}...{api_key[-10:]}")
    else:
        print("✗ Google API Key NOT found")
        print("  Please set GOOGLE_API_KEY or GEMINI_API_KEY in .env")
        return False
    
    # Try importing
    try:
        from app.services.lip_sync.lip_sync_service import LipSyncService
        print("✓ LipSyncService imported successfully")
    except Exception as e:
        print(f"✗ Failed to import LipSyncService: {e}")
        return False
    
    # Try creating service
    try:
        service = LipSyncService(provider="gemini")
        print("✓ GeminiLipSyncProvider initialized successfully")
    except Exception as e:
        print(f"✗ Failed to initialize GeminiLipSyncProvider: {e}")
        return False
    
    # Check FFmpeg
    try:
        import subprocess
        subprocess.run(["ffmpeg", "-version"], capture_output=True, check=True)
        print("✓ FFmpeg is installed and available")
    except FileNotFoundError:
        print("✗ FFmpeg not found. Install with: sudo apt install ffmpeg")
        return False
    
    print("\n" + "="*60)
    print("✓ All checks passed! Gemini Lip-sync is ready to use")
    print("="*60 + "\n")
    
    print("Usage:")
    print("  from app.services.lip_sync.lip_sync_service import LipSyncService")
    print("  service = LipSyncService(provider='gemini')")
    print("  result = service.generate_lip_sync(")
    print("      image_path='character.png',")
    print("      audio_path='dialogue.mp3',")
    print("      output_path='output_video.mp4'")
    print("  )")
    print()
    
    return True

if __name__ == "__main__":
    success = test_gemini_lipsync()
    sys.exit(0 if success else 1)
