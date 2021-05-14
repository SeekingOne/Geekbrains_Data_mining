page_selectors = {
    "pages": '//div[contains(@class, "pagination-hidden")]//a[@class="pagination-page"]/@href',
    "apartments": '//div[@data-marker="item"]'
                  '//div[contains(@class, "iva-item-body")]'
                  '//a[@data-marker="item-title"]/@href',
}

apartment_selectors = {
    "title": '//h1[@class="title-info-title"]/span[@class="title-info-title-text"]/text()',
    "price": '//div[@class="item-price-wrapper"]/div[@id="price-value"]//span[@itemprop="price"]/text()',
    "address": '//div[@itemprop="address"]/span[@class="item-address__string"]/text()',
    "properties": '//div[@class="item-params"]//li[@class="item-params-list-item"]//text()',
    "author_url": '//div[@data-marker="seller-info/name"]/a/@href'
}
