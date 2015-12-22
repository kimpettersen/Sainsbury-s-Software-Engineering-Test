##Sainsbury’s Software Engineering Test

Requires Python 3.5 (There's no reason it shouldn't work with at least 3.4).
For simplicity I've purposely not followed an OO pattern. If this script were to be used by another module and were responsible for storing some sort of state, I would probably want to change that.

##Run as a Docker container

- Make sure you hve Docker installed
- `docker run kimpettersen/sainsburys-product-crawler`

##Clone and run locally

- Create a virtualenv with python 3.5 https://virtualenv.readthedocs.org/en/latest/
- Install dependencies: `pip install -r requirements.txt`
- Run script with: `python product_crawler.py http://hiring-tests.s3-website-eu-west-1.amazonaws.com/2015_Developer_Scrape/5_products.html`
- Outputs a JSON string:

Sample output:

```
Started Scraping
{"total_product_sum": "15.10", "product_list": [{"unit_price": 3.5, "title": "Sainsbury's Apricot Ripe & Ready
x5", "description": "Apricots", "size": "38.3kb"}, {"unit_price": 1.5, "title": "Sainsbury's Avocado Ripe &
Ready XL Loose 300g", "description": "Avocados", "size": "38.7kb"}, {"unit_price": 1.8, "title": "Sainsbury's
Avocado, Ripe & Ready x2", "description": "Avocados", "size": "43.4kb"}, {"unit_price": 3.2, "title":
"Sainsbury's Avocados, Ripe & Ready x4", "description": "Avocados", "size": "38.7kb"}, {"unit_price": 1.5,
"title": "Sainsbury's Conference Pears, Ripe & Ready x4 (minimum)", "description": "Conference", "size":
"38.5kb"}, {"unit_price": 1.8, "title": "Sainsbury's Golden Kiwi x4", "description": "Gold Kiwi", "size":
"38.6kb"}, {"unit_price": 1.8, "title": "Sainsbury's Kiwi Fruit, Ripe & Ready x4", "description": "Kiwi",
"size": "39.0kb"}]}
```

##Tests

Uses `py.test` for both unit and integration tests. Run the tests with `py.test -v` for tests with verbose output

To only run unit tests: `py.test tests/product_crawler_test.py`
To only run integration tests: `py.test tests/integration_test.py`

###Integration Tests

I'm assuming I can use the s3 page as a test server for the integration tests. I didn't want to introduce another framework for these tests so i made a simple solution using a subprocess.
