from utils import OlgasLibs
from patent import Patent
import time



global_local_path = "./data/"
#generate path to csv where data will be saved for given company
def path_to_csv(company):
    name_parsed = company.replace(" ","_")
    return global_local_path+name_parsed+".csv"


# #generate path to csv where download failure report will be saved for given company
def path_to_failed(company):
    name_parsed = company.replace(" ", "_")
    return global_local_path + "failed/failed-scraping-"+name_parsed + ".csv"


# get links from html page with list of patents (currently restricted to max 10 per page
def get_links(url):
    base_link = 'http://patft.uspto.gov'
    html = OlgasLibs.openHtml(url)
    tds = html.body.find_all("td", attrs={'valign': 'top'})
    linx = []
    for td in tds:
        a = td.a
        if a is None:
            continue
        else:
            link = a["href"]
            linx.append(base_link + link)

    return remove_duplicates(linx)

# remove duplicate links (on a couple of occasions this happened)
def remove_duplicates(list_with_duplicates):
    final_list = []
    for num in list_with_duplicates:
        if num not in final_list:
            final_list.append(num)
    return final_list

# get patent data from a patent specific page
# uses read_from_page to do html level work
def get_patent_data(link):
    link_page = OlgasLibs.openHtml(link)
    try:
        return read_from_page(link_page,link)
        #print("in progress")
    except Exception as ex:
        print("Error reading link: "+link)
        print("Giving it another try...")
        time.sleep(100)
        try:
            return read_from_page(link_page,link)
        except Exception as e:
            print(e)
            faulty_page_str = str(link_page)
            print("HTML:\n"+faulty_page_str)
            raise

# retrieves required patent attributesto from a patent's html page
# returns Patent object
def read_from_page(link_page,link):
    inventors = get_inventors(link_page)  # link_page.find_all('table',attrs={"width":"100%"})[2].tr.td.text.strip()
    current_us_class = get_current_class(link_page, "Current U.S. Class:")
    current_cpc_class = get_current_class(link_page, "Current CPC Class:")
    current_international_class = get_current_class(link_page, "Current International Class:")
    current_assignee = get_assignee(link_page)
    filed = get_filed(link_page)
    patent_number = link_page.find_all('table', attrs={"width": "100%"})[1].find('td', attrs={"align": "right","width": "50%"}).text
    patent_title = link_page.find_all('font', attrs={"size": "+1"})[0].text
    return Patent(patent_number, filed, inventors, current_us_class, current_cpc_class, current_international_class, current_assignee,
                  patent_title, link)

# retrieves patent list of patent's inventors from patent's html page
def get_inventors(html):
    ths = html.find_all('th', attrs={"scope":"row","align": "left", "valign": "top", "width": "10%"})
    inventors = ""
    for th in ths:
        if (th.text.strip()=="Inventors:"):
            inv = th.parent.td.text.strip()
            inventors = inv
            break
        else: continue
    return inventors


# retrieves patent's assignee from patent's html page
def get_assignee(html):
    #<th scope="row" valign="top" align="left" width="10%">Inventors:</th>
    ths = html.find_all('th', attrs={"scope":"row","align": "left", "valign": "top", "width": "10%"})
    inventors = ""
    for th in ths:
        if (th.text.strip()=="Assignee:"):
            inv = th.parent.td.text.strip()
            inventors = inv
            break
        else: continue
    return inventors

# retrieves patent's filed info from patent's html page
def get_filed(html):
    ths = html.find_all('th', attrs={"align": "left", "scope": "row", "valign": "top", "width": "10%"})
    filed = ""
    for th in ths:
        if (th.text.strip()=="Filed:"):
            filed_date = th.parent.td.b.text
            filed = filed_date
            break
        else: continue
    return filed

# retrieves patent's current class from patent's html page
def get_current_class(html,class_name):

    try:
        bs = html.find_all('b')
        current_class = ""
        for b in bs:
            if (b.text.strip()==class_name):
                cc = b.parent.parent.find('td',attrs={ "align":"right","valign":"top","width":"70%"}).text
                current_class = cc
                break
            else: continue
        return current_class

    except Exception as ex:
        print("Could not get"+class_name)
        print(format(ex))
        "None"

# generates patent search page url
def generate_page_url(company,page_number,result_per_page=10):
    url_encoded = company.replace(" ","+")
    return "http://patft.uspto.gov/netacgi/nph-Parser?Sect1=PTO2&Sect2=HITOFF&p="+str(page_number)+"&u=%2Fnetahtml%2FPTO%2Fsearch-bool.html&r=0&f=S&l="+str(result_per_page)+"&TERM1="+url_encoded+"&FIELD1=ASNM&co1=AND&TERM2=&FIELD2=&d=PTXT"

# tuples of company names with nmumber of pages with patents available
patent_urls_pages_with_number_of_pages  = [
    ("tencent",132),
    ("facebook",262),
    ("apple",1944),
    ("amazon",881),
    ("google",1851),
    ("International Business Machines",12315),
    ("intel",3765),
    ("samsung",10774),
    ("hon hai precision",1854),
    ("oracle",854),
    ("microsoft",3909)

]


# top level function which does all the work for a given company by using other functions
def scrap_patents(company,number_of_pages, start_page=1):
    pages_count = start_page - 1
    patents = []
    try:
       while(number_of_pages>=pages_count):

                pages_count = pages_count + 1
                link = generate_page_url(company,pages_count)
                links_to_patent_pages = get_links(link)
                start_time = time.time()
                for patent_page_link in links_to_patent_pages:

                    try:
                        patent = get_patent_data(patent_page_link)
                        patents.append(patent)

                    except Exception :
                        print("exception occurred, skipping problematic patend page: "+patent_page_link)
                        try:
                            OlgasLibs.append_to_csv_file(path_to_failed(company), [{"page": pages_count, "link": patent_page_link}],["page", "link"])
                        except Exception as e:
                            print("failed to save failed link to csv")
                            print(e)
                            print("arhhh...fuck it! going for next link to process")

                            print("error:" + e)
                    except ConnectionResetError:
                            print("error:\n" + e)
                            raise
                if (pages_count % 1 == 0):
                    if len(patents):
                        end_time = time.time()
                        time_spent = end_time - start_time
                        time_per_page = int(round(time_spent / 10))
                        print("Average time per link: "+str(time_per_page)+" seconds")
                        OlgasLibs.append_objects_to_csv_file(path_to_csv(company), patents)
                        patents = []
                    #else : patents = []
       if len(patents):OlgasLibs.append_objects_to_csv_file(path_to_csv(company), patents)
       # return patents
    except :
            print("exiting...")
            raise

# get the work done for each company
for tuple in patent_urls_pages_with_number_of_pages:
    company,num_of_pages = tuple
    scrap_patents(company,num_of_pages)
    print("saved data for "+company)
print("All done")