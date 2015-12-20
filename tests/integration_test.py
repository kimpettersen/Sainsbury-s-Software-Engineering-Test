"""
    Integration tests

    Checking against the test page on s3:
     - count matches
     - sample data from s3
"""
import re
import subprocess
import pytest

from bs4 import BeautifulSoup

uri = 'http://hiring-tests.s3-website-eu-west-1.amazonaws.com/' \
    + '2015_Developer_Scrape/5_products.html'

def test_product_count():
    #Execute the script
    stdout = subprocess.check_output(['python', 'product_crawler.py', uri])
    stdout = str(stdout)

    # Get the count of all how many times each property is in the JSON
    title_count = len(re.findall(r'"title":', stdout))
    size_count = len(re.findall(r'"size":', stdout))
    unit_count = len(re.findall(r'"unit_price":', stdout))
    desc_count = len(re.findall(r'"description":', stdout))
    sum_count = len(re.findall(r'"total_product_sum":', stdout))

    assert title_count == 7
    assert size_count == 7
    assert unit_count == 7
    assert desc_count == 7
    assert sum_count == 1

def test_title():
    stdout = subprocess.check_output(['python', 'product_crawler.py', uri])
    stdout = str(stdout)
    assert '"title": "Sainsbury\\\'s Golden Kiwi x4"' in stdout

def test_unit_price():
    stdout = subprocess.check_output(['python', 'product_crawler.py', uri])
    stdout = str(stdout)
    assert '"unit_price": 3.5' in stdout

def test_unit_description():
    stdout = subprocess.check_output(['python', 'product_crawler.py', uri])
    stdout = str(stdout)
    assert '"description": "Avocados"' in stdout

def test_unit_total_price():
    stdout = subprocess.check_output(['python', 'product_crawler.py', uri])
    stdout = str(stdout)
    assert '"total_product_sum": "15.10"' in stdout

def test_unit_size():
    stdout = subprocess.check_output(['python', 'product_crawler.py', uri])
    stdout = str(stdout)
    assert '"size": "43.4kb"' in stdout
