import csv
import statistics
import json
import pandas as pd

from APM_ramen_ratings.models.Rating import Rating


def read_ratings():
    ratings = pd.read_csv("../assets/ramen-ratings.csv")
    ratings = ratings[ratings['Stars'] != 'Unrated']
    return ratings.values


class RatingRepository:
    def __init__(self):
        self.ratings = read_ratings()

    def get_brands(self):
        brands = []
        [brands.append(rt[1]) for rt in self.ratings if rt[1] not in brands]
        return sorted(brands)

    def get_countries(self):
        countries = []
        [countries.append(rt[4]) for rt in self.ratings if rt[4] not in countries]
        return sorted(countries)

    def get_filtered_ratings(self, filters):
        response = self.ratings
        if filters['brand'] != 'brand':
            response = [rt for rt in self.ratings if rt[1] == filters['brand']]
        if filters['country'] != 'country':
            response = [rt for rt in response if rt[4] == filters['country']]
        if filters['min_rating']:
            response = [rt for rt in response if float(rt[5]) >= filters['min_rating']]
        return response

    def get_mean_brand_rating(self, brand, country):
        brands = self.get_brands()
        {rt[1]:  for rt[rt for rt in self.get_filtered_ratings([br for br in self.get_brands()])]}
        return round(statistics.mean([float(rt.rating) for rt in self.ratings if rt[1] == brand and rt[4] == country]), 2)

    def search_ratings(self, search):
        return [rt for rt in self.ratings if search.lower() in rt[2].lower()]

# ratings = RatingRepository()
# print(ratings.get_brands())
# print(ratings.get_countries())
# print([rt[5] for rt in ratings.get_filtered_ratings({'brand': 'Nissin', 'country': 'Japan', 'min_rating': 3.75})])
# print(ratings.get_mean_ratings_brand('Nissin'))
# print(ratings.search_ratings('spicy'))
