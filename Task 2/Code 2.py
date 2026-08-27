import cv2
import numpy as np
import matplotlib.pyplot as plt

def pipeline(img):
    hls = cv2.cvtColor(img, cv2.COLOR_BGR2HLS)
    s_channel = hls[:, :, 2]
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    sobelx = cv2.Sobel(gray, cv2.CV_64F, 1, 0)
    abs_sobel64f = np.absolute(sobelx)
    scaled_sobel = np.uint8(255 * abs_sobel64f / np.max(abs_sobel64f))
    
    sxbinary = np.zeros_like(scaled_sobel)
    sxbinary[(scaled_sobel >= 20) & (scaled_sobel <= 100)] = 1
    
    s_binary = np.zeros_like(s_channel)
    s_binary[(s_channel >= 170) & (s_channel <= 255)] = 1
    
    combined = np.zeros_like(sxbinary)
    combined[(s_binary == 1) | (sxbinary == 1)] = 255
    return combined

def warp(img):
    h, w = img.shape[:2]
    src = np.float32([[w * 0.43, h * 0.65], [w * 0.57, h * 0.65], 
                      [w * 0.15, h], [w * 0.85, h]])
    dst = np.float32([[200, 0], [w - 200, 0], 
                      [200, h], [w - 200, h]])
    
    M = cv2.getPerspectiveTransform(src, dst)
    Minv = cv2.getPerspectiveTransform(dst, src)
    warped = cv2.warpPerspective(img, M, (w, h), flags=cv2.INTER_LINEAR)
    return warped, Minv

def fit_polynomial(warped_binary):
    histogram = np.sum(warped_binary[warped_binary.shape[0] // 2:, :], axis=0)
    midpoint = int(histogram.shape[0] // 2)
    leftx_base = np.argmax(histogram[:midpoint])
    rightx_base = np.argmax(histogram[midpoint:]) + midpoint

    nwindows = 9
    window_height = int(warped_binary.shape[0] // nwindows)
    nonzero = warped_binary.nonzero()
    nonzeroy = np.array(nonzero[0])
    nonzerox = np.array(nonzero[1])
    
    leftx_current, rightx_current = leftx_base, rightx_base
    margin, minpix = 100, 50
    left_lane_inds, right_lane_inds = [], []

    for window in range(nwindows):
        win_y_low = warped_binary.shape[0] - (window + 1) * window_height
        win_y_high = warped_binary.shape[0] - window * window_height
        
        win_xleft_low, win_xleft_high = leftx_current - margin, leftx_current + margin
        win_xright_low, win_xright_high = rightx_current - margin, rightx_current + margin
        
        good_left_inds = ((nonzeroy >= win_y_low) & (nonzeroy < win_y_high) & 
                          (nonzerox >= win_xleft_low) & (nonzerox < win_xleft_high)).nonzero()[0]
        good_right_inds = ((nonzeroy >= win_y_low) & (nonzeroy < win_y_high) & 
                           (nonzerox >= win_xright_low) & (nonzerox < win_xright_high)).nonzero()[0]
        
        left_lane_inds.append(good_left_inds)
        right_lane_inds.append(good_right_inds)
        
        if len(good_left_inds) > minpix:
            leftx_current = int(np.mean(nonzerox[good_left_inds]))
        if len(good_right_inds) > minpix:
            rightx_current = int(np.mean(nonzerox[good_right_inds]))

    left_lane_inds = np.concatenate(left_lane_inds)
    right_lane_inds = np.concatenate(right_lane_inds)

    leftx, lefty = nonzerox[left_lane_inds], nonzeroy[left_lane_inds] 
    rightx, righty = nonzerox[right_lane_inds], nonzeroy[right_lane_inds]

    left_fit = np.polyfit(lefty, leftx, 2)
    right_fit = np.polyfit(righty, rightx, 2)
    
    return left_fit, right_fit

def draw_lane(original_img, warped_binary, left_fit, right_fit, Minv):
    """Draws the detected curved lane polygon back onto the original perspective."""
    h, w = original_img.shape[:2]
    ploty = np.linspace(0, h - 1, h)
    
    left_fitx = left_fit[0] * ploty**2 + left_fit[1] * ploty + left_fit[2]
    right_fitx = right_fit[0] * ploty**2 + right_fit[1] * ploty + right_fit[2]

    warp_zero = np.zeros_like(warped_binary).astype(np.uint8)
    color_warp = cv2.merge((warp_zero, warp_zero, warp_zero))

    pts_left = np.array([np.transpose(np.vstack([left_fitx, ploty]))])
    pts_right = np.array([np.flipud(np.transpose(np.vstack([right_fitx, ploty])))])
    pts = np.hstack((pts_left, pts_right))

    # Fill lane polygon green
    cv2.fillPoly(color_warp, np.int32([pts]), (0, 255, 0))

    # Inverse warp to original perspective
    newwarp = cv2.warpPerspective(color_warp, Minv, (w, h))
    return cv2.addWeighted(original_img, 1, newwarp, 0.3, 0)


image_path = r"C:\Users\Dell\Desktop\Soumye Chauhan 26-B3-39\3 (1).png"
image = cv2.imread(image_path)

if image is None:
    print(r"C:\Users\Dell\Desktop\Soumye Chauhan 26-B3-39\ 3 (1).png")
else:
    binary_img = pipeline(image)
    warped_img, Minv = warp(binary_img)
    left_fit, right_fit = fit_polynomial(warped_img)
    final_output = draw_lane(image, warped_img, left_fit, right_fit, Minv)

    
    cv2.imwrite("output_detected_lane.jpg", final_output)

    cv2.imshow("Original Image", image)
    cv2.imshow("Detected Curved Lane", final_output)
    cv2.waitKey(0)
    cv2.destroyAllWindows()