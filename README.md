# Manga_Scraper

Hello! Welcome to my manga scraper. I made this project because I was interested in learning python and building a web scraper, and I decided to scrape something that
I was actually interested in rather than a generic stock information scraper. This scraper will automatically scrape the entirety of any individual manga from the popular
online manga site www.mangapanda.com when given the http address of the manga's home page. I made a single threaded model as well as a multi threaded model, and I encourage 
anyone interested to take this code apart and see how it works or to improve upon it. The multi threaded model doesnt have much in the way of a UI, but it will tell you what 
its dowloading as it happens at least.

To run this:
- `pip3 install -r requirements.txt`

- If you want to download all images from http://www.mangapanda.com/high-school-of-the-dead for example:
    ```
    python3 Manga_Scraper.py http://www.mangapanda.com/high-school-of-the-dead
    ```
    A new folder `www.mangapanda.com` will be created automatically that contains a sub folder `high-school-of-the-dead`. This folder will contain subfolders labeled according
    to chapter numbers for each individual chapter of the manga, and each subfolder will contain the images of the manga chapter. Downloading additional manga will create separate
    folders underneath the `www.mangapanda.com` folder with the same folder and file structure as the previous example.
    
- The above command probably needs to be run in the same folder that the scraper file is located in. I havent looked into how to publish or install this tool yet.
