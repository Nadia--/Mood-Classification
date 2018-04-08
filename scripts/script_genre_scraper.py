# Project Libraries
from genre_scraper import scrape_genres
from genre_scraper import WeightType

# General Libraries


BASEDIR = '../../../../Thesis/data_sample/W/I/D'
tags = scrape_genres(BASEDIR, WeightType.BINARY)
tags_by_frequency = scrape_genres(BASEDIR, WeightType.FREQUENCY)
tags_by_weight = scrape_genres(BASEDIR, WeightType.WEIGHT)


print("\nMost Popular Tags")
print(tags[:100])

print("\nMost Popular Tag Frequencies")
print(tags_by_frequency[:100])

print("\nMost Popular Tag Weights")
print(tags_by_weight[:100])
