import cv2
import numpy as np

image = cv2.imread(r'C:\Users\Dell\Desktop\Soumye Chauhan 26-B3-39\1.png')
image = cv2.resize(image, (800, 600))
output = image.copy()

hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

lower_dark = np.array([0, 0, 0])
upper_dark = np.array([180, 255, 80])
mask = cv2.inRange(hsv, lower_dark, upper_dark)

blurred = cv2.GaussianBlur(mask, (7, 7), 0)
kernel = np.ones((5, 5), np.uint8)
cleaned = cv2.morphologyEx(blurred, cv2.MORPH_CLOSE, kernel)

contours, _ = cv2.findContours(cleaned, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

print("--- Detected Pothole Coordinates ---")

for i, contour in enumerate(contours):
    area = cv2.contourArea(contour)
    

    if 500 < area < 50000:

        x, y, w, h = cv2.boundingRect(contour)
        
    
        aspect_ratio = float(w) / h
        if 0.3 < aspect_ratio < 3.0:
            
            print(f"Pothole #{i+1}: Top-Left=({x}, {y}), Width={w}, Height={h}, Bottom-Right=({x+w}, {y+h})")
            
            
            cv2.rectangle(output, (x, y), (x + w, y + h), (0, 255, 0), 2)
            
        
            coord_text = f"X:{x} Y:{y} W:{w} H:{h}"
            cv2.putText(output, coord_text, (x, max(y - 10, 20)), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

cv2.imshow('Pothole Bounding Boxes & Coordinates', output)
cv2.waitKey(0)
cv2.destroyAllWindows()