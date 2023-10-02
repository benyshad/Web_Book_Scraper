import scrapy
from bookscraper.items import BookscraperItem
from dotenv import load_dotenv
from urllib.parse import urlencode
import os
load_dotenv()

class BookspiderSpider(scrapy.Spider):
    name = "bookspider"
    allowed_domains = ["books.toscrape.com", "proxy.scrapeops.io"]
    start_urls = ["https://books.toscrape.com"]

    # custom_settings = {
    #     'FEEDS': { 'data.jsonl': { 'format': 'jsonlines',}}
    #     }

    def start_requests(self):
        yield scrapy.Request(url=self.get_proxy_url(self.start_urls[0]), callback=self.parse)

    def get_proxy_url(self, page_url):
        api_key = {'api_key' : os.getenv('API_SECRET_KEY')}
        api_key = urlencode(api_key)
        book_page_url = f"https://proxy.scrapeops.io/v1/?{api_key}&url={page_url}"
        return book_page_url

    def parse(self, response):
        books = response.css('article.product_pod')

        for book in books:
            yield{
                'name' : book.css('h3 a::text').get(),
                'price' : book.css('.product_price .price_color::text').get(),
                'url' : book.css('h3 a::attr(href)').get()
            }
            book_url = book.css('h3 a::attr(href)').get()
            if 'catalogue/' in book_url:
                book_page_url = 'https://books.toscrape.com/' + book_url
            else:
                book_page_url = 'https://books.toscrape.com/catalogue/' + book_url
            if book_page_url == 'https://books.toscrape.com/catalogue/libertarianism-for-beginners_982/index.html' or book_page_url == 'https://books.toscrape.com/catalogue/a-light-in-the-attic_1000/index.html':
                yield response.follow(self.get_proxy_url(book_page_url), self.parse_book_page)


        # next_page = response.css('li.next a::attr(href)').get()
        # if next is not None:
        #     if 'catalogue/' in next_page:
        #         next_page_url = 'https://books.toscrape.com/' + next_page
        #     else:
        #         next_page_url = 'https://books.toscrape.com/catalogue/' + next_page
        # yield response.follow(self.get_proxy_url(next_page_url), callback=self.parse)

    def parse_book_page(self, response):
        book_page = response.css('div.page_inner')
        book_item = BookscraperItem()

        book_item['title'] = book_page.css('h1::text').get(),
        book_item['url'] = response.url,
        book_item['category'] = book_page.xpath("//li[@class='active']/preceding-sibling::li[1]/a/text()").get(),
        book_item['price'] = book_page.css('p.price_color::text').get(),
        book_item['upc'] = book_page.xpath("//table/tr[1]/td/text()").get(),
        book_item['product_type'] = book_page.xpath("//table/tr[2]/td/text()").get(),
        book_item['tax'] = book_page.xpath("//table/tr[5]/td/text()").get(),
        book_item['availability'] = book_page.xpath("//table/tr[6]/td/text()").get(),
        book_item['num_reviews'] = book_page.xpath("//table/tr[7]/td/text()").get(),
        book_item['stars'] = book_page.css("p.star-rating::attr(class)").get()

        yield book_item
        