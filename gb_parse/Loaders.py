from scrapy import Field
from scrapy.loader import ItemLoader
from itemloaders.processors import TakeFirst, MapCompose, Join
from scrapy.item import Item
from urllib.parse import urljoin


class VacancyData(Item):
    url = Field()
    name = Field()
    description = Field()
    salary = Field()
    skills = Field()
    employer_url = Field()


class EmployerData(Item):
    name = Field()
    url = Field()
    work = Field()
    description = Field()


def get_salary(salary_str_list: list) -> dict:
    salary_amounts = list()
    salary = {
        'in_words': '',
        'min': 0.0,
        'max': 0.0
    }
    for literal in salary_str_list:
        literal = literal.replace('\xa0', '')
        salary['in_words'] += literal
        if literal.isdigit():
            salary_amounts.append(float(literal))
    if len(salary_amounts) > 1:
        salary_amounts.sort()
        salary['min'] = salary_amounts[0]
        salary['max'] = salary_amounts[len(salary_amounts)-1]
    elif len(salary_amounts) == 1:
        salary['min'] = salary_amounts[0]
        salary['max'] = salary_amounts[0]
    return salary


def clean_str(src_str: str) -> str:
    return src_str.replace('\xa0', ' ')


def full_url(url: str, loader_context):
    base_url = loader_context.get('url')
    return urljoin(base_url, url)


class HHVacancyLoader(ItemLoader):
    default_output_processor = TakeFirst()

    description_out = Join()
    salary_out = get_salary

    employer_url_in = MapCompose(full_url)


class HHEmployerLoader(ItemLoader):
    default_output_processor = TakeFirst()

    description_in = MapCompose(clean_str)
    description_out = Join()
    name_in = MapCompose(clean_str)
    name_out = Join()
