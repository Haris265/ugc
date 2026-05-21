from django.db import models

class IndustryChoices(models.IntegerChoices):
    FASHION = 1, 'Fashion'
    TECHNOLOGY = 2, 'Technology'
    FOOD_BEVERAGE = 3, 'Food & Beverage'
    HEALTH_WELLNESS = 4, 'Health & Wellness'
    BEAUTY = 5, 'Beauty'
    SPORTS = 6, 'Sports'
    TRAVEL = 7, 'Travel'
    FINANCE = 8, 'Finance'
    OTHER = 9, 'Other'


class CompanySizeChoices(models.IntegerChoices):
    SIZE_1_10 = 1, '1–10 employees'
    SIZE_11_50 = 2, '11–50 employees'
    SIZE_51_200 = 3, '51–200 employees'
    SIZE_200_PLUS = 4, '200+ employees'



class CampaignStatusChoices(models.IntegerChoices):
    LIVE = 1, 'Live'
    CLOSED = 2, 'Closed'
    DRAFT = 3, 'Draft'





