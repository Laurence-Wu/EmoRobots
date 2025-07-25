import cv2

print("Testing available cameras...")

# Test camera indices 0-5
for i in range(6):
    cap = cv2.VideoCapture(i)
    if cap.isOpened():
        ret, frame = cap.read()
        if ret:
            print(f"Camera {i}: Working - Resolution: {frame.shape[1]}x{frame.shape[0]}")
        else:
            print(f"Camera {i}: Opened but can't read frames")
        cap.release()
    else:
        print(f"Camera {i}: Not available")

print("\nDone testing cameras.")