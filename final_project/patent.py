from utils import OlgasLibs

class Patent:

    def __init__(self,patent_number,filed,inventors,current_us_class,current_cpc_class,current_international_class, current_assignee,patent_title, link):
        self.number = patent_number
        self.date = filed
        self.inventors = inventors
        self.us_class = current_us_class
        self.cpc_class = current_cpc_class
        self.intl_class = current_international_class
        self.current_assignee = current_assignee
        self.title = patent_title
        self.link = link
