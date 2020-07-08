import requests
import os
from tqdm import tqdm
from bs4 import BeautifulSoup as bs
from urllib.parse import urljoin, urlparse


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

    # Grab the cover image
    cover_container = soup.find(id="mangaimg")
    if cover_container:
        cover_img = cover_container.find("img")
        cover_url = cover_img.attrs.get("src")
        cover_url = urljoin(url, cover_url)
        # go ahead and download the cover image
        r = urlparse(url)
        path = r.netloc + "/" + url.split("/")[-1]
        download(cover_url, path, "cover")

    # get the chapter listings table
    chapter_table = soup.find(id="listing")



    for a_tag in tqdm(chapter_table.find_all("a"), "Extracting Chapters"):

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

def get_all_images(url):
    """
    Returns all image URLs on a single `url`
    """
    # url list that will be returned
    urls = []

    # beautifil soup variable
    soup = bs(requests.get(url).content, "html.parser")
    
    # get the pageMenu container
    menu = soup.find(id="pageMenu")
    
    # calculate the number of images
    num_images = 5 # len(menu.contents) // 2

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
    for img_page in tqdm(img_page_urls, f"Extracting {url} : "):

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

        # finally, if the url is valid
        if is_valid(img_url):
            urls.append(img_url)

    return urls

def download(url, pathname, num):
    """
    Downloads a file given an URL and puts it in the folder `pathname`
    """
    # if path doesn't exist, make that path dir
    if not os.path.isdir(pathname):
        os.makedirs(pathname)
    # download the body of response by chunk, not immediately
    response = requests.get(url, stream=True)

    # get the total file size
    file_size = int(response.headers.get("Content-Length", 0))

    # get the file name
    filename = os.path.join(pathname, num + ".jpg")

    # progress bar, changing the unit to bytes instead of iteration (default by tqdm)
    progress = tqdm(response.iter_content(1024), f"Downloading {filename}", total=file_size, unit="B", unit_scale=True, unit_divisor=1024)
    with open(filename, "wb") as f:
        for data in progress:
            # write data read to the file
            f.write(data)
            # update the progress bar manually
            progress.update(len(data))


def main(url, path):
    # get all images

    # grab all of the chapter urls then iterate
    chapters = get_all_chapters(url)
    for chapter in chapters:

        # customize the path for each chapter url
        img_path = path + "/" + chapter.split("/")[-1]
        # counter for the image's page number
        i = 1
        
        # for each chapter, grab all of the image urls then iterate
        imgs = get_all_images(chapter)
        for img in imgs:

            # download each image
            download(img, img_path, (str)(i))
            # update counter
            i = i + 1
    


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="This script downloads all images from a web page")
    parser.add_argument("url", help="The URL of the web page you want to download images")
    parser.add_argument("-p", "--path", help="The Directory you want to store your images, default is the domain of URL passed")
    
    args = parser.parse_args()
    url = args.url
    path = args.path

    if not path:
        # if path isn't specified, use the domain name of that url as the folder name
        r = urlparse(url)
        path = r.netloc + "/" + url.split("/")[-1]
    
    main(url, path)