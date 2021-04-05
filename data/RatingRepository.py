import csv
import statistics
import json

from APM_ramen_ratings.models.Rating import Rating


class RatingRepository:
    def __init__(self):
        self.ratings = self.read_ratings()

    def read_ratings(self):
        ratings = []
        with open('../assets/ramen-ratings.csv', newline='', encoding='UTF-8') as csvfile:
            spamreader = csv.reader(csvfile, delimiter=',')
            next(spamreader)
            for row in spamreader:
                ratings.append(Rating(row[0], row[1], row[2], row[3], row[4], row[5]))
        return ratings

    def get_brands(self):
        brands = []
        [brands.append(rt.brand) for rt in self.ratings if rt.brand not in brands]
        return brands

    def get_countries(self):
        countries = []
        [countries.append(rt.country) for rt in self.ratings if rt.country not in countries]
        return countries

    def get_filtered_ratings(self, filters):
        response = self.ratings
        if filters['brand'] != 'brand':
            response = [rt for rt in self.ratings if rt.brand == filters['brand']]
        if filters['country'] != 'country':
            response = [rt for rt in response if rt.country == filters['country']]
        if filters['min_rating']:
            response = [rt for rt in response if float(rt.rating) >= filters['min_rating']]
        response = [rt.__dict__ for rt in response]
        return response

    def get_mean_ratings_brand(self, brand):
        return round(statistics.mean([float(rt.rating) for rt in self.ratings if rt.brand == brand]),2)


# ratings = RatingRepository()
# print(ratings.get_brands())
# print(ratings.get_countries())
# print([rt['review_number'] for rt in ratings.get_filtered_ratings({'brand': 'Nissin', 'country': 'Japan', 'min_rating': 3.75})])
# print(ratings.get_mean_ratings_brand('Nissin'))