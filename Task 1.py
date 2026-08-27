import cv2
img = cv2.imread("c:\\Users\\Dell\\Desktop\\Soumye Chauhan 26-B3-39\\1.png", 0)
img = cv2.resize(img, (400, 400))
cv2.imshow('image', img)
cv2.waitKey(0)
cv2.destroyAllWindows()