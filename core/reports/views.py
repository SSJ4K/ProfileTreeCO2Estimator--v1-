from datetime import datetime, timedelta
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Sum

# Plotly for graphing
from plotly.offline import plot
import plotly.graph_objs as go

from .models import WebsiteReport, PageReport,CarbonFootprintReport, HostingProvider

@login_required
def list_website_reports(request):
    user = request.user
    website_reports = WebsiteReport.objects.filter(user=user).order_by('-created_at')

    # Pagination
    page = request.GET.get('page', 1)
    paginator = Paginator(website_reports, 5) 
    try:
        website_reports_page = paginator.page(page)
    except PageNotAnInteger:
        website_reports_page = paginator.page(1)
    except EmptyPage:
        website_reports_page = paginator.page(paginator.num_pages)

    # Create a range of page numbers for numeric pagination
    page_range = range(max(1, website_reports_page.number - 2), min(website_reports_page.number + 3, paginator.num_pages + 1))

    return render(request, 'reports/list_website_reports.html', {'website_reports': website_reports_page, 'page_range': page_range})

@login_required
def delete_website_report(request, report_id):
    user = request.user
    website_report = get_object_or_404(WebsiteReport, id=report_id, user=user)

    if request.method == 'POST':
        # Ensure that only the user who created the report can delete it
        if website_report.user == user:
            website_report.delete()
            return redirect('list_website_reports')
        else:
            # Redirect or handle the case where the user is not allowed to delete the report
            return redirect('list_website_reports')  

    return render(request, 'reports/delete_website_report.html', {'website_report': website_report})

@login_required(login_url='login')
def show_website_report(request, report_id):
    user = request.user

    # Get the website report by ID
    try:
        website = WebsiteReport.objects.get(id=report_id, user=user)
    except WebsiteReport.DoesNotExist:
        return HttpResponse('Website report not found', status=404)

    # Get the CarbonFootprintReport for the website
    carbon_footprint_report = CarbonFootprintReport.objects.get(page__website=website)

    bar_chart_data = generate_bar_chart_data(website)
    bar_chart_layout = generate_bar_chart_layout()

    pie_chart_data = generate_pie_chart_data(website)
    pie_chart_layout = generate_pie_chart_layout()

    carbon_footprint_chart_data = generate_carbon_footprint_chart_data(carbon_footprint_report)
    carbon_footprint_chart_layout = generate_carbon_footprint_chart_layout()

    # Get the top 3 websites with the highest total energy usage
    top_three_websites = CarbonFootprintReport.objects.filter(user=user).order_by('-total_energy_usage')[:3]

    # Generate the bar chart for the top 3 websites
    top_websites_bar_chart_data = generate_top_websites_bar_chart_data(top_three_websites)
    top_websites_bar_chart_layout = generate_top_websites_bar_chart_layout()


    # Get the CO2 scores for all the user's websites over the last 30 days
    thirty_days_ago = datetime.now() - timedelta(days=30)
    co2_reports = CarbonFootprintReport.objects.filter(user=user, created_at__gte=thirty_days_ago)

    # Generate the line chart for the CO2 scores
    co2_line_chart_data = generate_co2_line_chart_data(co2_reports)
    co2_line_chart_layout = generate_co2_line_chart_layout()

    # Get 5 random hosting providers
    hosting_providers = HostingProvider.objects.order_by('?')[:5]

    return render(request, 'reports/show_website_report.html', {
        'website': website,
        'carbon_footprint_report': carbon_footprint_report,
        'bar_chart_data': plot(go.Figure(data=[bar_chart_data], layout=bar_chart_layout), output_type='div'),
        'carbon_footprint_chart_data': plot(go.Figure(data=[carbon_footprint_chart_data], layout=carbon_footprint_chart_layout), output_type='div'),
        'pie_chart_data': plot(go.Figure(data=[pie_chart_data], layout=pie_chart_layout), output_type='div'),
        'top_websites_bar_chart_data': plot(go.Figure(data=[top_websites_bar_chart_data], layout=top_websites_bar_chart_layout), output_type='div'),
        'co2_line_chart_data': plot(go.Figure(data=[co2_line_chart_data], layout=co2_line_chart_layout), output_type='div'),
        'hosting_providers': hosting_providers,
    })

def generate_top_websites_bar_chart_data(carbon_footprint_reports):
    return go.Bar(
        x=[report.page.website.url for report in carbon_footprint_reports],
        y=[report.total_energy_usage for report in carbon_footprint_reports],
        name='Top 3 Websites by Energy Usage'
    )

def generate_top_websites_bar_chart_layout():
    return go.Layout(
        title='Top 3 Websites by Energy Usage',
        xaxis=dict(title='Website'),
        yaxis=dict(title='Total Energy Usage (kWh)'),
        template='plotly_dark'
    )

def generate_bar_chart_data(website):
    return go.Bar(
        x=['Internal Links', 'External Links', 'External Resources', 'Social Media Links', 'Images', 'Videos'],
        y=[
            PageReport.objects.filter(website=website).aggregate(Sum('num_internal_links'))['num_internal_links__sum'],
            PageReport.objects.filter(website=website).aggregate(Sum('num_external_links'))['num_external_links__sum'],
            PageReport.objects.filter(website=website).aggregate(Sum('num_external_resources'))['num_external_resources__sum'],
            PageReport.objects.filter(website=website).aggregate(Sum('num_social_media_links'))['num_social_media_links__sum'],
            PageReport.objects.filter(website=website).aggregate(Sum('num_images'))['num_images__sum'],
            PageReport.objects.filter(website=website).aggregate(Sum('num_videos'))['num_videos__sum'],
        ],
        name='Page Statistics'
    )

def generate_bar_chart_layout():
    return go.Layout(
        title='Page Statistics',
        xaxis=dict(title='Link Type'),
        yaxis=dict(title='Count'),
        template='plotly_dark'
    )

def generate_pie_chart_data(website):
    return go.Pie(
        labels=['Internal Links', 'External Links', 'External Resources', 'Social Media Links', 'Images', 'Videos'],
        values=[
            PageReport.objects.filter(website=website).aggregate(Sum('num_internal_links'))['num_internal_links__sum'],
            PageReport.objects.filter(website=website).aggregate(Sum('num_external_links'))['num_external_links__sum'],
            PageReport.objects.filter(website=website).aggregate(Sum('num_external_resources'))['num_external_resources__sum'],
            PageReport.objects.filter(website=website).aggregate(Sum('num_social_media_links'))['num_social_media_links__sum'],
            PageReport.objects.filter(website=website).aggregate(Sum('num_images'))['num_images__sum'],
            PageReport.objects.filter(website=website).aggregate(Sum('num_videos'))['num_videos__sum'],
        ]
    )

def generate_pie_chart_layout():
    return go.Layout(
        title='Link Distribution',
        template='plotly_dark'
    )

def generate_carbon_footprint_chart_data(carbon_footprint_report):
    return go.Bar(
        x=['Images', 'Videos', 'Other'],
        y=[
            carbon_footprint_report.carbon_footprint_images,
            carbon_footprint_report.carbon_footprint_videos,
            carbon_footprint_report.carbon_footprint_other
        ],
        name='Carbon Footprint'
    )

def generate_carbon_footprint_chart_layout():
    return go.Layout(
        title='Carbon Footprint',
        xaxis=dict(title='Resource Type'),
        yaxis=dict(title='Carbon Footprint (kg)'),
        template='plotly_dark'
    )

def generate_co2_line_chart_data(co2_reports):
    return go.Scatter(
        x=[report.created_at for report in co2_reports],
        y=[report.carbon_footprint_score for report in co2_reports],
        mode='lines+markers',
        name='CO2 Scores Over Time'
    )

def generate_co2_line_chart_layout():
    return go.Layout(
        title='CO2 Scores Over Time',
        xaxis=dict(title='Date'),
        yaxis=dict(title='Total CO2 (kg)'),
        template='plotly_dark'
    )