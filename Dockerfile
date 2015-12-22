FROM ubuntu:15.10

# Install dependencies
RUN apt-get update -y && apt-get install -y \
    wget git \
    python3.5 \
    python3.5

# Get pip
RUN wget https://bootstrap.pypa.io/get-pip.py && python3.5 get-pip.py

# Clone directory and install python requirements
RUN git clone https://github.com/kimpettersen/Sainsbury-s-Software-Engineering-Test.git && pip install -r Sainsbury-s-Software-Engineering-Test/requirements.txt

# Run the crawler
ENTRYPOINT python3.5 Sainsbury-s-Software-Engineering-Test/product_crawler.py http://hiring-tests.s3-website-eu-west-1.amazonaws.com/2015_Developer_Scrape/5_products.html
