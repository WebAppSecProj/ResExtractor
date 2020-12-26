# -*- coding: utf-8 -*-
"""
Created on Tue Dec 22 21:08:56 2020

@author: hypo
"""

from treelib import Tree
from bs4 import BeautifulSoup
from multimethod import multimethod
import bs4
import ssl
import urllib.request
import urllib.parse
import re
import sys
import os


class Converter:
    def __init__(self, dom_tree, dimension):
        self.dom_tree = dom_tree
        self.node_info_list = []
        self.dimension = dimension
        self.initial_weight = 1
        self.attenuation_ratio = 0.6
        self.dom_eigenvector = {}.fromkeys(range(0, dimension), 0)

    def get_eigenvector(self):
        for node_id in range(1, self.dom_tree.size() + 1):
            node = self.dom_tree.get_node(node_id)
            node_feature = self.create_feature(node)
            feature_hash = self.feature_hash(node_feature)
            node_weight = self.calculate_weight(node, node_id, feature_hash)
            self.construct_eigenvector(feature_hash, node_weight)
        return self.dom_eigenvector

    @staticmethod
    def create_feature(node):
        node_attr_list = []
        node_feature = node.data.label + '|'
        for attr in node.data.attrs.keys():
            node_attr_list.append(attr + ':' + str(node.data.attrs[attr]))
        node_feature += '|'.join(node_attr_list)
        return node_feature

    @staticmethod
    def feature_hash(node_feature):
        return abs(hash(node_feature)) % (10 ** 8)

    def calculate_weight(self, node, node_id, feature_hash):
        brother_node_count = 0
        depth = self.dom_tree.depth(node)
        for brother_node in self.dom_tree.siblings(node_id):
            brother_node_feature_hash = self.feature_hash(
                self.create_feature(brother_node))
            if brother_node_feature_hash == feature_hash:
                brother_node_count = brother_node_count + 1
        if brother_node_count:
            node_weight = self.initial_weight * self.attenuation_ratio ** depth * \
                self.attenuation_ratio ** brother_node_count
        else:
            node_weight = self.initial_weight * self.attenuation_ratio ** depth
        return node_weight

    def construct_eigenvector(self, feature_hash, node_weight):
        feature_hash = feature_hash % self.dimension
        self.dom_eigenvector[feature_hash] += node_weight


class DOMTree:
    def __init__(self, label, attrs):
        self.label = label
        self.attrs = attrs


class HTMLParser:

    def __init__(self, html):
        self.dom_id = 1
        self.dom_tree = Tree()
        self.bs_html = BeautifulSoup(html, 'lxml')

    def get_dom_structure_tree(self):
        for content in self.bs_html.contents:
            if isinstance(content, bs4.element.Tag):
                self.bs_html = content
        self.recursive_descendants(self.bs_html, 1)
        return self.dom_tree

    def recursive_descendants(self, descendants, parent_id):
        if self.dom_id == 1:
            self.dom_tree.create_node(descendants.name, self.dom_id, data=DOMTree(
                descendants.name, descendants.attrs))
            self.dom_id = self.dom_id + 1
        for child in descendants.contents:
            if isinstance(child, bs4.element.Tag):
                self.dom_tree.create_node(
                    child.name, self.dom_id, parent_id, data=DOMTree(child.name, child.attrs))
                self.dom_id = self.dom_id + 1
                self.recursive_descendants(child, self.dom_id - 1)


def calculated_similarity(dom1_eigenvector, dom2_eigenvector, dimension):
    a, b = 0, 0
    for i in range(dimension):
        a += dom1_eigenvector[i]-dom2_eigenvector[i]
        if dom1_eigenvector[i] and dom2_eigenvector[i]:
            b += dom1_eigenvector[i] + dom2_eigenvector[i]
    similarity = abs(a)/b
    return similarity


def get_html_similarity(html_doc1, html_doc2, dimension=5000):
    hp1 = HTMLParser(html_doc1)
    html_doc1_dom_tree = hp1.get_dom_structure_tree()
    hp2 = HTMLParser(html_doc2)
    html_doc2_dom_tree = hp2.get_dom_structure_tree()
    converter = Converter(html_doc1_dom_tree, dimension)
    dom1_eigenvector = converter.get_eigenvector()
    converter = Converter(html_doc2_dom_tree, dimension)
    dom2_eigenvector = converter.get_eigenvector()
    value = calculated_similarity(
        dom1_eigenvector, dom2_eigenvector, dimension)
    if value > 0.2:
        return False, value
    else:
        return True, value


"""
Get URL feature 
store in dimension dataset[list]
"""


def get_html_info(html, dimension=5000):
    hp1 = HTMLParser(html)
    html_doc1_dom_tree = hp1.get_dom_structure_tree()
    converter = Converter(html_doc1_dom_tree, dimension)
    dom1_eigenvector = converter.get_eigenvector()

    return dom1_eigenvector


"""
The Core url similarity compare function
Input should be two list, have the same dimension
"""


def cal_html_similarity(list1, list2, dimension=5000):
    value = calculated_similarity(list1, list2, dimension)
    if value > 0.2:
        return False, value
    else:
        return True, value


def add_parameters(params, **kwargs):
    "parms producer"
    params.update(kwargs)


def url_filter(url,filter):
    """
        filter can refer to the top 1w weblist by alexa
        or some special string ——such as github/fjson?.
        whatever filter should be a list
    """
    for i in filter:
        if i in url:
            return True
    return False



def url_alive(url):
    """
        To detect the url weather still achievable
    """
    try:
        response = urllib.request.urlopen(url,timeout=3)
    except IOError:
        return False
    except ssl.CertificateError:
        return False
    else:
        code = response.getcode()
        if code == 404:
            return False
        elif code == 403:
            return False
        else:
            return True

def get_html(url):
    response = urllib.request.urlopen(
                url).read().decode('UTF-8')
    html = response.text
    return html

class HTML:
    def __init__(self, URL, ifip=False, dimension=5000):
        if URL.startswith('http'):
            self.__URL = URL
        else:
            self.__URL = 'http://'+URL
        self.__isip = ifip
        self.__content = None
        self.__feature = None
        self.__alive = None
        self.__dimension = dimension

    @property
    def getname(self):
        """
        get url
        """
        return self.__URL

    @property
    def ifip(self):
        """
        check if ip or url
        """
        return self.__isip

    @property
    def topdomain(self):
        """
        get top level domain
        """
        if self.getname.count("/") >=3:
            return re.findall('https?://(.*?)/', self.getname)[0]
        return self.getname

    @property
    def alive(self):
        """
        test if the url is alive
        """
        if self.__alive == None:
            try:
                response = urllib.request.urlopen(self.getname,timeout=3)
            except IOError:
                self.__alive == False
                return False
            except ssl.CertificateError:
                self.__alive == False
                return False
            else:
                code = response.getcode()
                if code == 404:
                    self.__alive == False
                    return False
                elif code == 403:
                    self.__alive == False
                    return False
                else:
                    self.__alive == True
                    return True
        return self.__alive

    @property
    def get_content(self):
        """
        get content
        """
        if self.alive == True and self.__content == None:
            self.__content = urllib.request.urlopen(
                self.__URL).read().decode('UTF-8')
        return self.__content

    @property
    def url_feature(self):
        """
        get feature
        """
        if self.alive == True and self.__feature == None:
            self.__feature = get_html_info(self.get_content, self.__dimension)
        return self.__feature
    
    @multimethod
    def url_similarity(self, url2:object):
        """
        Get the similarity with url2
        """
        if self.url_feature != None and url2.url_feature != None:
            return calculated_similarity(self.url_feature, url2.url_feature, self.__dimension)
        return None
    
    @url_similarity.register
    def url_similarity(self, dom1_eigenvector:list):
        """
        Get the similarity with dblist
        """
        if self.url_feature != None:
            return calculated_similarity(self.url_feature, dom1_eigenvector, self.__dimension)

    @url_similarity.register
    def url_similarity(self,urlstring:str):
        if not urlstring.startswith('http'):
            urlstring = 'http://'+urlstring
        if url_alive(urlstring):
            content = urllib.request.urlopen(
                urlstring).read().decode('UTF-8')
            feature = get_html_info(content, self.__dimension)
            if self.url_feature != None:
                return calculated_similarity(self.url_feature, feature, self.__dimension)
            else:
                return None
        return None
    
    def file_similarity(self,content:str):
        feature = get_html_info(content, self.__dimension)
        if self.url_feature != None:
            return calculated_similarity(self.url_feature, feature, self.__dimension)
        else:
            return None
    
    def regexcheck(self, regex):
        """
        Find a regex in html.
        """
        result = []
        text = self.get_content
        r = re.compile(regex)
        result.extend(r.findall(text))
        return result

    def domain_check(self, balcklist, whitelist):
        """
        check if domain in whitelist or blacklist
        """
        if self.topdomain in whitelist:
            return True
        elif self.topdomain in balcklist:
            return False
        else:
            return None
    
    def download_file(self, filename, path):
        name = filename.split('/')[-1]
        if not os.path.isdir(path):
            os.makedirs(path)
        path = path+'\\'
        
        try:
            if filename[-4:] in ['.jpg', '.png', '.gif', '.bmp','webp','jpeg']:
                path = path + 'images\\'
                if not os.path.isdir(path):
                    os.makedirs(path)
                urllib.request.urlretrieve(filename,'{}{}'.format(path,name))  
            if filename[-2:] == 'js':
                path = path + 'js\\'
                if not os.path.isdir(path):
                    os.makedirs(path)
                urllib.request.urlretrieve(filename,'{}{}'.format(path,name))
            if filename[-3:] == 'css':
                path = path + 'css\\'
                if not os.path.isdir(path):
                    os.makedirs(path)
                urllib.request.urlretrieve(filename,'{}{}'.format(path,name))
            if filename[-4:] == 'html':
                urllib.request.urlretrieve(filename,'{}{}'.format(path,name))
        except Exception as e:
            print("{}{}".format(path,name))
            print("ERROR",e)
            return None
        
    @property
    def css_list(self):
        "save css file"
        content = self.get_content
        patterncss1 = '<link href="(.*?)"'
        patterncss2 = '<link rel="stylesheet" href="(.*?)"'
        patterncss3 = '<link type="text/css" rel="stylesheet" href="(.*?)"'
        result = re.compile(patterncss1, re.S).findall(content)
        result += re.compile(patterncss2, re.S).findall(content)
        result += re.compile(patterncss3, re.S).findall(content)
        result = list(set(result))
        return result
    
    @property
    def js_list(self):
        "save js file"
        content = self.get_content
        patternjs1 = '<script src="(.*?)"'   
        patternjs2 = '<script type="text/javascript" src="(.*?)"'
        lists = re.compile(patternjs1, re.S).findall(content)
        lists += re.compile(patternjs2, re.S).findall(content)
        lists = list(set(lists))
        return lists
        
    @property
    def img_list(self):
        "save pic file"
        content = self.get_content
        patternimg = '<img src="(.*?)"'
        #patternimg2 = '<img.*?src="(.*?)"'
        patternimg3 = r'<img.*?src="([^"]+?\.(jpg|png|gif|bmp|webp|jepg))'
        pic_list = re.compile(patternimg, re.S).findall(content)
        #pic_list += re.compile(patternimg2, re.S).findall(content)
        for i in re.compile(patternimg3 ,re.S).findall(content):
            pic_list.append(i[0])
        pic_list = list(set(pic_list))
        return pic_list

    def list_download(self,lists,newpath):
        final_list = [] 
        for i in lists:
            try:
                if i[0] == 'h':
                    js_url = i
                    self.download_file(i, newpath)
                elif i.startswith('//'):
                    js_url = 'http://'+i[2:]
                    self.download_file(js_url, newpath)
                elif i.startswith('/'):
                    js_url = 'http://'+self.topdomain+i
                    self.download_file(js_url, newpath)
                else:
                    print(i)
                final_list.append(js_url)                     
            except Exception as e:
                print('{}匹配失败'.format(i), '原因:', e)
        return final_list
    
    def scarpy_web(self, appname, path):
        if not self.alive:
            return False
        newpath = os.path.join(path,appname)
        if not os.path.isdir(newpath):
            os.mkdir(newpath)
            
        content = self.get_content
        if content == None:
            return False
        
        "save the main html"
        if self.getname.endswith('.html'):
            self.download_file(self.getname, newpath)
        else:
            try:
                urllib.request.urlretrieve(self.getname,'{}{}.{}'.format(newpath+'\\',self.getname.split('/')[-1],'html'))
            except:
                print("html open error")
                
        "save css file"
        result = self.css_list
        final_list= self.list_download(result,newpath)
        with open(newpath+'\\css.txt','w+') as f:
            for line in final_list:
                f.write(line+'\n')
  

        lists = self.js_list
        final_list = self.list_download(lists,newpath)
        with open(newpath+'\\js.txt','w+') as f:
            for line in final_list:
                f.write(line+'\n')

    
        pic_list = self.img_list
        final_list = self.list_download(pic_list,newpath)
        with open(newpath+'\\img.txt','w+') as f:
            for line in final_list:
                f.write(line+'\n')
        
        return True
        

def test():
    htest = HTML("https://blog.csdn.net/by_side_with_sun/article/details/93859318")
    print(htest.alive)
    print(htest.getname)
    #print(htest.get_content)
    print(htest.url_feature[1])
    print(htest.topdomain)
    #相似度如果大于0.2认为不相似
    print(htest.url_similarity(HTML("http://www.baidu.com")))
    print(htest.url_similarity("www.baidu.com"))
    #print(htest.regexcheck(r'www\.(.*?).com'))
    #htest.download_img(r'C:\Users\hypo\Desktop\黑灰产paper\Applications')
    #htest.download_file('http://www.runoob.com/wp-content/themes/w3cschool.cc/assets/img/qrcode.jpg',r'C:\Users\hypo\Desktop\黑灰产paper\Applications')
    htest.scarpy_web("baidu",r'/home/demo/Desktop/WebAppSec/ResExtractor/')

if __name__== "__main__":
    sys.exit(test())
