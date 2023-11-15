from django.db import models
from django.utils.timezone import now


# Create your models here.


# <HINT> Create a Car Make model `class CarMake(models.Model)`:
# - Name
# - Description
# - Any other fields you would like to include in car make model
# - __str__ method to print a car make object
class CarMake(models.Model):
    name = models.CharField(null=False, max_length=64, default="Unknown")
    description = models.CharField(max_length=128)

    def __str__(self):
        return self.name


# <HINT> Create a Car Model model `class CarModel(models.Model):`:
# - Many-To-One relationship to Car Make model (One Car Make has many Car Models, using ForeignKey field)
# - Name
# - Dealer id, used to refer a dealer created in cloudant database
# - Type (CharField with a choices argument to provide limited choices such as Sedan, SUV, WAGON, etc.)
# - Year (DateField)
# - Any other fields you would like to include in car model
# - __str__ method to print a car make object
class CarModel(models.Model):
    car_make = models.ForeignKey(CarMake, on_delete=models.CASCADE)
    name = models.CharField(max_length=64)
    dealer_id = models.IntegerField()
    type = models.CharField(max_length=64)
    year = models.DateField(default=now)

    def __str__(self):
        return self.name


# <HINT> Create a plain Python class `CarDealer` to hold dealer data
class CarDealer:
    def __init__(
        self,
        _id,
        _rev,
        address,
        city,
        full_name,
        id,
        lat,
        long,
        short_name,
        st,
        state,
        zip,
    ):
        self._id = _id
        self._rev = _rev
        self.address = address
        self.city = city
        self.full_name = full_name
        self.id = id
        self.lat = lat
        self.long = long
        self.short_name = short_name
        self.st = st
        self.state = state
        self.zip = zip

    def __str__(self):
        return self.full_name


# <HINT> Create a plain Python class `DealerReview` to hold review data
class DealerReview:
    def __init__(
        self,
        _id,
        _rev,
        dealership,
        id,
        name,
        review,
        purchase,
        purchase_date,
        car_make,
        car_model,
        car_year,
        sentiment,
    ):
        self._id = _id
        self._rev = _rev
        self.dealership = dealership
        self.id = id
        self.name = name
        self.review = review
        self.purchase = purchase
        self.purchase_date = purchase_date
        self.car_make = car_make
        self.car_model = car_model
        self.car_year = car_year
        self.sentiment = sentiment

    def __str__(self):
        return self.name
