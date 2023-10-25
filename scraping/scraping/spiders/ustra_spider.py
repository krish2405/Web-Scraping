import scrapy
import json
import re
from scrapy.http import Request


class UstraSpider(scrapy.Spider):
    name = 'ustra'
    start_urls=["https://www.ustraa.com/"]
    
    def parse(self, response):
        category_urls= response.css("div.CategoryListingStrip__Container-gdQQvX a::attr(href)").extract()
        for category_url in category_urls:
            print(category_url)
            yield Request(
                      url=f"{self.start_urls[0]}{category_url[1:]}",
                    callback=self.parse_category  
                
                )
    
    def parse_category(self,response):
        product_urls=response.css("div.ProductCardSimple__ImageContainerStyled-cyJraj a::attr(href)").extract()
        for product_url in product_urls:
            print(product_url)
            yield Request(
                    url=f"{self.start_urls[0]}{product_url[1:]}",
                    callback=self.parse_product
                )
            
    def parse_product(self,response):
        product_name=response.css("h1.product-name-main::text").get() 
        description=(",").join(response.css("div.Content-ezcNVe p::text").extract()+response.css("div.Content-ezcNVe br::text").extract())
        product_detail=response.css("div.ProductFeatureList__FeatureListSection-jclYSD ul li::text").extract()
        manufacture_detail=response.css("div.Col-bXfyBz::text").extract()
        price=response.css("p.SpecialPrice-fPYwa::text").extract()
        product_price=""
        for i in price :
            if i.isdigit():
                product_price+=i
        script_data = response.xpath('//script[@type="application/ld+json"]/text()').get()
        sku="not found"
        if script_data:
            json_data = json.loads(script_data)
            sku = json_data[0].get('sku',"nor")
        image_url=response.css("div.ProductDetailsPageSlide-byLtJI img::attr(src)").extract()
        # print(sku)
        
        product_data={
            "product_name":product_name,
            "product_sku":sku,
            "product_price":product_price,
            "image_url":image_url,
            "description":description,
            "product_detail":product_detail,
            "manufacture_detail":manufacture_detail,

        }

        yield product_data



