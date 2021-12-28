from django.shortcuts import render
from django.db.models import Max, Min

from bokeh.models import ColumnDataSource, NumeralTickFormatter, HoverTool
from bokeh.embed import components
from bokeh.plotting import figure

from .models import GDP

import math

# Create your views here.
def index(request):
    # Define which year we want data from
    max_year = GDP.objects.aggregate(max_yr=Max('year'))['max_yr']
    min_year = GDP.objects.aggregate(min_yr=Min('year'))['min_yr']
    year = request.GET.get('year', max_year)

    # Define number of countries to fetch 
    count = int(request.GET.get('count', 10))
    
    gdps = GDP.objects.filter(year=year).order_by('gdp').reverse()[:count]

    country_names = [d.country for d in gdps]
    country_gdps = [d.gdp for d in gdps]

    cds = ColumnDataSource(data=dict(country_names=country_names, country_gdps=country_gdps))

    fig = figure(x_range=country_names, height=500, title=f"Top {count} GDPs ({year})")
    fig.title.align = 'center'
    fig.title.text_font_size = '1.5em'
    fig.yaxis[0].formatter = NumeralTickFormatter(format="$0.0a")
    fig.xaxis.major_label_orientation = math.pi / 4

    fig.vbar(source=cds, x='country_names', top='country_gdps', width=0.8)

    tooltips = [
        ('Country', '@country_names'),
        ('GDP', '@country_gdps')
    ]

    fig.add_tools(HoverTool(tooltips=tooltips))

    script, div = components(fig)

    context = {
        'script': script,
        'div': div,
        'years': range(min_year, max_year + 1),
        'count': count,
        'year_selected': year,
    }

    if request.htmx:
        return render(request, 'partials/gdp-bar.html', context)

    return render(request, 'index.html', context)


def line(request):
    countries = GDP.objects.values_list('country', flat=True).distinct()
    country = request.GET.get('country', 'Germany')

    gdps = GDP.objects.filter(country=country).order_by('year')

    country_years = [d.year for d in gdps]
    country_gdps = [d.gdp for d in gdps]

    cds = ColumnDataSource(data=dict(country_years=country_years, country_gdps=country_gdps))

    fig = figure(height=500, title=f"{country} GDP")
    fig.title.align = 'center'
    fig.title.text_font_size = '1.5em'
    fig.yaxis[0].formatter = NumeralTickFormatter(format="$0.0a")
    
    fig.line(source=cds, x='country_years', y='country_gdps', line_width=2)

    script, div = components(fig)

    context = {}
    context['countries'] = countries
    context['country'] = country
    context['script'] = script
    context['div'] = div

    if request.htmx:
        return render(request, 'partials/gdp-bar.html', context)

    return render(request, 'line.html', context)


def multi(request):
    countries = GDP.objects.values_list('country', flat=True).distinct()
    country_1 = request.GET.get('country_1', 'Germany')
    country_2 = request.GET.get('country_2', 'China')
    country_3 = request.GET.get('country_3', 'France')

    year_data = []
    gdp_data = []
    c = [country_1, country_2, country_3]

    for country in c:
        gdps = GDP.objects.filter(country=country).order_by('year')
        year_data.append([d.year for d in gdps])
        gdp_data.append([d.gdp for d in gdps])

    cds = ColumnDataSource(data=dict(
        country_years=year_data, 
        country_gdps=gdp_data,
        names=c,
        colors=['red', 'blue', 'green']
        ))

    fig = figure(height=500, title=f"{country} GDP")
    fig.title.align = 'center'
    fig.title.text_font_size = '1.5em'
    fig.yaxis[0].formatter = NumeralTickFormatter(format="$0.0a")
    
    fig.multi_line(
        source=cds, 
        xs='country_years', 
        ys='country_gdps', 
        line_width=2,
        legend_group='names',
        line_color='colors')

    fig.legend.location = 'top_left'

    script, div = components(fig)

    context = {}
    context['countries'] = countries
    context['c1'] = country_1
    context['c2'] = country_2
    context['c3'] = country_3
    context['script'] = script
    context['div'] = div

    if request.htmx:
        return render(request, 'partials/gdp-bar.html', context)
        
    return render(request, 'multiline.html', context)