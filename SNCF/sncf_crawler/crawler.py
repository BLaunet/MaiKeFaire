from city import City

class SncfCrawler:
    def __init__(self, origin, destination, discountCard=None):
        self.origin = City(origin)
        self.destination = City(destination)
        self.discountCard = discountCard
