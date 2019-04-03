# Webscrapper that downloads data from fanfiction.net.
# Serves for Natural Language Processing purposes.
# Necessary modules: mechanicalsoup,nltk,sklearn,json,time,pickle
# Note: the name of site is global variable


import mechanicalsoup
import time
import json
# import nltk
# import pickle
from timeit import default_timer as timer
import re
from unidecode import unidecode

SITE = "http://fanfiction.net"  # Default site to work on, tested.


class Scrapper:
    def __init__(self, site):
        """
        Webscrapper that extracts text data from fanfiction site.

        parameters
        ----------
        site : string
        the site from which the data are taken

        attributes
        ----------
        linksOnPage : list
        links to the fanfics

        downloaded : list
        list of all downloaded fanfics

        """
        self.site = site
        self.__browser = mechanicalsoup.StatefulBrowser(raise_on_404=True)
        self.response = self.__browser.open(self.site)
        self.linksOnPage = []
        self.linksToDownload = []

        with open("dict.txt", "a+") as f:  # file with history of downloads
            # f.close()
            pass

    def open(self, site):
        """ Opens the site """
        return self.__browser.open(site)

    def follow_link(self, follow_link):
        """ Follows the link passed as an input """
        self.__browser.follow_link(follow_link)
        return (self.__browser.get_url())

    def filtered_fan_fiction(self):
        """ Filters the fanficts looking for only the desired settings """
        URL = self.__browser.get_url()
        Filters = ('srt', 'lan', 'len', 'p')  # list of desired filters
        FilterValues = (3, 1, 0, 2)  # list of values for filters
        FilterSet = ''
        for i in range(len(Filters)):
            FilterSet += '&%s=%d' % (Filters[i], FilterValues[i])

        newURL = str(URL) + '?' + FilterSet
        return newURL

    @staticmethod
    def cleaning(soup):
        '''Function to cleaning html leftovers from soup.get_text '''
        splitted = soup.split('\n')
        result = splitted
        d = 0
        for n in range(len(splitted)):
            if splitted[n] == '});':
                p = n
                break
        for n in range(len(splitted)):
            if splitted[n] == '    function review_init() {':
                d = n
                result = splitted[p+3:d-2]
                break
        result = [frag.replace("\'", '') for frag in result]
        result = [frag.replace("\r", '') for frag in result]
        return result


    def preparing_links(self):
        """This module is tasked with finding all links to stories on a search
         page of fanfiction.net. It takes a ResultSet of URLs, extracted from
         StatefulBrowser, and runs a regular expression.

        To reduce calcultions, the module searches only for links to the last
         chapters of stories. Then it reconstructs links to the firsts.
         Yeah, it's faster that way."""

        all_links = self.__browser.links()
        all_links = all_links[1::2]
        self.linksOnPage = re.findall(r'/s/[0-9]+/[0-9]+/[-a-zA-Z0-9]+', str(all_links))

        return self.linksOnPage

    def download_list(self,ran_giv=2,pr_link=False,save_file=True): 
        """links and chapters are product of preparing_links function;
        ran_giv is a number of links that are going to be downloaded;
        or all links  use len(links);
        pr_link is a decision whether print links during downloading or not."""
        # self.__ran_giv = ran_giv
        links = self.linksToDownload
        data_sample = []

        for n in range(0,ran_giv):
            split = links[n].split('/')
            story_number = split[2]
            chapters = split[3]
            story_name = split[4]
            one_fan_fic = []
            for r in range(1, int(chapters)+1):
                download_link = self.site + '/s/' + story_number + '/{}/'.format(r) + story_name
                if pr_link:
                    print(download_link)
                # Using mechanicalsoup to get and clean a page.
                self.__browser.open(download_link)
                __soup = self.__browser.get_current_page()
                page = __soup.get_text()
                page = unidecode(page) # THE SAVIOR OF MY SANITY
                self.__cleaned = self.cleaning(page)
                one_fan_fic.append(self.__cleaned)

            data_sample.append(one_fan_fic)
            if save_file:
                with open (str(story_name) + '.txt','a') as k:
                        k.write(str(one_fan_fic))
                        # k.close()
                download_link = self.site + '/s/' + story_number + '/1/' + story_name
                with open ('dict.txt','a') as h:
                        h.write(download_link + "\n")
                        # h.close()
        print ("Operation completed!")
        return data_sample # or set(story_name) depend on our needs.

    def checkfiles(self):
        __links = self.linksOnPage
        #print ("Links avalible to scrap:", len(self.links))
        with open ('dict.txt','r') as g:
            history = g.read()
            # g.close()
            for j in range(len(self.linksOnPage)):
                for i in __links:
                    split = i.split('/')
                    story_number = split[2]
                    if story_number in history:
                        __links.remove(i)
                        # print('bingo!') # for debug purposes
                    else:
                        pass
        self.linksToDownload = __links
        #print ("Links not downloaded:", len(__links))
        #print ('You selected {} links to download.'.format(self.__ran_giv))
        return self.linksToDownload


if __name__ == '__main__':
#     from mech_scrapper_run import *
    CATEGORY = 'movie'
    UNIVERSE = 'Star-Wars'
    scrap = Scrapper(SITE)
    print('Scrapper object created!')
    scrap.follow_link(CATEGORY)
    print('Processing to: ', CATEGORY)
    scrap.follow_link(UNIVERSE)
    print('Processing to: ', UNIVERSE)
    scrap.open(scrap.filtered_fan_fiction())
    scrap.preparing_links()
    print("Filtering and preparing links: ", 'DONE')
    print("Scrapper will now download the fanfiction into files. \n")
    print('=======================================================')
    print("Status:")
    print("Links on website:", len(scrap.linksOnPage))
    print("Links on HDD:", len(scrap.linksOnPage) - len(scrap.checkfiles()), "\n")
    print("You have {} links left to scrap.".format(len(scrap.linksToDownload)))
    print('=======================================================')

    answer = input("Do you want to continue? [Y/N] \n")
    if answer.upper() == "Y":

        print('How many links(stories) you want to download? \n ')
        x = input("all or int \n")
        if x.upper() is "ALL":
            story = scrap.download_list(ran_giv=len(scrap.linksToDownload))
        else :
            story = scrap.download_list(ran_giv=int(x))
    