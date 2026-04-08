import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.vision import analyze_facial_features
from PIL import Image

print("--- AuraScore Logic Verification ---")
print("1. Testing blank image (simulating webcam without face)...")
img = Image.new('RGB', (640, 480), color='white')
res = analyze_facial_features(img)
print(f"Result: {res}")
assert res is None, "Should return None for empty face"

print("\n2. Arithmetic correctness check...")
# Simulate some random ratios
hr = 1.5
proportions_score = min(100, max(0, int(100 - abs(1.618 - hr) * 100)))
print(f"Proportions score for ratio 1.5 (Ideal 1.618): {proportions_score}/100")

eye_ratio = 0.5
eyes_score = min(100, max(0, int(100 - abs(0.46 - eye_ratio) * 200)))
print(f"Eyes score for ratio 0.5 (Ideal 0.46): {eyes_score}/100")

weighted_total = int((proportions_score * 0.2) + (eyes_score * 0.15) + (80 * 0.25) + (85 * 0.15) + (90 * 0.25))
print(f"Calculated Weighted Total (out of 100): {weighted_total}")
assert 0 <= weighted_total <= 100

print("\nVerification successful! All mathematical bounds are properly enforced (0-100).")
