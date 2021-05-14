from scrapy.loader import ItemLoader
from itemloaders.processors import TakeFirst, MapCompose, Compose, Join


def clean_str(src_str: str) -> str:
    yield str(src_str).strip().replace("\n ", "").replace('\xa0', ' ')


def full_url(url: str, loader_context):
    return loader_context.get('response').urljoin(url)


def get_properties(properties_list: list):
    properties = {}

    # properties_list = list(map(lambda x: str(x).strip(), properties_list))
    clear_list = list(filter(lambda x: x != "" and x != "\n", properties_list))

    size = len(clear_list)

    for i in range(0, size, 2):
        if i < size - 1:
            properties.update({clear_list[i]: clear_list[i + 1]})

    return properties


class AvitoApartmentLoader(ItemLoader):
    default_output_processor = TakeFirst()

    title_in = MapCompose(clean_str)
    address_in = MapCompose(clean_str)
    properties_in = MapCompose(clean_str)
    properties_out = get_properties
    author_url_in = MapCompose(full_url)
