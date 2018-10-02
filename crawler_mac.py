#coding=utf-8
import requests
import re
import time
import random
import os
from bs4 import BeautifulSoup

# Start a new session every time to keep the cache update in runtime.
s = requests.Session()

def get_html(url):
    '''Send http request
    Args:
        url: the web url need to fetch
    Return:
        html: the webpage
    '''

    # Sometimes time gap may be needed between each request
    # time.sleep(5+random.random()*5) 
    
    # Http header, copy cookie at start 
    head={'copy your header here'}
    html = s.get(url,headers=head).text
    return html

def find_link(html):
    '''Get related links
    Find the needed links on the main page, judge whether blocked.
    Args:
        html: webpage returned by get_html()
    Return:
        links: needed links
    '''
    # Some websites have auto-block system, judge it by identifying special strings
    if re.search(r'distilIdentificationBlock',html):
        print "Error! Blocked!"
        return 0, 0
    else:
        sales_link = re.search(r'nearbyDiv.load\(Utils.AppPath(.*?),',html)
        #Some webpages don't have such links
        if not sales_link: 
            print "Error! Invalid!"
            return 0,0
        sales_link = "http://www.mlsli.com"+str(sales_link.group(1))[4:-1]
        
        neighbors_link = re.search(r'https:\/\/www.rdesk.com\/(.*?);',html)
        neighbors_link = str(neighbors_link.group())[:-2]
        print "Success"
    
    return sales_link, neighbors_link

def craw_main(f, html):
    '''Craw the main page
    Get the information on the main page and output to file.
    Args:
        f: output stream
        html: webpage returned by get_html()
    Output: 
        Write info to file
    Raise:
        IndexError: some tag organized differently.
    '''
    street = re.search(r'full-address.*inline">(.*?),',html)
    street =  str(street.group(1))
    soup = BeautifulSoup(html,"lxml")
    city = soup.select('span[itemprop="addressLocality"]')[0].string.encode('utf-8')
    state = soup.select('span[itemprop="addressRegion"]')[0].string.encode('utf-8')
    postcode = soup.select('span[itemprop="postalCode"]')[0].string.encode('utf-8')
    status = soup.select('span[class="ld-status"]')[0].select('span')[0].string.encode('utf-8')
    try:
        price = soup.select('span[class="price"]')[0].string.encode('utf-8')
    except:
        price = soup.select('span[class="price"]')[0].select('span')[0].string.encode('utf-8')

    bed_bath = soup.select('div[class="bed-baths"]')[0].text.encode('utf-8')
    MLS_num = soup.select('div[class="listing-number"]')[0].text.encode('utf-8')
    # Some webpages don't have summary
    if soup.select('div[class="summary-remarks"]'):
        summary = soup.select('div[class="summary-remarks"]')[0].text.encode('utf-8')
    else:
        summary = ""
    
    basic_info = [street, city, state, postcode, status, price, bed_bath, MLS_num, summary]

    _list_summary = soup.select('div[class="summary-additional details-info"]')[0].select('div')
    list_summary = []
    for item in _list_summary:
        label = item.text.encode('utf-8').replace("\n","").split(':')
        if label[0]:
            label[1] = label[1].lstrip()
            list_summary.append(label)

    _list_info = soup.select('table[class="details-info-table1"]')[0].select('td')
    list_info = []
    for item in _list_info:
        label = item.text.encode('utf-8').replace("\n","").replace("\r","").replace("\t","").split(':')
        if label[0]:
            label[1] = label[1].lstrip()
            list_info.append(label)
    
    _room_info = soup.select('div[id="listingdetail-roominfo"]')[0].select('div[class="details-3-per-row details-text-data"]')
    room_info = []
    for item in _room_info:
        label = item.text.encode('utf-8').replace("\n","").replace("\r","").replace("\t","").split(':')
        if label[0]:
            label[1] = label[1].lstrip()
            room_info.append(label)

    _int_info = soup.select('div[id="listingdetail-interiorfeatures1"]')[0].select('div[class="details-3-per-row details-text-data"]')
    int_info = []
    for item in _int_info:
        label = item.text.encode('utf-8').replace("\n","").replace("\r","").replace("\t","").split(':')
        if label[0]:
            label[1] = label[1].lstrip()
            int_info.append(label)
    
    _ext_info = soup.select('div[id="listingdetail-exteriorfeatures"]')[2].select('div[class="details-3-per-row details-text-data"]')
    ext_info = []
    for item in _ext_info:
        label = item.text.encode('utf-8').replace("\n","").replace("\r","").replace("\t","").split(':')
        if label[0]:
            label[1] = label[1].lstrip()
            ext_info.append(label)
    
    _fin_info = soup.select('div[id="listingdetail-financial"]')[0].select('div[class="details-3-per-row details-text-data"]')
    fin_info = []
    for item in _fin_info:
        label = item.text.encode('utf-8').replace("\n","").replace("\r","").replace("\t","").split(':')
        if label[0]:
            label[1] = label[1].lstrip()
            fin_info.append(label)
    
    _other_info = soup.select('div[id="listingdetail-financial"]')[1].select('div[class="details-1-per-row details-text-data"]')
    other_info = []
    for item in _other_info:
        label = item.text.encode('utf-8').replace("\n","").replace("\r","").replace("\t","")
        sp = label.index(":")
        label = [label[:sp+1],label[sp+1:]]
        if label[0]:
            label[1] = label[1].lstrip()
            other_info.append(label)
     
    print >> f, "Basic Info:\n", basic_info, "\n"
    print >> f, "Listing Summary:\n", list_summary, "\n"
    print >> f, "Listing Information:\n", list_info, "\n"
    print >> f, "Room Information:\n", room_info, "\n"
    print >> f, "Interior Features / Utilities:\n", int_info, "\n"
    print >> f, "Exterior / Lot Features:\n", ext_info, "\n"
    print >> f, "Financial Considerations:\n", fin_info, "\n"
    print >> f, "Other:\n", other_info, "\n"

def craw_sales(f, sales_link):
    '''Craw the sales page
    Get the information on the sales page and output to file.
    Some website have block system, may use some auto-operate software to download the html files then crawl the local webpages.
    Args:
        f: output stream
        sales_link: needed link returned by find_link
    Output: 
        Write info to file
    Raise:
        IndexError: some tag organized differently.
    '''
    print "Getting Sales"
    # Overwrite sales_link, crawl local downloaded webpages.
    sales_link = "http://localhost/saleslink/"+sales_link[-9:]+".html"
    print sales_link
    html = get_html(sales_link)
    # time.sleep(25+random.random()*5)
    soup = BeautifulSoup(html,"lxml")
    tables = soup.select('table[class="price-history-tbl"]')
    
    _sales_thead = tables[0].select('thead th')
    sales_thead =[]
    for item in _sales_thead:
        label = item.text.encode('utf-8').replace("\n","").replace("\r","").replace("\t","")
        sales_thead.append(label)
    sales_thead[0] = '#'
    _sales_table = tables[0].select('tbody tr')
    sales_table = []
    for row in _sales_table:
        _trow = row.select('td')
        trow = []
        for item in _trow:
            label = item.text.encode('utf-8').replace("\n","").replace("\r","").replace("\t","").strip().lstrip()
            trow.append(label)
        sales_table.append(trow)
    print "Get sales table"

    _price_thead = tables[1].select('thead th')
    price_thead =[]
    for item in _price_thead:
        label = item.text.encode('utf-8').replace("\n","").replace("\r","").replace("\t","")
        price_thead.append(label)
    _price_table = tables[1].select('tbody tr')
    price_table = []
    for row in _price_table:
        _trow = row.select('td')
        trow = []
        for item in _trow:
            label = item.text.encode('utf-8').replace("\n","").replace("\r","").replace("\t","").replace("\xc2\xa0","").replace(" ","").strip().lstrip()
            trow.append(label)
        price_table.append(trow)
    print "Get price table"

    tables = soup.select('table[class="price-history-tbl property-tax-history-tbl"]')[0]
    _tax_thead = tables.select('thead th')
    tax_thead =[]
    for item in _tax_thead:
        label = item.text.encode('utf-8').replace("\n","").replace("\r","").replace("\t","")
        tax_thead.append(label)
    _tax_table = tables.select('tbody tr')
    tax_table = []
    for row in _tax_table:
        _trow = row.select('td')
        trow = []
        for item in _trow:
            label = item.text.encode('utf-8').replace("\n","").replace("\r","").replace("\t","").replace("\xc2\xa0","").replace(" ","").strip().lstrip()
            trow.append(label)
        tax_table.append(trow)
    print "Get tax table"
    
    print >> f, "Nearby Recent Sales:\n", sales_thead, "\n", sales_table, "\n"
    print >> f, "Price History:\n", price_thead, "\n", price_table, "\n"
    print >> f, "Tax History:\n", tax_thead, "\n", tax_table, "\n"

def craw_neighbors(f, neighbors_link):
    '''Craw the sales page
    Get the information on the neighbors page and output to file.
    This is an api page, so no blocked.
    Args:
        f: output stream
        neighbors_link: needed link returned by find_link
    Output: 
        Write info to file
    '''
    print "Getting Neighbors"
    # Re-construct neighbors_link to get different tabs data
    tab_name = ["HomeValues2","Demographics2", "Economy2", "SchoolsEducation", "Environment", "Commute"]
    sp = neighbors_link.index("ReportName=")
    neighbors_link1 = neighbors_link[:sp+11]
    neighbors_link2 = neighbors_link[sp+11:]
    sp = neighbors_link2.index("&")
    neighbors_link2 = neighbors_link2[sp:]

    for name in tab_name:
        neighbors_url = neighbors_link1+name+neighbors_link2
        html = get_html(neighbors_url)
        # time.sleep(2+random.random()*3)
        data = re.findall(r'.Data = \[(.*?)\];',html)
        # Descriptions show at the end of every row, hidden on webpages
        for item in data:
            _item = item.encode('utf-8')
            print >> f, name, ":\n", _item, "\n"
        print "Get tab "+str(tab_name.index(name))
        
def get_url(path):
    '''Get urls from seperate files
    At first the input was thousands of files, need to get all links in a list and output the links to a single file.
    Args:
        path: the path of files
    Returns:
        urls: list of urls
    '''
    files= os.listdir(path)
    urls = []  
    for file in files: 
        if not os.path.isdir(file):   
            f = open(path+"/"+file)
            iter_f = iter(f)
            i=0     # Only get the first 10 links, all the repeated links after 10.
            for line in iter_f:  
                urls.append(line.strip())  
                i=i+1
                if i>9: break
    print "Total urls: ", len(urls) 
    path = "Your url"
    f = open("urls.txt","w")
    for url in urls:
        print >> f, url
    f.close()

    return urls

def read_url(file):
    '''Get urls from single file
    Args:
        path: the path of single file
    Returns:
        urls: list of urls
    '''
    urls = []
    f = open(file,"r")
    iter_f = iter(f)
    for line in iter_f:  
        urls.append(line.strip())
    print "Total urls: ", len(urls) 
    return urls

def rename_saleslink():
    '''Rename the downloaded sales pages
    The downloaded filename format may be not able to request from localhost
    '''
    src = "Your path of downloaded sales pages"
    filelist = os.listdir(src)
    for i in filelist:
        if i[:4] == "http":
            h_id = re.search(r'listingid=(.*?) .htm',i).group(1)
            os.rename(src+i,src+h_id+".html")

def main():
    path = "Your url file"
    filelist = os.listdir(path)
    # Store the index of error pages 
    error = [655,755,1129,1393,1471,2181,2402,2527,2683,2887,2934,2958,3203]
    # Start from breakpoint
    for i in range(3204,len(filelist)):
        print i
        print filelist[i]
        # Request from local files
        url = "http://localhost/html/"+filelist[i]
        html = get_html(url)
        (sales_link, neighbors_link) = find_link(html)
        file = "data/"+str(i)+".txt"
        f = open(file,"w")
        print >> f, url
        print >> f, sales_link
        print >> f, neighbors_link
        craw_main(f, html)
        try:
            craw_sales(f, sales_link)
        except:
            print >> f, "No Sales Data!"
    
        try:
            craw_neighbors(f, neighbors_link)
        except:
            # Raise a weird alarm noise when error, if you leave the machine alone.
            os.system('say "Error!"')
        f.close()
        # time.sleep(120+random.random()*60)

main()