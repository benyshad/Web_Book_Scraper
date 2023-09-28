# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter


class BookscraperPipeline:
    def process_item(self, item, spider):
        adapter = ItemAdapter(item)

        # convert all field values from tuples to strings
        field_names = adapter.field_names()
        for field_name in field_names:
            if field_name != 'stars':
                value = adapter.get(field_name)
                adapter[field_name] = value[0]

        # converts values to lowercase
        lowercase_keys = ['category', 'product_type']
        for lowercase_key in lowercase_keys:
            value = adapter.get(lowercase_key)
            adapter[lowercase_key] = value.lower()

        # removes euro symbol and converts to float
        euros = ['price', 'tax']
        for euro in euros:
            value = adapter.get(euro)
            value = value.replace('£', '')
            adapter[euro] = float(value)

        # removes all char except the amount availible and returns as int 
        value = adapter.get('availability')
        split_value = value.split('(')
        if len(split_value) < 2:
            value = 0
        else:
            split_value = split_value[1].split(' ')
            value = split_value[0]
        adapter['availability'] = int(value)

        # converts to int
        value = adapter.get('num_reviews')
        adapter['num_reviews'] = int(value)

        # converts the amount of stars from str to int
        stars_string = adapter.get('stars')
        split_stars_array = stars_string.split(' ')
        stars_text_value = split_stars_array[1].lower()
        if stars_text_value == "zero":
            adapter['stars'] = 0
        elif stars_text_value == "one":
            adapter['stars'] = 1
        elif stars_text_value == "two":
            adapter['stars'] = 2
        elif stars_text_value == "three":
            adapter['stars'] = 3
        elif stars_text_value == "four":
            adapter['stars'] = 4
        elif stars_text_value == "five":
            adapter['stars'] = 5            

        return item
