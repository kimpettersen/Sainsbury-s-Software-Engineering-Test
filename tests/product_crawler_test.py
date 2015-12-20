import pytest
import requests

from unittest.mock import Mock
from unittest.mock import patch

import product_crawler as crawler


@patch('requests.get')
def test_request_html(mock_get):
    uri = 'http://domain.com/a'
    requests_mock = Mock()
    mock_get.return_value = requests_mock

    res = crawler.request_html(uri)

    requests.get.assert_called_once_with(uri)
    requests_mock.raise_for_status.assert_called_once_with()
    assert res == requests_mock

def test_parse_input_price():
    assert crawler.parse_unit_price('&pound1.50;/unit') == 1.50
    assert crawler.parse_unit_price('&pound;/unit') == None
    assert crawler.parse_unit_price('&pound1.abc;/unit') == 1.0

def test_parse_description():
    description = 'a product description'
    html = """
        <div>
            <htmlcontent>
                <div></div>
                <div class='productText'><p>{}</p>\n\t<p></p></div>
                <div class='productText'><p>abc</p>\n\t<p></p></div>
            </htmlcontent>
        </div>
    """
    html = html.format(description)
    assert crawler.parse_description(html) == description

def test_get_page_size():
    mock_request = Mock()
    mock_request.headers = {
        'Content-Length': 2048
    }
    assert crawler.get_page_size(mock_request) == '2.0kb'

def test_parse_product_list():
    href_1 = 'http://domain.com'
    title_1 = 'a product title'
    price_1 = 1.3
    href_2 = 'http://domain2.com'
    title_2 = 'another product title'
    price_2 = 2.0
    html = """
        <ul class="productLister">
            <li>
                <div class="productInfo">
                    <h3>
                        <a href="{href_1}">
                            {title_1}
                        </a>
                    </h3>
                </div>
                <div class="pricePerUnit"><p>'&pound{price_1};/unit'</p></div>
            </li>
            <li>
                <div class="productInfo">
                    <h3>
                        <a href="{href_2}">
                            {title_2}
                        </a>
                    </h3>
                </div>
                <div class="pricePerUnit"><p>'&pound{price_2};/unit'</p></div>
            </li>
        </ul>
    """
    html = html.format(
        href_1=href_1,
        title_1=title_1,
        price_1=price_1,
        href_2=href_2,
        title_2=title_2,
        price_2=price_2
        )
    product_list = crawler.parse_products_list(html)
    res = next(product_list)
    assert res.get('title') == title_1
    assert res.get('uri') == href_1
    assert res.get('unit_price') == price_1
    res = next(product_list)
    assert res.get('title') == title_2
    assert res.get('uri') == href_2
    assert res.get('unit_price') == price_2

def test_parse_product_list_no_list():
    html = '<ul class="productLister"></ul>'
    product_list = crawler.parse_products_list(html)
    assert list(product_list) == []

def test_parse_product_list_no_values():
    html = """
        <ul class="productLister">
            <li></li>
        </ul>
    """
    product_list = crawler.parse_products_list(html)
    res = next(product_list)
    assert res.get('title') == None
    assert res.get('uri') == None
    assert res.get('unit_price') == None

@patch('product_crawler.request_html')
@patch('product_crawler.get_page_size')
@patch('product_crawler.parse_description')
def test_construct_product_list_desc(desc_mock, size_mock, req_mock):
    products = [{'uri': ''},{'uri': ''}]
    desc_mock.side_effect = ['description1', 'description2']
    res = crawler.construct_product_list(products)
    assert desc_mock.call_count == 2
    assert res[0]['description'] == 'description1'
    assert res[1]['description'] == 'description2'

@patch('product_crawler.request_html')
@patch('product_crawler.get_page_size')
@patch('product_crawler.parse_description')
def test_construct_product_list_size(desc_mock, size_mock, req_mock):
    products = [{'uri': ''},{'uri': ''}]
    size_mock.side_effect = ['1kb', '2kb']
    res = crawler.construct_product_list(products)
    assert size_mock.call_count == 2
    assert res[0]['size'] == '1kb'
    assert res[1]['size'] == '2kb'

@patch('product_crawler.request_html')
@patch('product_crawler.get_page_size')
@patch('product_crawler.parse_description')
def test_construct_product_list_title(desc_mock, size_mock, req_mock):
    products = [{'title': 'title1'},{'title': 'title2'}]
    res = crawler.construct_product_list(products)
    assert res[0]['title'] == 'title1'
    assert res[1]['title'] == 'title2'

@patch('product_crawler.request_html')
@patch('product_crawler.get_page_size')
@patch('product_crawler.parse_description')
def test_construct_product_list_price(desc_mock, size_mock, req_mock):
    products = [{'unit_price': 1},{'unit_price': 2}]
    res = crawler.construct_product_list(products)
    assert res[0]['unit_price'] == 1
    assert res[1]['unit_price'] == 2


@patch('product_crawler.request_html')
def test_crawl_sys_exit(req_mock):
    req_mock.side_effect = requests.exceptions.HTTPError
    uri = 'domain.com'
    with pytest.raises(SystemExit) as e:
        crawler.crawl(uri)
        assert 'Bad request when getting: ' in e
        assert uri in e


@patch('product_crawler.parse_products_list')
@patch('product_crawler.request_html')
def test_crawl_sys_linked_page_fail(req_mock, prod_list_mock):
    prod_list_mock.side_effect = requests.exceptions.HTTPError
    with pytest.raises(SystemExit) as e:
        crawler.crawl('')
        assert 'An error occured when getting a linked page: ' in e

@patch('product_crawler.construct_product_list')
@patch('product_crawler.parse_products_list')
@patch('product_crawler.request_html')
def test_crawl_sum(req_mock, prod_list_mock, construct_list_mock):
    prod_list_mock.return_value = [{'unit_price': 1.0},{'unit_price': 2.0}]
    res = crawler.crawl('')
    assert res.get('total_product_sum') == '3.00'

@patch('product_crawler.construct_product_list')
@patch('product_crawler.parse_products_list')
@patch('product_crawler.request_html')
def test_crawl_product_list(req_mock, prod_list_mock, construct_list_mock):
    prod_list = [{'title': 'test'}, {'title': 'test2'}]
    construct_list_mock.return_value = prod_list
    res = crawler.crawl('')
    assert res.get('product_list') == prod_list
