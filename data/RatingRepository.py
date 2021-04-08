import csv
import statistics
import json
import pandas as pd

from APM_ramen_ratings.models.Rating import Rating


class RatingRepository:
    def __init__(self):
        self.ratings = self.read_ratings()

    def read_ratings(self):
        # ratings = []
        # with open('../assets/ramen-ratings.csv', newline='', encoding='UTF-8') as csvfile:
        #     spamreader = csv.reader(csvfile, delimiter=',')
        #     next(spamreader)
        #     for row in spamreader:
        #         if row[5] != 'Unrated':
        #             ratings.append(Rating(row[0], row[1], row[2], row[3], row[4], row[5]))
        ratings = pd.read_csv("../assets/ramen-ratings.csv")
        print(ratings.values)
        return ratings.values

    def get_brands(self):
        brands = []
        [brands.append(rt[1]) for rt in self.ratings if rt[1] not in brands]
        return brands

    def get_countries(self):
        countries = []
        [countries.append(rt[4]) for rt in self.ratings if rt[4] not in countries]
        return countries

    def get_filtered_ratings(self, filters):
        response = self.ratings
        if filters['brand'] != 'brand':
            response = [rt for rt in self.ratings if rt[1] == filters['brand']]
        if filters['country'] != 'country':
            response = [rt for rt in response if rt[4] == filters['country']]
        if filters['min_rating']:
            response = [rt for rt in response if float(rt[5]) >= filters['min_rating']]
        return response

    def get_mean_ratings_brand(self, brand, country):
        return round(statistics.mean([float(rt.rating) for rt in self.ratings if rt[1] == brand and rt[4] == country]),2)

    def search_ratings(self, search):
        return [rt.variety for rt in self.ratings if search in rt.variety]


# ratings = RatingRepository()
# print(ratings.get_brands())
# print(ratings.get_countries())
# print([rt[5] for rt in ratings.get_filtered_ratings({'brand': 'Nissin', 'country': 'Japan', 'min_rating': 3.75})])
# print(ratings.get_mean_ratings_brand('Nissin'))
# print(ratings.search_ratings('spicy'))