# UGV-DTU Software Department – Final Round Submission

Hi! This is my repository for the UGV-DTU Software Department departmental test. I'm a first-year BTech student and this is my first time working on a robotics/computer vision project, so this repo is basically me learning Python, OpenCV, and GitHub by actually building things instead of just reading tutorials.

I'm submitting tasks 1 to 4. I'm attaching this README to keep track of what I did, what broke, and what I learnt along the way (as asked in the problem statement).

---

## Tools & Libraries Used

- **Python 3** – the only language I know so far, and it's great for this
- **OpenCV (cv2)** – for reading, processing, and drawing on images
- **NumPy** – for array/matrix operations that OpenCV images are built on
- **Git & GitHub** – for version control and submitting my code
- **Matplotlib** (occasionally) – just to preview images while debugging

---
 ```

Each task folder has a main Python file plus `input/` (given images) and `output/` (my generated/marked images), as required.

---

## Task-wise Summary

### Task 1 – GitHub Basics
Set up my first proper GitHub repo and learnt the basic Git workflow:
- `git init`, `git add`, `git commit`, `git push`, `git pull`, `git clone`
- Recovering old versions using `git log` + `git checkout` / `git revert`
- Basic Linux commands (`mkdir`, `mv`, `rm`, `touch`, `cd`, `ls`) to create/delete/rename files from the command line

### Task 2 – Lane Detection
**Goal:** Detect the two lane boundaries on a road image and highlight the drivable area between them.

**My approach:**
1. Convert the image to grayscale, then apply Gaussian blur to reduce noise.
2. Use Canny edge detection to find edges in the image.
3. Apply a region-of-interest (ROI) mask so I only look at the road area (ignoring sky/surroundings).
4. Use Hough Line Transform (`cv2.HoughLinesP`) to detect straight line segments and separate them into left lane and right lane based on their slope.
5. Fit/average the lines and draw them on the original image.
6. Fill the polygon between the two lane lines with a semi-transparent overlay to mark the drivable area.
7. Save the final marked image to the `output/` folder.

**Problems faced:** Getting a proper ROI mask took a few tries — I first hardcoded a triangle, but it didn't fit all images well. Also had trouble separating left vs right lines when slope was near zero, had to add a threshold to filter out near-horizontal lines.

### Task 3 – Obstacle & Pothole Detection
**Goal:** Detect obstacles/potholes (white circular blobs) and mark them with bounding boxes + coordinates.

**My approach:**
1. Convert image to grayscale and apply thresholding to isolate bright/white blobs.
2. Use morphological operations (`cv2.erode`/`cv2.dilate`) to clean up noise in the thresholded image.
3. Use `cv2.findContours` to detect blob contours.
4. Filter contours by area/shape (roughly circular, reasonable size) so I don't pick up random noise.
5. Draw a rectangular bounding box (`cv2.boundingRect`) around each detected blob and label it with its pixel coordinates.
6. Print/display the total count of obstacles and potholes found in the image.
7. Save the output image with all boxes and labels drawn.

**Problems faced:** Choosing the right threshold value was tricky since lighting varies across images — used `cv2.THRESH_OTSU` to make thresholding more automatic instead of a fixed value. Small noise blobs were getting detected too, so I added a minimum contour area filter.

### Task 4 – Aerial Path Planning
**Goal:** Using the aerial images, plan a safe path from start to goal that completes one loop, avoiding obstacles/potholes and staying on the road.

**My approach:**
1. Reused/adapted the lane and obstacle detection logic from Task 2 & 3 to figure out the drivable area and obstacle locations in the aerial image.
2. Built a simple occupancy grid — marked road area as free space and obstacles/potholes (+ some safety margin around them) as blocked space.
3. Implemented a basic path-planning algorithm (checkpoint-based approach: manually/programmatically placed a sequence of waypoints along the track, then checked each segment against the occupancy grid to make sure it doesn't cross an obstacle or leave the road).
4. Connected the waypoints to draw a continuous safe path completing one loop of the track.
5. Drew the final path on the aerial image and saved it as output.

**Problems faced:** I initially tried to read about A* and RRT*, but since it was my first time implementing a search algorithm, I went with the simpler checkpoint method mentioned in the problem statement to get a working solution first. I want to try A* properly as a next improvement.

---

## Daily Log

> Updating this every day as I work through the tasks.

**Day 1 (24/08/26)**
- What I did: learning about basic git commands and how to link codes to my repository
- Problems faced: not able to create a repository properly  

**Day 2 (25/08/26)**
- What I did: Understanding basic concepts about OpenCv and how to use it in python

**Day 3 (26/08/26)**
- What I did: writing syntax to solve Task 2
- Problems Faced: Getting a proper ROI mask took a few tries — I first hardcoded a triangle, but it didn't fit all images well. Also had trouble separating left vs right line

**Day 4 (27/08/26)**
- What I did: writing syntax to solve task 3, learning about RRT* and A*
- Problems Faced: Choosing the right threshold value was tricky since lighting varies across images — used `cv2.THRESH_OTSU` to make thresholding more automatic instead of a fixed value. Small noise blobs were getting detected too, so I added a minimum contour area filter.

**Day 5 (28/08/26)**
- What I did: learning about setting up Ubuntu and dual boot it
- Problems Faced: after restarting every time my GNU GRUB opened as some file got corrupted or deleted

**Day 6 (29/08/26)**
- What I did: writing syntax to solve task 4
- Problems faced: but since it was my first time implementing a search algorithm, I went with the simpler checkpoint method mentioned in the problem statement to get a working solution first. I want to try A* properly as a next improvement.

---


## Final Notes

This was my first real hands-on project with computer vision, and honestly a lot of it was trial and error — reading OpenCV docs, testing on sample images, and fixing things when they didn't work. My solutions aren't perfect, but I focused on understanding the approach and building something that actually works, as suggested in the problem statement. 
