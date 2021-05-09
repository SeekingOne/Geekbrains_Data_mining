
vacancy_selectors = {
    "name": '//h1[@data-qa="vacancy-title"]/span/text()',
    "salary": '//p[@class="vacancy-salary"]/span/text()',
    "description": '//div[@data-qa="vacancy-description" and @class]//text()',
    "skills": '//div[@class="bloko-tag-list"]//span[@data-qa="bloko-tag__text"]/text()',
    "employer_url": '//div[@class="vacancy-company__details"]'
                    '/a[@data-qa="vacancy-company-name"]/@href',
}

employer_selectors = {
    'name': '//div[@class="company-header"]//*[@data-qa="company-header-title-name"]/text() | '
            '//div[@class="tmpl_hh_note"]/text() | //div[@class="tmpl_hh_logo__slogan"]/text()',
    'url': '//a[@data-qa="sidebar-company-site"]/@href | //a[@class="tmpl_hh_head__link"]/@href | '
           '//a[@class="tmpl_hh_button"]/@href',
    'work': '//div[@class="employer-sidebar-block"]/p/text()',
    'description': '//div[@data-qa="company-description-text"]//text()',
}

page_selectors = {
    "pages": '//div[@data-qa="pager-block"]//a[@class="bloko-button"]/@href',
    "vacancies": '//div[@data-qa="vacancy-serp__vacancy vacancy-serp__vacancy_premium"]'
                 '//a[@data-qa="vacancy-serp__vacancy-title"]/@href',
    "employers": '//div[@data-qa="vacancy-serp__vacancy vacancy-serp__vacancy_premium"]'
                 '//div[@class="vacancy-serp-item__meta-info-company"]'
                 '/a[@data-qa="vacancy-serp__vacancy-employer"]/@href',
    "employer_vacancies": '//div[@class="employer-sidebar-block"]'
                          '//a[@data-qa="employer-page__employer-vacancies-link"]/@href',
}
