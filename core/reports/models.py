from django.db import models
from django.contrib.auth.models import User

class WebsiteReport(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    url = models.URLField()
    pages = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.url} - {self.id} - {self.user.username}"

class PageReport(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    website = models.ForeignKey(WebsiteReport, on_delete=models.CASCADE)
    page_size = models.FloatField()  # in megabytes
    num_images = models.IntegerField()
    num_videos = models.IntegerField()
    num_external_resources = models.IntegerField()
    num_internal_links = models.IntegerField()
    num_external_links = models.IntegerField()
    num_social_media_links = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.website.url} - {self.user.username} - Page {self.id}"

class ImageReport(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    page = models.ForeignKey(PageReport, on_delete=models.CASCADE)
    total_size = models.FloatField()  # in kilobytes
    format = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Image {self.id} - {self.page}"

class VideoReport(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    page = models.ForeignKey(PageReport, on_delete=models.CASCADE)
    total_size = models.FloatField()  # in megabytes
    format = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Video {self.id} - {self.page}"

class CarbonFootprintReport(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    page = models.ForeignKey(PageReport, on_delete=models.CASCADE)
    total_energy_usage = models.FloatField()  # in kilowatt-hours
    carbon_footprint_score = models.FloatField(default=0.0)
    carbon_footprint_images = models.FloatField()  # in kilograms of CO2e
    carbon_footprint_videos = models.FloatField()  # in kilograms of CO2e
    carbon_footprint_other = models.FloatField()  # in kilograms of CO2e
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"CarbonFootprint {self.id} - {self.page}"

class Recommendation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    page = models.OneToOneField(PageReport, on_delete=models.CASCADE)
    recommendation_text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Recommendation {self.id} - {self.page}"

class HostingProvider(models.Model):
    name = models.CharField(max_length=100)
    sustainability_info = models.TextField(default='No sustainability information available.')
    url = models.URLField(default='https://www.google.com')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"HostingProvider {self.id} - {self.name}"
