"""
Utility script to generate XPaths for the given URL
* Take the input URL from the user
* Parse the HTML content using beautifilsoup
* Find all Input and Button tags
* Guess the XPaths
"""

from selenium import webdriver
from bs4 import BeautifulSoup
import requests
from lxml import etree, html
from io import StringIO
import logging

parser = etree.HTMLParser()


class Xpath_Util:
    "Class to generate the xpaths"

    def __init__(self):
        self.elements = None
        self.required_elements = ['input', 'button','li', 'a', 'h3', 'div']
        self.known_attribute_list = ['id', 'name', 'placeholder', 'value', 'title', 'type', 'class']
        self.root = None
        self.locators = []
        self.locatortype = {}

    def check_xpath(self, xpath):
        return self.root.xpath(xpath)

    def generate_xpath(self, response):
        "generate the xpath"
        soup = BeautifulSoup(response.text, 'html.parser')
        self.root = etree.parse(StringIO(response.text), parser)
        result_flag = False
        try:
            for required_element in self.required_elements:
                self.elements = soup.find_all(required_element)
                for element in self.elements:
                    self.locatortype = {}
                    if (not element.has_attr("type")) or (element.has_attr("type") and element['type'] != "hidden"):
                        for attr in self.known_attribute_list:
                            if self.identify_xpath(required_element, element):
                                result_flag = True
                                break
                            elif required_element == 'button' and element.getText():
                                button_text = element.getText()
                                if element.getText() == button_text.strip():
                                    locator = xpath_obj.guess_xpath_button(required_element, "text()",
                                                                           element.getText())
                                else:
                                    locator = xpath_obj.guess_xpath_using_contains(required_element, "text()",
                                                                                   button_text.strip())
                                if len(self.check_xpath(locator)) == 1:
                                    result_flag = True
                                    replace_string = self._replace_hypen(href_text)
                                    key = replace_string+"_button"
                                    self.locatortype['xpath'] = locator
                                    self.locatortype['key'] = key
                                    break
                            elif required_element == 'a' and element.getText():
                                href_text = element.getText()
                                if element.getText() == href_text.strip():
                                    locator = xpath_obj.guess_xpath_button(required_element, "text()",
                                                                           element.getText())
                                else:
                                    locator = xpath_obj.guess_xpath_using_contains(required_element, "text()",
                                                                                   href_text.strip())
                                if len(self.check_xpath(locator)) == 1:
                                    result_flag = True
                                    replace_string = self._replace_hypen(href_text)
                                    key = replace_string+"_link"
                                    self.locatortype['xpath'] = locator
                                    self.locatortype['key'] = key
                                    break
                            else:
                                print(element)

                    else:
                        print(element)
                    if self.locatortype:
                        self.locators.append(self.locatortype)
            print(self.locators)

        except Exception as e:
            print("Exception when trying to generate xpath for:%s" % required_element)
            logging.exception("message")
            print("Python says:%s" % str(e))
        return result_flag

    def guess_xpath(self, tag, attr, element):
        "Guess the xpath based on the tag,attr,element[attr]"
        # Class attribute returned as a unicodeded list, so removing 'u from the list and joining back
        if type(element[attr]) is list:
            element[attr] = [i for i in element[attr]]
            element[attr] = ' '.join(element[attr])
        self.xpath = "//%s[@%s='%s']" % (tag, attr, element[attr])
        return self.xpath

    def guess_xpath_button(self, tag, attr, element):
        "Guess the xpath for button tag"
        self.button_xpath = "//%s[%s='%s']" % (tag, attr, element)

        return self.button_xpath

    def guess_xpath_using_contains(self, tag, attr, element):
        "Guess the xpath using contains function"
        self.button_contains_xpath = "//%s[contains(%s,'%s')]" % (tag, attr, element)

        return self.button_contains_xpath

    def _replace_hypen(self, text):
        field_name = text.lower().translate({ord(c): "_" for c in "!@#$%^&*()[]{};:,./<>?\|`~-=_+"})
        field_name = field_name.translate({ord(c): " " for c in "'"})
        field_name = field_name.translate({ord(c): " " for c in "\n"})
        field_name = field_name.translate({ord(c): "_" for c in "__"})
        return field_name

    def identify_xpath(self, tag, element):
        attr_list = []
        for attr in self.known_attribute_list:
            if element.has_attr(attr):
                if type(element[attr]) is list:
                    element[attr] = [i for i in element[attr]]
                    element[attr] = ' '.join(element[attr])
                attr_list.append("@%s='%s'" % (attr, element[attr]))
                if attr == 'class':
                    self.locatortype['class'] = element[attr]
                if attr == 'id':
                    self.locatortype['id'] = element[attr]
                if attr == 'tag':
                    self.locatortype['id'] = element[attr]
                if attr == 'name':
                    self.locatortype['name'] = element[attr]
        attr_elements = ''
        for ele in attr_list:
            if attr_elements:
                attr_elements = ele + 'and' + attr_elements
            else:
                attr_elements = ele
                field_name = self._replace_hypen(ele.split("='")[1])
                key = field_name+ "_" + tag
            xpath = "//%s[%s]" % (tag, attr_elements)
            if len(self.check_xpath(xpath)) == 1:
                self.locatortype['xpath'] = xpath
                self.locatortype['key'] = key
                return xpath
        return False


# -------START OF SCRIPT--------
if __name__ == "__main__":
    print("Start of %s" % __file__)
    url = "https://testproject.io/"
    #url = "https://www.flipkart.com/"
    # Initialize the xpath object
    xpath_obj = Xpath_Util()

    # Get the URL and parseto generate xpath for
    response = requests.get(url)

    # execute generate_xpath
    if xpath_obj.generate_xpath(response) is False:
        print("No XPaths generated for the URL:%s" % url)
