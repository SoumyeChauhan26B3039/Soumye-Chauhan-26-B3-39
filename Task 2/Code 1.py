import cv2
import numpy as np


def canny(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5,5), 0)
    canny = cv2.Canny(blur, 50, 150)
    return canny

def ROI(img):
    height = img.shape[0]
    polygons = np.array([
        [(-100, height), (1500, height), (450, 250), (300, 250)]
    ])
    mask = np.zeros_like(img)
    cv2.fillPoly(mask, polygons, 255)
    masked_image = cv2.bitwise_and(img, mask)
    return masked_image

def display_lines(img, lines):
    line_image = np.zeros_like(img)
    if lines is not None:
        for line in lines:
            x1, y1, x2, y2 = line.reshape(4)
            cv2.line(line_image, (x1, y1), (x2, y2), (255, 0, 0), 10)
    return line_image

def coordinates(img, parameters):
    slope, intercept = parameters
    y1 = img.shape[0]
    y2 = int(y1 * (3/5))
    x1 = int((y1 - intercept) / slope)
    x2 = int((y2 - intercept) / slope)
    return np.array([x1, y1, x2, y2])


def average_slope(img, lines):
    left_fit = []
    right_fit = []
    if lines is not None:
        for line in lines:
            x1, y1, x2, y2 = line.reshape(4)
            parameters = np.polyfit((x1, x2), (y1, y2), 1)
            slope = parameters[0]
            intercept = parameters[1]
            if slope < 0:
                left_fit.append((slope, intercept))
            else:
                right_fit.append((slope, intercept))
    left_fit_average = np.average(left_fit, axis=0)
    right_fit_average = np.average(right_fit, axis=0)
    left_line = coordinates(img, left_fit_average)
    right_line = coordinates(img, right_fit_average)
    return np.array([left_line, right_line])

img = cv2.imread("c:\\Users\\Dell\\Desktop\\Soumye Chauhan 26-B3-39\\Task 2\\2 (1).png", -1)
lane_image = np.copy(img)
canny = canny(lane_image)
roi = ROI(canny)
lines = cv2.HoughLinesP(roi, 2, np.pi/180, 100, np.array([]), minLineLength=40, maxLineGap=5)
average_lines = average_slope(lane_image, lines)
line_image = display_lines(lane_image, average_lines)
final_image = cv2.addWeighted(lane_image, 0.8, line_image, 2, 2)
cv2.imwrite("c:\\Users\\Dell\\Desktop\\Soumye Chauhan 26-B3-39\\Task 2\\output.png", final_image)       
cv2.imshow ("image", final_image)
cv2.waitKey(0)