import hashlib
import uuid

from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.utils import timezone
from django.utils.safestring import mark_safe

from core.authentication.models import Address, ProfileUser


class Brand(models.Model):
    name = models.CharField(max_length=255)
    image = models.ImageField(upload_to="brand/")

    def __str__(self):
        return self.name

    def image_preview(self):
        return mark_safe('<img src="%s"/>' % self.image.url)

    image_preview.allow_tags = True


class Car(models.Model):

    class FuelTypes(models.TextChoices):
        GASOLINE = "Gasoline"
        DIESEL = "Diesel"
        PROPANE = "Propane"
        CNG = "CNG"
        ETHANOL = "Ethanol"
        BIODIESEL = "Bio-diesel"

    name = models.CharField(max_length=255)
    image = models.ImageField(upload_to="car/")
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE)
    passengers = models.IntegerField()
    doors = models.IntegerField()
    has_air_conditioning = models.BooleanField()
    has_power_locks = models.BooleanField()
    has_power_windows = models.BooleanField()
    fuel_type = models.CharField(
        max_length=20,
        choices=FuelTypes.choices,
        default=FuelTypes.GASOLINE,
    )
    is_automatic = models.BooleanField()
    horsepower = models.IntegerField()
    top_speed = models.IntegerField()
    acceleration_0_100 = models.DecimalField(max_digits=4, decimal_places=2)
    model_year = models.IntegerField()

    def __str__(self):
        return self.name + f"({self.brand.name})"

    def image_preview(self):
        return mark_safe('<img src="%s" height="200px"/>' % self.image.url)

    image_preview.allow_tags = True


class Rental(models.Model):
    class RentType(models.TextChoices):
        DAILY = "Daily"
        WEEKLY = "Weekly"
        MONTHLY = "Monthly"
        YEARLY = "Yearly"

    owner = models.ForeignKey(ProfileUser, on_delete=models.CASCADE)
    car = models.ForeignKey(Car, on_delete=models.CASCADE)
    rent_type = models.CharField(
        max_length=20, choices=RentType.choices, default=RentType.WEEKLY
    )
    rent_value = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(default=timezone.now, editable=False)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.owner} - {self.car}"

    def save(self, *args, **kwargs):
        self.updated_at = timezone.now()
        super(Rental, self).save(*args, **kwargs)


class Review(models.Model):

    reviewer = models.ForeignKey(ProfileUser, on_delete=models.CASCADE)
    rental = models.ForeignKey(Rental, on_delete=models.CASCADE)
    stars = models.DecimalField(max_length=2, decimal_places=1, max_digits=2)
    comment = models.CharField(max_length=50)
    created_at = models.DateTimeField(default=timezone.now, editable=False)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        self.updated_at = timezone.now()
        super(Review, self).save(*args, **kwargs)

    def __str__(self):
        return f"{self.reviewer} [{self.rental}]"


class Favorite(models.Model):

    owner = models.ForeignKey(ProfileUser, on_delete=models.CASCADE)
    rental = models.ForeignKey(Rental, on_delete=models.CASCADE)
    created_at = models.DateTimeField(default=timezone.now, editable=False)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        self.updated_at = timezone.now()
        super(Favorite, self).save(*args, **kwargs)

    def __str__(self):
        return f"{self.user} [{self.rental}]"


class Payment(models.Model):

    class Type(models.TextChoices):
        CREDIT_CARD = "Credit Card"
        DEBIT_CARD = "Debit Card"
        CASH = "Cash"

    class Status(models.TextChoices):
        PENDING = "Pending"
        COMPLETED = "Completed"
        CANCELLED = "Cancelled"
        FAILED = "Failed"

    owner = models.ForeignKey(
        ProfileUser, on_delete=models.CASCADE, related_name="payment_owner"
    )
    receiver = models.ForeignKey(
        ProfileUser, on_delete=models.CASCADE, related_name="payment_receiver"
    )

    payment_type = models.CharField(
        max_length=20, choices=Type.choices, default=Type.CREDIT_CARD
    )
    payment_hash = models.CharField(
        primary_key=True,
        max_length=100,
        editable=False,
    )
    payment_status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.PENDING
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(blank=True)
    bill_date = models.DateTimeField()
    created_at = models.DateTimeField(default=timezone.now, editable=False)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Payment HASH: {self.payment_hash}"

    def save(self, *args, **kwargs):
        if not self.payment_hash:
            self.payment_hash = hashlib.sha256(uuid.uuid4().bytes).hexdigest()
        self.updated_at = timezone.now()
        super(Payment, self).save(*args, **kwargs)


class Booking(models.Model):

    renter = models.ForeignKey(ProfileUser, on_delete=models.CASCADE)
    rental = models.ForeignKey(Rental, on_delete=models.CASCADE)
    location = models.ForeignKey(Address, on_delete=models.CASCADE)
    rent_date = models.DateTimeField()
    return_date = models.DateTimeField()
    payments = models.ManyToManyField(Payment)
    created_at = models.DateTimeField(default=timezone.now, editable=False)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        self.updated_at = timezone.now()
        super(Booking, self).save(*args, **kwargs)

    def __str__(self):
        return f"{self.id} [{self.renter} - {self.rental}]"