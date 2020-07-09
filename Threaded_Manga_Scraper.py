import os
import requests
from concurrent.futures import ThreadPoolExecutor
from threading import Thread
from queue import Queue
from bs4 import BeautifulSoup as bs
from urllib.parse import urljoin, urlparse

# global file path for images
path = ""

# number of threads to spawn
n_threads = 10

# thread-safe queue initialization
q = Queue()

def is_valid(url):
    """
    Checks whether `url` is a valid URL.
    """
    parsed = urlparse(url)
    return bool(parsed.netloc) and bool(parsed.scheme)


def get_all_chapters(url):
    """
    Returns all chapter URLs on a single manga panda series homepage and the cover image
    """
    # url list that will be returned
    urls = []

    #  create a bs object with the given url
    soup = bs(requests.get(url).content, "html.parser")

    # get the chapter listings table
    chapter_table = soup.find(id="listing")

    # grab every chapter url and append to urls to return
    for a_tag in chapter_table.find_all("a"):

        # get the href attr from the a tag
        chapter_url = a_tag.attrs.get("href")

        # make the URL absolute by joining domain with the URL that is just extracted
        chapter_url = urljoin(url, chapter_url)

        # remove URLs like '/hsts-pixel.gif?c=3.2.5'
        try:
            pos = chapter_url.index("?")
            chapter_url = chapter_url[:pos]
        except ValueError:
            pass

        # finally, if the url is valid
        if is_valid(chapter_url):
            urls.append(chapter_url)

    return urls

def get_chapter_images(url):
    """
    Returns all image URLs on a single manga chapter url
    """
    global q

    # beautifil soup variable
    soup = bs(requests.get(url).content, "html.parser")
    
    # get the pageMenu container
    menu = soup.find(id="pageMenu")
    
    # calculate the number of images
    num_images = len(menu.contents) // 2

    # build the image page urls to extract from and add to image_page_urls[]
    img_page_urls = []
    for x in range(num_images):

        # if 0 its just the chapter url, otherwise its /x+1
        if x == 0:
            page_url = url
        else:
            page_url = url + "/" + (str)(x+1)

        # if the url is valid add it to the list
        if is_valid(page_url):
            img_page_urls.append(page_url)

    # for every image page url get the image off of the page
    for img_page in img_page_urls:

        # make the soup object for the page
        img_page_soup = bs(requests.get(img_page).content, "html.parser")

        # get the image holder class
        img_holder = img_page_soup.find(id="imgholder")

        # get the image from the holder
        img = img_holder.find("img")

        # get the src from the img
        img_url = img.attrs.get("src")

        # make the URL absolute by joining domain with the URL that is just extracted
        img_url = urljoin(url, img_url)

        # remove URLs like '/hsts-pixel.gif?c=3.2.5'
        try:
            pos = img_url.index("?")
            img_url = img_url[:pos]
        except ValueError:
            pass

        # finally, if the url is valid add it to the global queue
        if is_valid(img_url):
            q.put(img_url)
            print(img_url)

def download():
    """
    Downloads a file given an URL and puts it in the folder `pathname`
    """
    global q
    global path

    while True:

        # get the url from the queue
        url = q.get()

        # parse the chapter from the url and add it to the path to create local path
        local_path = path + "/" + url.split("/")[-2]

        # if local_path doesn't exist, make the dir
        if not os.path.isdir(local_path):
            os.makedirs(local_path)
    
        # download the body of response by chunk, not immediately
        response = requests.get(url, stream=True)
    
        # get the total file size
        file_size = int(response.headers.get("Content-Length", 0))
    
        # get the file name
        filename = local_path + "/" + url.split("/")[-1]
    
        # download the file incrementally
        print(f"Downloading {filename} ...")
        with open(filename, "wb") as f:
            for data in response.iter_content(1024):
                # write data read to the file
                f.write(data)
        print(f"    Finished with {filename}")

        # we're done downloading the file
        q.task_done()

def main(url):

    # grab all of the chapter urls
    chapters = get_all_chapters(url)

    for chapter in chapters:
        print(chapter)

    # start the threads to get all of the image urls in the queue
    with ThreadPoolExecutor(max_workers=n_threads) as pool:
        pool.map(get_chapter_images, chapters)

    # start the threads to download all of the images off of the queue
    for t in range(n_threads):
        worker = Thread(target=download)
        # daemon thread means a thread that will end when the main thread ends
        worker.daemon = True
        worker.start()

    # wait until the queue is empty
    q.join()



if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="This script downloads all images from a web page")
    parser.add_argument("url", help="The URL of the web page you want to download images")

   # global path

    args = parser.parse_args()
    url = args.url
    
    r = urlparse(url)
    path = r.netloc + "/" + url.split("/")[-1]

    main(url)