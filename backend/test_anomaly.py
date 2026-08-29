from pathlib import Path

import cv2

from app.services.anomaly_detection import MVTecAnomalyDetector


DATASET = Path("dataset/mvtec/bottle")

detector = MVTecAnomalyDetector(
    max_reference_images=20
)

reference_count = detector.build_reference(
    DATASET / "train" / "good"
)

print(f"Normal reference images: {reference_count}")


# Find one normal test image
good_images = list(
    (DATASET / "test" / "good").glob("*.png")
)

# Find one defective test image
defect_images = []

for folder in (DATASET / "test").iterdir():

    if folder.is_dir() and folder.name != "good":
        defect_images.extend(
            folder.glob("*.png")
        )


if not good_images:
    raise RuntimeError("No good test images found.")

if not defect_images:
    raise RuntimeError("No defective test images found.")


good_path = good_images[0]
defect_path = defect_images[0]


good_image = cv2.imread(
    str(good_path)
)

defect_image = cv2.imread(
    str(defect_path)
)


good_score = detector.calculate_score(
    good_image
)

defect_score = detector.calculate_score(
    defect_image
)


print()
print("Inspection Results")
print("-------------------")

print(f"Good image:")
print(f"  {good_path}")
print(f"  Anomaly score: {good_score:.4f}")

print()

print(f"Defective image:")
print(f"  {defect_path}")
print(f"  Anomaly score: {defect_score:.4f}")

print()

if defect_score > good_score:
    print("Result: Defective image has a higher anomaly score.")
else:
    print("Result: Baseline detector needs further improvement.")
