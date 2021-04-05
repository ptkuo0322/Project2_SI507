#################################
##### Name:Po-Tsun Kuo      #####
##### Uniqname:ptkuo        #####
#################################

from bs4 import BeautifulSoup
import requests
import json
import secrets # file that contains your API key
import time
import ast


######## self-defined functions ########

def load_cache():
    ''' To read the dictionary from the cache file if it exists, if not, create
    an empty dictionary

    Parameters
    ----------
    None

    Returns
    -------
    dict
        information store in the cache, which is a dictionary
    '''
    try:
        cache_file = open(CACHE_FILE_NAME, 'r')
        cache_file_contents = cache_file.read()
        cache = json.loads(cache_file_contents)
        cache_file.close()
    except:
        cache = {}
    return cache


def save_cache(cache):
    ''' 
    Parameters
    ----------
    cache
        a dictionary that contains the information

    Returns
    -------
    None
        
    '''
    cache_file = open(CACHE_FILE_NAME, 'w')
    contents_to_write = json.dumps(cache)
    cache_file.write(contents_to_write)
    cache_file.close()


def make_url_request_using_cache(url, cache):
    ''' Make a dictionary that maps information from url

    Parameters
    ----------
    url
        the url link that for both chenking the keys in dictionary and 
        sending the request to the website
    cache
        the dictionary that store the information for future use

    Returns
    -------
    string
        the value of specific key-value pair in the cache dictionary
        
    '''
    if (url in cache.keys()): # the url is our unique key
        print("Using cache")
        return cache[url]
    else:
        print("Fetching")
        time.sleep(1)
        response = requests.get(url)
        cache[url] = response.text
        save_cache(cache)
        return cache[url]

def printPlaceNear(Aclass):
    '''Print out the Places near thespecific place.
    
    Parameters
    ----------
    Aclass: class
        a class return from get_nearby_places
    
    Returns
    -------
    none
    '''
    print("----------------------------------")
    print(f"Places near {Aclass.name}")
    print("----------------------------------")

def printListOfNationalSites(Astring):
    '''Print out the list of national sites.

    Parameters
    ----------
    Astring: string
        a string input by the user
    
    Returns
    -------
    none
    '''
    print("----------------------------------")
    print(f"List of national sites in {Astring}")
    print("----------------------------------")

def printForStepFive(Adict):
    '''Print out the information of nearby places of specific sites in specific format.
    
    
    Parameters
    ----------
    Adict: dictionary
        a dictionary return from get_nearby_places
    
    Returns
    -------
    none

    '''
    for ele in result['searchResults']:
        if ele["fields"]["group_sic_code_name_ext"] == "" and ele['fields']['address']=="" and ele['fields']['city']== "":
            print('-' + ele['name'] +'(no cateogry): ' + 'no address' + ', ' + 'no city') 
        elif ele["fields"]["group_sic_code_name_ext"] == "" and ele['fields']['address']=="" and ele['fields']['city']!= "":
            print( "-" + ele['name'] +'(no cateogry): ' + 'no address' + ", " + ele['fields']['city'] )
        elif ele["fields"]["group_sic_code_name_ext"] == "" and ele['fields']['address']!="" and ele['fields']['city']!= "":
            print( "-" + ele['name'] +'(no cateogry): ' + ele['fields']['address'] + ", " + ele['fields']['city'] )
        else:
            print( '-' + ele['name'] + ' (' + ele['fields']['group_sic_code_name_ext'] + ")" + ': '  + ele['fields']['address'] + ", " + ele['fields']['city'])    
    
#### setting up parameters and API key and other stuff for use
CACHE_DICT = {}
CACHE_FILE_NAME = 'cacheSITE_Scraping.json'
BASEURL = "https://www.nps.gov"
CACHE_DICT = load_cache()
stateSiteResult = []
new_list = []
api_key = secrets.API_KEY



##### the following functions are initially defined by the instructors/GSIs

class NationalSite:
    '''a national site

    Instance Attributes
    -------------------
    category: string
        the category of a national site (e.g. 'National Park', '')
        some sites have blank category.
    
    name: string
        the name of a national site (e.g. 'Isle Royale')

    address: string
        the city and state of a national site (e.g. 'Houghton, MI')

    zipcode: string
        the zip-code of a national site (e.g. '49931', '82190-0168')

    phone: string
        the phone of a national site (e.g. '(616) 319-7906', '307-344-7381')
    '''
    def __init__(self, category, name, address, zipcode, phone):
        self.category = category
        self.name = name
        self.address = address
        self.zipcode = zipcode
        self.phone = phone
    def info(self):
        return self.name + " (" + self.category + "): " + self.address + " "+ self.zipcode
        
    


def build_state_url_dict():
    ''' Make a dictionary that maps state name to state page url from "https://www.nps.gov"

    Parameters
    ----------
    None

    Returns
    -------
    dict
        key is a state name and value is the url
        e.g. {'michigan':'https://www.nps.gov/state/mi/index.htm', ...}
    '''
    UrlDict = {}
    response = make_url_request_using_cache(BASEURL,CACHE_DICT)
    soup = BeautifulSoup(response, "html.parser")
    soup1 = soup.find(class_="dropdown-menu SearchBar-keywordSearch")
    for ele in soup1.find_all("a"):
        UrlDict[ele.text.lower()] = BASEURL + "/state/" + ele.text.lower()[0:2]+ "/index.htm"
    return UrlDict
    

def get_site_instance(site_url):
    '''Make an instances from a national site URL.
    
    Parameters
    ----------
    site_url: string
        The URL for a national site page in nps.gov
    
    Returns
    -------
    instance
        a national site instance
    '''
    response = make_url_request_using_cache(site_url,CACHE_DICT)
    soup = BeautifulSoup(response, "html.parser")
    ### find the attribute for class
    soup_address0 = soup.find("span", itemprop="addressLocality").string.strip()
    soup_address1 = soup.find("span", itemprop="addressRegion").string.strip()
    soup_address = soup_address0 + ", " + soup_address1
    soup_phone = soup.find("span", itemprop="telephone").string.strip()
    soup_zipcode = soup.find("span", itemprop="postalCode").string.strip()
    soup_name = soup.find("a",class_="Hero-title").string.strip()
    soup_category = soup.find("span", class_="Hero-designation").string.strip()
    a = NationalSite(soup_category,soup_name,soup_address, soup_zipcode, soup_phone)
    
    return a




def get_sites_for_state(state_url):
    '''Make a list of national site instances from a state URL.
    
    Parameters
    ----------
    state_url: string
        The URL for a state page in nps.gov
    
    Returns
    -------
    list
        a list of national site instances
    '''
    response = requests.get(state_url)
    soup = BeautifulSoup(response.text, "html.parser")
    soup_parent = soup.find("ul", id = "list_parks")
    soup_h3 = soup_parent.find_all('li', recursive=False)
    site_list = []
    sites_list = []
    for ele in soup_h3:
        soup_link_tag = ele.find("a")['href']
        site_list.append(soup_link_tag)
    for ele in site_list:
        url = 'https://www.nps.gov' + ele +'index.htm'
        #print(url)
        sites_list.append(get_site_instance(url))
    return sites_list
    


def get_nearby_places(site_object):
    '''Obtain API data from MapQuest API.
    
    Parameters
    ----------
    site_object: object
        an instance of a national site
    
    Returns
    -------
    dict
        a converted API return from MapQuest API
    '''
    baseurl = "http://www.mapquestapi.com/search/v2/radius?" 
    url = f"{baseurl}key={api_key}&origin={site_object.zipcode}&radius=10&maxMatches=10&ambiguities=ignore&outFormat=json"
    response = make_url_request_using_cache(url,CACHE_DICT)
    res = json.loads(response)
    return res



if __name__ == "__main__":

    
    query = input("Enter a state name (e.g. Michigan, michigan) or 'exit' ")
    query = query.lower()
    if query == "exit":
        quit()
    else:
        generalDict = build_state_url_dict()
        while True:
            if query not in generalDict.keys():
                print("[Error] Enter the Proper state name, please")
                query = input("Enter a state name (e.g. Michigan, michigan) or 'exit' ")
                query = query.lower()
            else:
                break
    LinkforSite = generalDict[query]
    result = get_sites_for_state(LinkforSite)
    printListOfNationalSites(query)
    for i in range(len(result)):
        new_list.append(result[i])
        print("[" + str(i+1) + "] ", result[i].info() )

    while True:
        usr_input = input("Choose the number for detail search or 'exit', or 'back' ")
        if usr_input == "exit":
            quit()
        elif usr_input == "back":
            query = input("Enter a state name (e.g. Michigan, michigan) or 'exit' ")
            generalDict = build_state_url_dict()
            while True:
                if query not in generalDict.keys():
                    print("[Error] Enter the Proper state name, please")
                    query = input("Enter a state name (e.g. Michigan, michigan) or 'exit' ")
                    query = query.lower()
                else:
                    break
            LinkforSite = generalDict[query]
            result = get_sites_for_state(LinkforSite)
            printListOfNationalSites(query)
            for i in range(len(result)):
                new_list.append(result[i])
                print("[" + str(i+1) + "] ", result[i].info() )
    
        elif usr_input.isnumeric() and int(usr_input) in range(len(new_list)+1):
            a = new_list[int(usr_input)-1]
            printPlaceNear(a)
            result = get_nearby_places(a)
            printForStepFive(result)
        else:
            print("[Error] Invalid input")
                
