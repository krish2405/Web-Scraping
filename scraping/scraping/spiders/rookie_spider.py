import scrapy
import json
import re
from scrapy.http import Request


class RookieSpider(scrapy.Spider):
    name = 'rookie'
    start_urls=["https://rookieindia.com/"]
    # cat_url = "{}?pageNumber={}"
    cat_url="{}?page={}"


    def parse(self,response):
        category_urls=response.css("div.text-center ul.site-nav li a::attr(href)").extract()
        for category_url in category_urls:
            if("#" not in category_url):
                  if ("/pages" not in category_url):
                    print(category_url)
                    yield Request(
                    url=self.cat_url.format(self.start_urls[0]+category_url[1:],1),
                    callback=self.parse_category,
                    meta={'page': 2, 'cat_url': self.start_urls[0]+category_url[1:]}
                    )  
            
    def parse_category(self,response):
        page=response.meta.get('page')
        cat_url=response.meta.get('cat_url')
        product_urls=response.css("div.grid-product__content a::attr(href)").extract()
        if (len(product_urls)==0):
            return
        for product_url in product_urls:
            print(self.start_urls[0]+product_url)
            yield Request(
                    url=self.start_urls[0]+product_url,
                    meta={'cat_url':cat_url},
                    callback=self.parse_product
                )
        # pagination
        yield Request(
            url=self.cat_url.format(cat_url,page),
            callback=self.parse_category,
            meta={'page':page+1,'cat_url':cat_url}
        )

    def parse_product(self,response):
        category=response.css("nav.breadcrumb a::text").extract()+response.css("div.product-block h1::text").extract()
        category_tree=""
        for i in range (len(category)):
            if i!=(len(category)-1) :
                category_tree+=category[i]+' > '
            else:
                category_tree+=category[i]
        product_name=response.css("h1.h2.product-single__title::text").get().strip() 
        old_price= response.css("span.product__price.product__price--compare::text").get().strip()
        current_price=response.css("span.product__price.on-sale::text").get().strip()
        size_list=response.css("div.variant-input label::text").extract()
        description=response.css("div.rte p::text").get() 
        product_detail=response.css("div.rte ul li::text").extract()
        image_list=response.css("div.product__thumb-item div a::attr(href)").extract()
        k=response.url
        sku_value=""
        parts = k.split("sku-")
        if len(parts) > 1:
            sku_value += parts[1]
        else:
            print("SKU value not found in the URL.")



        product_data={
            "url":response.url,
            "sku_value":sku_value,
            "category_tree":category_tree,
            "product_name":product_name,
            "old_price":old_price,
            "current_price":current_price,
            "sizelist":size_list,
            "imagelist":image_list,
            "description":description,
            "product_detail":product_detail

        }
        yield product_data
