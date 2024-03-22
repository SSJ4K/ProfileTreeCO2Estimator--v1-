from django.contrib import admin
from .models import WebsiteReport, PageReport, ImageReport, VideoReport, CarbonFootprintReport, Recommendation, HostingProvider

admin.site.register([
    WebsiteReport, 
    PageReport, 
    ImageReport, 
    VideoReport, 
    CarbonFootprintReport, 
    Recommendation, 
    HostingProvider
])