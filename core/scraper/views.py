import requests
import cssutils
import re 
from django.shortcuts import render, redirect
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from reports.models import WebsiteReport, PageReport, ImageReport, VideoReport, CarbonFootprintReport
from django.core.exceptions import ValidationError
from django.core.validators import URLValidator

class WebParser:
    def __init__(self, user, url):
        self.user = user
        self.url = url
        self.soup = self.parse_web_page()
    
    def parse_web_page(self):
        response = requests.get(self.url)
        soup = BeautifulSoup(response.content, 'html.parser')
        return soup

    def calculate_carbon_footprint(self, size_in_kb):
        CARBON_INTENSITY = 441.3  # estimated grams of CO2e per kilowatt-hour
        GIGABYTE_TO_BYTES = 1073741824
        AVERAGE_KILO_WATT_HOUR_PER_GB = 1.805

        size_in_bytes = size_in_kb * 1024  # Convert size from KB to bytes
        energy_usage = size_in_bytes * (AVERAGE_KILO_WATT_HOUR_PER_GB / GIGABYTE_TO_BYTES)  
        
        # in kilowatt-hours
        carbon_footprint = energy_usage * CARBON_INTENSITY  # in kilograms of CO2e
        return energy_usage, carbon_footprint
    
    # Get background images from CSS
    def get_background_images(self):
        css = cssutils.parseString(self.soup.text)
        background_images = []
        for rule in css:
            if rule.type == rule.STYLE_RULE:
                style = rule.style
                if 'background-image' in style:
                    bg_img = style['background-image']
                    url_match = re.search(r'url\((.*?)\)', bg_img)
                    if url_match:
                        background_images.append(url_match.group(1))
        return background_images
    
    def get_resource_size(self, resource_url, unit='KB'):
        absolute_url = urljoin(self.url, resource_url)
        response = requests.head(absolute_url)
        content_length = response.headers.get('Content-Length', 0)
        size_in_bytes = int(content_length)

        if unit.upper() == 'MB':
            size_in_mb = size_in_bytes / (1024 * 1024)
            return size_in_mb
        elif unit.upper() == 'KB':
            size_in_kb = size_in_bytes / 1024
            return size_in_kb
        else:
            raise ValueError("Invalid unit. Supported units are 'KB' and 'MB'.")

    def calculate_score(self, carbon_footprint, max_carbon_footprint=100):
        score = max(0, 100 * (1 - carbon_footprint / max_carbon_footprint))
        return score
        
    def scrape_page(self):
        page_size = 0.0
        num_images = 0
        num_videos = 0
        total_js_size = 0
        total_css_size = 0
        total_image_size = 0.0
        total_video_size = 0.0

        website_report = WebsiteReport.objects.create(
            user = self.user,
            url = self.url,
            pages = len(self.soup.find_all('a')),
        )

        num_images += len(self.soup.find_all('img')) + len(self.get_background_images()) + len(self.soup.find_all('svg'))

        for img_tag in self.soup.find_all('img'):
            img_url = img_tag.get('src', '')
            img_size = self.get_resource_size(img_url)
            total_image_size += img_size
            page_size += img_size

        for img_url in self.get_background_images():
            img_size = self.get_resource_size(img_url)
            total_image_size += img_size
            page_size += img_size

        for svg_tag in self.soup.find_all('svg'):
            svg_size = self.get_resource_size(str(svg_tag))
            total_image_size += svg_size
            page_size += svg_size

        for video_tag in self.soup.find_all('video'):
            video_url = video_tag.get('src', '')
            video_size = self.get_resource_size(video_url)
            if video_size > 0:
                total_video_size += video_size
                page_size += video_size
                num_videos += 1
        
        # count youtube video embeds
        for iframe_tag in self.soup.find_all('iframe'):
            iframe_src = iframe_tag.get('src', '')
            if 'youtube.com' in iframe_src:
                video_size = self.get_resource_size(iframe_src)
                if video_size > 0:
                    total_video_size += video_size
                    page_size += video_size
                    num_videos += 1
        
        # Calculate CSS size
        for link_tag in self.soup.find_all('link', rel='stylesheet'):
            css_url = link_tag.get('href', '')
            css_size = self.get_resource_size(css_url)
            total_css_size += css_size
            page_size += css_size

        # Calculate JS size
        for script_tag in self.soup.find_all('script'):
            js_url = script_tag.get('src', '')
            if js_url:  # External JS file
                js_size = self.get_resource_size(js_url)
                total_js_size += js_size
                page_size += js_size
            else:  # Inline JS
                js_size = self.get_resource_size(str(script_tag))
                total_js_size += js_size
                page_size += js_size

        page_report = PageReport.objects.create(
            user = self.user,
            website = website_report,
            page_size = page_size,
            num_images = num_images,
            num_videos = num_videos,
            num_external_resources = len(self.soup.find_all('link')),
            num_internal_links = len(self.soup.find_all('a', href=self.url)),
            num_external_links = len(self.soup.find_all('a', href=lambda x: x and self.url not in x)),
            num_social_media_links = len(self.soup.find_all('a', href=lambda x: x and 'social' in x)),
        )

        ImageReport.objects.create(
            user = self.user,
            page = page_report,
            total_size = total_image_size,
            format = "jpeg",  
        )

        VideoReport.objects.create(
            user = self.user,
            page = page_report,
            total_size = total_video_size,
            format = "mp4",  
        )

        total_energy_usage, _ = self.calculate_carbon_footprint(page_size)
        _, carbon_footprint_images = self.calculate_carbon_footprint(total_image_size)
        _, carbon_footprint_videos = self.calculate_carbon_footprint(total_video_size)
        _, carbon_footprint_other = self.calculate_carbon_footprint(page_size - total_image_size - total_video_size)

        carbon_footprint_score, _ = self.calculate_carbon_footprint(page_size)

        CarbonFootprintReport.objects.create(
            user=self.user,
            page=page_report,
            total_energy_usage=total_energy_usage,
            carbon_footprint_score=carbon_footprint_score,
            carbon_footprint_images=carbon_footprint_images,
            carbon_footprint_videos=carbon_footprint_videos,
            carbon_footprint_other=carbon_footprint_other,
        )

        # Set the computed page_size in the PageReport model, then save it
        page_report.page_size = page_size
        page_report.save()

def analyze(request):    
    # user must be logged in to access this page
    if not request.user.is_authenticated:
        return redirect('login')
    # if the user is logged in and the request is POST, then scrape the page
    if request.method == 'POST':
        url = request.POST.get('url')
        url = 'https://' + url if not url.startswith('https') else url
        # Validate the URL
        validate = URLValidator()
        try:
            validate(url)
        except ValidationError:
            return render(request, 'scraper/scrape.html', {'error': 'Invalid URL'})
        web_parser = WebParser(request.user, url)
        web_parser.scrape_page()
        return redirect('list_website_reports')
    return render(request, 'scraper/scrape.html')
