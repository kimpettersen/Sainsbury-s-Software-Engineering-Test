"""
    CLI tool to crawl Sainsburys Product Pages.
    - Prints a json string of the parsed products:
    {
        'product_list': [{

            'title': <title>,
            'unit_price': <unit_price>,
            'size': <size>,
            'description': <description>
        }],
        'total_product_sum': <sum x.xx>
    }
    - It will fail if any product has broken links that can't be retrieved
    - Title, unit_price, size or description are set to null if they
    can't be parsed by the set rules
"""

import json
import re
import sys

import requests

from bs4 import BeautifulSoup
from pprint import pprint


def request_html(uri):
    """
        - Takes a uri and returns a requests object.
        - Raises requests.exceptions.HTTPError when status code is 4XX or 5XX
    """
    req = requests.get(uri)
    req.raise_for_status()
    return req

def parse_unit_price(inner_text):
    """
        - Input is innerText of an element: '&pound1.50;/unit'
        - Regex looks for any number - integer or floating point.
        - Returns the number casted to a float or None
    """
    match = re.search(r'\d+(.\d+)?', inner_text)
    if match:
        return float(match.group())
    return None

def parse_description(html):
    """
        - Returns a string with product description
        - Assumes that the first occurence of .productTest inside of the custom
            tag htmlcontent contains the product description
    """
    soup = BeautifulSoup(html, 'html.parser')
    description = soup.select('htmlcontent .productText')[0]
    description = description.get_text().strip()
    return description

def get_page_size(req):
    """
        - Returns a string representing the size of the request body
            in kilo bytes.
            The value is taken from the Content-Length header and converted to
            bytes assuming 1024 bytes == 1kb
    """
    content_length = req.headers.get('Content-Length')
    size = int(content_length)
    size = round(size / 1024, 1)
    return '{}kb'.format(size)

def parse_products_list(html):
    """
        - Returns an iterator that yields a dictonary in the follwing format:
        {
            'uri': <uri to product specific page>
            'title': <title of the product>
            'unit_price': <unit price of the product>
        }
        - Raises ValueError if None is passed
        - Assumes titles can be found with: '.productInfo h3 a'
        - Assumes unit_price can be found with: '.pricePerUnit'
    """
    if not html:
        raise ValueError('Bad input for parsing product list: {}'.format(html))

    soup = BeautifulSoup(html, 'html.parser')
    product_list = soup.find('ul', attrs={'class': 'productLister'})

    if not product_list:
        raise ValueError('Could not find element with class \'productLister\'')

    for li in product_list.select('li'):
        title = None
        uri = None
        unit_price = None

        title_html = li.select('.productInfo h3 a')
        price_html = li.select('.pricePerUnit')

        if title_html:
            title = title_html[0].get_text().strip()
            uri = title_html[0].get('href')

        if price_html:
            unit_price = parse_unit_price(price_html[0].get_text())

        yield {
            'title': title,
            'uri': uri,
            'unit_price': unit_price
        }

def construct_product_list(products):
    """
        - Returns a list of dictonaries:
        {
            'title': <title>
            'unit_price': <unit_price>
            'size': <size>
            'description': <description>
        }
        - Raises requests.exceptions.HTTPError if the requested uri is bad
    """

    res = []
    for product in products:
        uri = product.get('uri')

        # Raises requests.exceptions.HTTPError if the request is bad
        product_request = request_html(uri)

        size = get_page_size(product_request)
        description = parse_description(product_request.text)

        res.append({
            'title': product.get('title'),
            'unit_price': product.get('unit_price'),
            'size': size,
            'description': description
        })
    return res

def crawl(uri):
    """
        - Returns full dictionary with results and total_price
        {
            'product_list': <product_list>
            'total_product_sum': <sum x.xx>
        }
        - Exits if any of requested pages can't be retrieved
    """

    try:
        product_list_request = request_html(uri)
    except requests.exceptions.HTTPError as e:
        sys.exit('Bad request when getting: {}\n{}\n'.format(uri, e))

    html = product_list_request.text
    try:
        products = list(parse_products_list(html))
    except requests.exceptions.HTTPError as e:
        m = 'An error occured when getting a linked page\n{}'.format(e)
        sys.exit(m)
    else:
        total_sum = sum([product.get('unit_price') for product in products])
        total_sum = format(total_sum, '.2f')
        return {
            'product_list': construct_product_list(products),
            'total_product_sum': total_sum
        }

if __name__ == '__main__':
    """
        - Crawls each uri passed to the script
        - Prints separate json object for each passed uri
    """
    args = sys.argv[1:]
    print('Started Scraping')
    for arg in args:
        products = crawl(arg)
        print(json.dumps(products))
