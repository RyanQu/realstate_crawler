# Realstate Crawler

Author: RyQ

Date: 10/02/2018

For academical using, craw data from a real state website in NY.

## Functions

* **get\_html(url)**: Send http requests
* **find\_link(html)**: Find more links to crawl on the pages. Verify for the blocked.
* **craw\_main(f, html)**: Main page crawler.
* **craw\_sales(f, sales_link)**: Sales page crawler
* **craw\_neighbors(f, neighbors_link)**: Neignbors page crawler
* **get\_url(path)**: Get urls in seperate files and output in one file.
* **read\_url(file)**: Get urls from a single file.
* **rename\_saleslink()**: Rename the downloaded webpages which are illegal  to request by webservice.
* **main()**: Main entrance.

## Initialize

1. Claim the hashbang at the beginning.
2. Change the all the file paths.
3. Run `get_url(path)` or `read_url(file)` to read the links appropriately.
4. Visit the object website by any browser and get your unique http request header.
5. Install python packages `lxml` and `bs4`.
6. Reset the loop in `main` function.
7. Use `python crawler_mac.py` command in Terminal to start.
8. Enjoy your life.

## Runtime notes

* Some `os` command may be not able for Windows.
* If the crawler is blocked, we need to download all the webpages to local and visit by localhost. I used some Chinese magic called "AnJianJingLing".
* Breakpoint is important, since it may stop frequently while nearly half of links are empty which means sold.