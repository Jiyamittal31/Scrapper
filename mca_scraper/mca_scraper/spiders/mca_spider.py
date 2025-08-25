import scrapy
from mca_scraper.items import McascraperItem

class McaSpider(scrapy.Spider):
    name = 'mca'
    allowed_domains = ['mca.gov.in']
    start_url = 'https://www.mca.gov.in/mcafoportal/viewCompanyMasterData.do'

    def start_requests(self):
        """
        This method is called by Scrapy to start the crawling process.
        It reads CINs passed from the command line.
        """
        # Get CINs from the command line arguments using -a
        # Example: scrapy crawl mca -a cins=CIN1,CIN2
        cins_str = getattr(self, 'cins', None)
        if not cins_str:
            self.logger.error("No CINs provided! Use -a cins=CIN1,CIN2,...")
            return

        cins = cins_str.split(',')
        for cin in cins:
            cin = cin.strip()
            if cin:
                self.logger.info(f"Queueing request for CIN: {cin}")
                # We use FormRequest to send a POST request, just like in Sprint 1.
                yield scrapy.FormRequest(
                    url=self.start_url,
                    formdata={'companyID': cin},
                    callback=self.parse,
                    meta={'cin': cin} # Pass the CIN to the parse method
                )

    def parse(self, response):
        """
        This method is called to handle the response for each request.
        It parses the HTML and extracts the company data.
        """
        cin = response.meta['cin']
        self.logger.info(f"Parsing response for CIN: {cin}")

        # Check if the result table exists
        result_table = response.css('table#resultTab1')
        if not result_table:
            self.logger.warning(f"No data table found for CIN: {cin}. It might be invalid.")
            return

        # Use a dictionary to map the table labels to our Item fields
        # This makes the code cleaner and easier to maintain.
        field_mapping = {
            'CIN': 'cin',
            'Company Name': 'company_name',
            'ROC Code': 'roc_code',
            'Registration Number': 'registration_number',
            'Company Category': 'company_category',
            'Company Sub Category': 'company_sub_category',
            'Class of Company': 'class_of_company',
            'Date of Incorporation': 'date_of_incorporation',
            'Age of Company': 'age_of_company',
            'Activity': 'activity',
            'Number of Members': 'number_of_members',
        }

        item = McascraperItem()

        # Iterate through rows and extract data
        for row in result_table.css('tr'):
            label = row.css('td:nth-child(1)::text').get(default='').strip().replace(':', '')
            value = row.css('td:nth-child(2)::text').get(default='').strip()

            if label in field_mapping:
                field_name = field_mapping[label]
                item[field_name] = value

        # Yield the populated item to be processed by the pipeline
        yield item
