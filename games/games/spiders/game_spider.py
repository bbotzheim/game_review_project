from scrapy import Spider, Request
from games.items import GameItem, ReviewItem

class GameSpider(Spider):
    name = 'game_spider'
    allowed_urls = ['https://www.metacritic.com']
    start_urls = ['https://www.metacritic.com/browse/games/score/metascore/all/all/filtered?sort=desc&page=0']

    def parse(self, response):
        num_pages = int(response.xpath('//*[@id="main_content"]//div[@class="page_nav"]//li[@class="page last_page"]/a/text()').extract_first())
        page_urls = [f'https://www.metacritic.com/browse/games/score/metascore/all/all/filtered?sort=desc&page={i}' for i in range(0, num_pages)]

        for url in page_urls:
            yield Request(url=url, callback=self.parse_game_urls, dont_filter = True)

    def parse_game_urls(self, response):
        game_urls = response.xpath('//*[@id="main_content"]//table[@class="clamp-list"]//td[@class="clamp-summary-wrap"]//a[@class="title"]/@href').extract()
        game_urls = ['https://www.metacritic.com' + url for url in game_urls]

        for url in game_urls:
            yield Request(url=url, callback=self.parse_game_page, meta={'url':url}, dont_filter = True)

    def parse_game_page(self, response):
        url = response.meta['url']
        
        patterns = ['//*[@id="main_content"]//div[@class="content_head product_content_head game_content_head"]//span[@class="platform"]//text()', '//*[@id="main_content"]//div[@class="content_head product_content_head game_content_head"]//span[@class="platform"]/a/text()']
        
        for pattern in patterns:
            platform = response.xpath(pattern).extract_first().strip() #extra white space
            if platform:
                break
        title = response.xpath('//*[@id="main_content"]//div[@class="content_head product_content_head game_content_head"]//h1/text()').extract_first()
        genres = response.xpath('//*[@id="main_content"]//div[@id="main" and @class="col main_col"]//li[@class="summary_detail product_genre"]/span[@class="data"]/text()').extract()
        try:
            average_user_score = float(response.xpath('//*[@id="main_content"]//div[@class="details side_details"]//a[@class="metascore_anchor"]/div/text()').extract_first())
        except:
            average_user_score = response.xpath('//*[@id="main_content"]//div[@class="details side_details"]//a[@class="metascore_anchor"]/div/text()').extract_first()
        try:
            metascore = float(response.xpath('//*[@id="main_content"]//div[@class="details main_details"]//a[@class="metascore_anchor"]/div/span/text()').extract_first()) #float
        except:
            metascore = response.xpath('//*[@id="main_content"]//div[@class="details main_details"]//a[@class="metascore_anchor"]/div/span/text()').extract_first()

        item = GameItem()
        item['url'] = url #need to make sure this works...
        item['title'] = title
        item['platform'] = platform
        item['genres'] = ", ".join(genres)
        item['release_date'] = response.xpath('//*[@id="main_content"]//div[@class="content_head product_content_head game_content_head"]/div[@class="product_data"]//li[@class="summary_detail release_data"]/span[@class="data"]/text()').extract_first() #date
        item['ESRB_rating'] = response.xpath('//*[@id="main_content"]//div[@id="main" and @class="col main_col"]//li[@class="summary_detail product_rating"]/span[@class="data"]/text()').extract_first()
        item['summary'] = response.xpath('//*[@id="main_content"]//div[@id="main" and @class="col main_col"]//div[@class="details main_details"]//span[@class="blurb blurb_expanded"]/text()').extract_first()
        item['average_user_score'] = average_user_score
        item['metascore'] = metascore
        item['developer'] = response.xpath('//*[@id="main_content"]//div[@id="main" and @class="col main_col"]//li[@class="summary_detail developer"]/span[@class="data"]/text()').extract_first().strip() #extra white space
        item['publisher'] = response.xpath('//*[@id="main_content"]//div[@class="content_head product_content_head game_content_head"]/div[@class="product_data"]//li[@class="summary_detail publisher"]/span[@class="data"]/a/text()').extract_first().strip() #extra white space

        yield item

        user_review_page = response.xpath('//*[@id="main_content"]//li[@class="nav nav_user_reviews"]//@href').extract_first()
        user_review_page = 'https://www.metacritic.com' + user_review_page

        critic_review_page = response.xpath('//*[@id="main_content"]//li[@class="nav nav_critic_reviews"]//@href').extract_first()
        critic_review_page = 'https://www.metacritic.com' + critic_review_page

        yield Request(url=user_review_page, callback=self.parse_user_urls, meta={'title':title, 'platform':platform, 'url':url}, dont_filter = True)
        yield Request(url=critic_review_page, callback=self.parse_critic_urls, meta={'title':title, 'platform':platform, 'url':url}, dont_filter = True)
        print('Finished Scraping ' + title )

    def parse_user_urls(self, response):
        title = response.meta['title']
        platform = response.meta['platform']
        try:
            num__user_pages = int(response.xpath('//*[@id="main_content"]//div[@class="page_nav"]//li[@class="page last_page"]/a/text()').extract_first())
            user_urls = [response.meta['url'] + f'/user-reviews?page={i}' for i in range(0, num__user_pages)]
        except:
            user_urls = [response.meta['url'] + '/user-reviews?page=0']

        for url in user_urls:
            yield Request(url=url, callback=self.parse_user_reviews, meta={'title':title, 'platform':platform}, dont_filter = True)

    def parse_user_reviews(self, response):
        title = response.meta['title']
        platform = response.meta['platform']

        reviews = response.xpath('//*[@id="main_content"]//div[@class="body product_reviews"]//div[@class="review_section"]')
        if reviews:
            for review in reviews:
                username = review.xpath('.//div[@class="name"]/a/text()').extract_first()
                score = review.xpath('.//div[@class="review_grade"]/div/text()').extract_first() # int
                date = review.xpath('.//div[@class="date"]/text()').extract_first()
                review_text = review.xpath('.//div[@class="review_body"]//span[@class="blurb blurb_expanded"]/text()').extract()
                review_text = " ".join([text.strip() for text in review_text])
                if not review_text:
                    review_text = review.xpath('.//div[@class="review_body"]//text()').extract()
                    review_text = " ".join([text.strip() for text in review_text])

                item = ReviewItem()
                item['title'] = title #meta syntax?
                item['platform'] = platform
                item['username'] = username
                item['score'] = int(score)
                item['date'] = date
                item['review_text'] = review_text
                item['critic_flag'] = 0

                yield item
            else: pass

        print('Finished Scraping {0} User Reviews for '.format(len(reviews)) + title)

    def parse_critic_urls(self, response):
        title = response.meta['title']
        platform = response.meta['platform']
        try:
            num__critic_pages = int(response.xpath('//*[@id="main_content"]//div[@class="page_nav"]//li[@class="page last_page"]/a/text()').extract_first())
            critic_urls = [response.meta['url'] + f'/critic-reviews?page={i}' for i in range(0, num__critic_pages)]
        except:
            critic_urls = [response.meta['url'] + '/critic-reviews?page=0']

        for url in critic_urls:
            yield Request(url=url, callback=self.parse_critic_reviews, meta={'title':title, 'platform':platform}, dont_filter = True)

    def parse_critic_reviews(self, response):
        title = response.meta['title']
        platform = response.meta['platform']

        reviews = response.xpath('//*[@id="main_content"]//div[@class="body product_reviews"]//div[@class="review_section"]')

        if reviews:
            for review in reviews:
                username = review.xpath('.//div[@class="source"]//text()').extract_first().strip() 
                score = review.xpath('.//div[@class="review_grade"]/div/text()').extract_first()
                try:
                    score = int(score)
                except Exception:
                    pass
                date = review.xpath('.//div[@class="date"]/text()').extract_first()
                review_text = review.xpath('.//div[@class="review_body"]//text()').extract() #extra white space
                review_text = " ".join([text.strip() for text in review_text])

                item = ReviewItem()
                item['title'] = title #meta syntax?
                item['platform'] = platform
                item['username'] = username
                item['score'] = score
                item['date'] = date
                item['review_text'] = review_text
                item['critic_flag'] = 1

                yield item
        else: pass
        print('Finished Scraping {0} Critic Reviews for '.format(len(reviews)) + title)

