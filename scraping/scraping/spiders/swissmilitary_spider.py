import scrapy
import json
import re
from scrapy.http import Request


class SwissmilitarySpider(scrapy.Spider):
    name = 'swiss'
    start_urls=["https://www.swissmilitaryindia.com/"]
    # cat_url = "{}?pageNumber={}"
    cat_url="{}page/{}/"

    def parse(self, response):
        category_urls=response.css("li.menu-item a::attr(href)").extract()
        for category_url in category_urls:
            if("product-category" in category_url ):
                yield Request(
                      url=self.cat_url.format(category_url,1),
                    callback=self.parse_category,
                    meta={'page': 2, 'cat_url': category_url}
                
                )
    
    def parse_category(self,response):
        page=response.meta.get('page')
        cat_url=response.meta.get('cat_url')
        product_urls=response.css("div.hover-img a::attr(href)").extract()
        if (len(product_urls)==0):
            return
        for product_url in product_urls:
            print(product_url)
            yield Request(
                    url=product_url,
                    callback=self.parse_product
                )
        # paginatioin
        yield Request(
            url=self.cat_url.format(cat_url,page),
            callback=self.parse_category,
            meta={'page':page+1,'cat_url':cat_url}
        )

    def parse_product(self,response):
        category=response.css("nav.woocommerce-breadcrumb a::text").extract()+response.css("span.breadcrumb-last::text").extract()
        category_tree=""
        for i in range (len(category)):
            if i!=(len(category)-1) :
                category_tree+=category[i].strip()+' > '
            else:
                category_tree+=category[i].strip()
        product_name=response.css("h1.product_title::text").get().strip()
        old_price=response.css("p.price span.woocommerce-Price-amount bdi::text").extract()[0]
        current_price=response.css("p.price span.woocommerce-Price-amount bdi::text").extract()[1]
        product_sku=response.css("span.sku::text").get().strip()
        image_list=response.css("div.product-image-wrap figure::attr(data-thumb)").extract()
        lab=response.css("span.posted_meta::text").extract()
        val=response.css("span.meta_data::text").extract()
        prodcut_detail={}
        for i in range(len(lab)):
            prodcut_detail[lab[i].replace(": ","")]=val[i]
        sizeandcolorlist=response.css("div.swatches-select.swatches-on-single div::text").extract()
        sizes=[]
        for s in sizeandcolorlist:
            if s in ['S','L', 'M', 'XL', 'XXL','XXXL']:
                sizes.append(s)
        color=[]
        for k in sizeandcolorlist:
            if k not in sizes:
                color.append(k)

        product_data={
            "category_tree":category_tree,
            "product_sku":product_sku,
            'product_name':product_name,
            'old_price':old_price,
            "current_price":current_price,
            "image_list":image_list,
            "product_detail":prodcut_detail,
            "sizes":sizes,
            "colorlist":color

        }
        yield product_data
