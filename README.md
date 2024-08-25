# Mini Projects Repository

Welcome to the Mini Projects Repository! This repository contains a collection of small projects that demonstrate various techniques and solutions in programming.

## Projects

### 1. Question Detection
This project focuses on detecting and classifying questions from a given text. It utilizes natural language processing techniques to identify question patterns and extract relevant information.

### 2. ngspice Output Analysis
This project involves analyzing the output from ngspice simulations using Python. It includes:
- Generating plots to visualize the data
- Calculating important timing parameters such as tphl, tplh, and tp

### 3. Web Scraping
This project demonstrates how to scrape data from websites. Some examples include:
- Amazon: Extracting product information and reviews
- Kentucky: Scraping specific data related to Kentucky (details of the site would be specified)
- #### 🚀 Judicial Decisions in Arabic
 ##### overview
##### This repository contains code to scrape judicial decisions from an Arabic website where clicking on the next page button isn't straightforward. The project leverages Python, Bash, Selenium, and computer vision techniques to automate this process.
 #### 📷 How It Works
1. **Navigate the Web Page**: Selenium is used to open the target web page.
2. **Take a Screenshot**: A screenshot of the current page is taken using a Bash script.
3. **Detect Next Page Button**: Using OpenCV, the script analyzes the screenshot to find the coordinates of the "Next Page" button.
4. **Simulate Click**: xdotool is employed to simulate a mouse click on the detected coordinates, navigating to the next page.

## Learn English with Ctrl+E
This project automates the download of all posts from an account that teaches English through movie clips.

#### Features
- Downloads all posts. If your internet disconnects and the code stops, simply run it again. The download will resume from where it left off.
- The script `randomPlay.sh` can be moved to `/usr/bin` and made executable using `chmod +x randomPlay.sh`.
- Create a keyboard shortcut (e.g., Ctrl+E) in your system settings (Settings -> Keyboard -> View and Customize Shortcuts -> Customize Shortcuts) and set the command to `"randomPlay.sh"`.

#### Usage
When you press `Ctrl+E`, a video will open using VLC, allowing you to learn English in a fun and interactive way.
