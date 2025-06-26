import cv2

cam = cv2.VideoCapture(2)
if not cam.isOpened():
    print("Error: Camera not found.")
    exit(1)

while True:
    ret, frame = cam.read()
    if not ret:
        print("Error: Could not read frame.")
        break

    # Display the frame
    cv2.imshow('Camera Feed', frame)

    # Wait for 1 ms and check if 'q' is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
