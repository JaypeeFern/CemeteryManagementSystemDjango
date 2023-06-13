from django.shortcuts import render, redirect
import folium
import geocoder
import pandas as pd
from search.models import DeceasedInformation
from django.db.models import Q
# Create your views here.

# Folium
# Map Render
def renderGraveLocator(request):
    
    url = (
    "locator/templates/locator/data"
    )
    
    lot_geo = f"{url}/map.geojson"
    lot_csv = f'{url}/testdata.csv'
    lot_data = pd.read_csv(lot_csv)
   
    data = geocoder.osm('Surigao Memorial Park')
    lat = data.lat 
    lng = data.lng
    
    m = folium.Map(location=[9.767206409981258, 125.49904571692107], zoom_start=17, max_zoom=17, min_zoom=14)
    
    style_function = lambda x: {
        'fillOpacity': 0.7, 'weight': 1, 'opacity': 0.5, 'color': '#000000',
        'fillColor': '#BDD9BF' if x['properties']['name'] == 'Garden of Peter' else '#00ff00' 
         and '#8dd3c7' if x['properties']['name'] == 'Garden of Paul' else '#00ff00'
         and '#ffffb3' if x['properties']['name'] == 'Garden of Andrew' else '#00ff00'
         and '#bebada' if x['properties']['name'] == 'Garden of James' else '#00ff00'
         and '#fb8072' if x['properties']['name'] == 'Garden of Philip' else '#00ff00'
         and '#80b1d3' if x['properties']['name'] == 'Garden of Nathaniel' else '#00ff00'
         and '#fdb462' if x['properties']['name'] == 'Garden of John' else '#00ff00'
         and '#b3de69' if x['properties']['name'] == 'Garden of Thomas' else '#00ff00'
         and '#fccde5' if x['properties']['name'] == 'Garden of Nicolas De Tolentino' else '#00ff00'
         and '#d9d9d9' if x['properties']['name'] == 'Garden of Joseph' else '#00ff00'
         and '#bc80bd' if x['properties']['name'] == 'Garden of Jude' else '#00ff00'
         and '#ccebc5' if x['properties']['name'] == 'Garden of Lorenzo Ruiz' else '#00ff00'
         and '#ffed6f' if x['properties']['name'] == 'Garden of Pedro Calungsod' else '#00ff00'
         and '#9e0142' if x['properties']['name'] == 'Garden of Mary' else '#00ff00'
         and '#1a9850' if x['properties']['name'] == 'Garden of Matthew' else '#00ff00'
         and '#543005' if x['properties']['name'] == 'Garden of Ignatius' else '#00ff00'
        }
    
    highlight_function = lambda x: {'fillColor': '#000000', 'color':'#000000', 'fillOpacity': 0.50, 'weight': 0.1}
    
    folium.GeoJson(lot_geo, name="geojson", style_function=style_function, highlight_function=highlight_function).add_to(m)
    folium.LayerControl().add_to(m)
    
    onHoverTooltip = folium.features.GeoJson(
        lot_geo,
        style_function=style_function,
        control=False,
        highlight_function=highlight_function,
        tooltip=folium.features.GeoJsonTooltip(
            fields=["name","lotnum"],
            aliases=['Lot Name: ','Lot Number: '],
            style=("background-color: white; color: #333333; font-family: arial; font-size: 12px; padding: 10px;") 
        )
    )
    
    m.add_child(onHoverTooltip)
    m.keep_in_front(m)
  
    # Marker Function
    
    if request.method == 'POST':
        z = request.POST['a']
        # data = DeceasedInformation.objects.filter(name__iexact=z)
        data = DeceasedInformation.objects.filter(id=z).values('name','location__grave_area')
        lotNames = {
            'lot1': 'Garden of Peter',
            'lot2':'Garden of Paul',
            'lot3':'Garden of Andrew',
            'lot4':'Garden of James',
            'lot5':'Garden of Philip',
            'lot6':'Garden of Nathanel',
            'lot7':'Garden of John',
            'lot8':'Garden of Thomas',
            'lot9':'Garden of Nicolas De Tolentino',
            'lot10':'Garden of Joseph',
            'lot11':'Garden of Jude',
            'lot12':'Garden of Lorenzo Ruiz',
            'lot13':'None',
            'lot14':'Garden of Pedro Calungsod',
            'lot15':'Garden of Mary',
            'lot16':'Garden of Matthew',
            'lot17':'Garden of Ignatius',
        }
        lotCoordinates = {
            'lot1': [9.767243416604591, 125.49654053369511],
            'lot2': [9.76694339148084, 125.49671085072434],
            'lot3': [9.767494429277574, 125.49703174187478],
            'lot4': [9.766965763152823, 125.49773984506957],
            'lot5': [9.767108277480373, 125.49905652765433],
            'lot6': [9.766939104223683, 125.49923355345639],
            'lot7': [9.767906562656655, 125.50051028484954],
            'lot8': [9.76742547711993, 125.49911017185333],
            'lot9': [9.767927709256048, 125.4991906381162],
            'lot10': [9.767251017359339, 125.50040299650408],
            'lot11': [9.766415723897579, 125.50030643699469],
            'lot12': [9.76819732830619, 125.50094480273268],
            'lot13': [0, 0],
            'lot14': [9.768681090642376, 125.50073831412882],
            'lot15': [9.76778103927861, 125.4982264254473],
            'lot16': [9.76503196862887, 125.49956752987396],
            'lot17': [9.766791077523944, 125.49547846101629]
            }
        
        lotDirections = {
            'lot1': '<a href=https://fr.wikipedia.org/wiki/Place_Guillaume_II></a>',
            'lot2': '',
            'lot3': '',
            'lot4': '',
            'lot5': '',
            'lot6': '',
            'lot7': '',
            'lot8': '',
            'lot9': '',
            'lot10': '',
            'lot11': '',
            'lot12': '',
            'lot13': '',
            'lot14': '',
            'lot15': '',
            'lot16': '',
            'lot17': '',
        }

        lot_name = 'location__grave_area'
        
        for data in data:
            if data[lot_name] == lotNames['lot1'].upper():    
                folium.Marker(lotCoordinates['lot1'], popup=lotDirections['lot1'], icon=folium.Icon(color='red',  icon='info-sign'),).add_to(m)
            if data[lot_name] == lotNames['lot2'].upper():
                folium.Marker(lotCoordinates['lot2'], popup=lotDirections['lot2'], icon=folium.Icon(color='red',  icon='info-sign'),).add_to(m)
            if data[lot_name] == lotNames['lot3'].upper():
                folium.Marker(lotCoordinates['lot3'], popup=lotDirections['lot3'], icon=folium.Icon(color='red',  icon='info-sign'),).add_to(m)
            if data[lot_name] == lotNames['lot4'].upper():
                folium.Marker(lotCoordinates['lot4'], popup=lotDirections['lot4'], icon=folium.Icon(color='red',  icon='info-sign'),).add_to(m)
            if data[lot_name] == lotNames['lot5'].upper():
                folium.Marker(lotCoordinates['lot5'], popup=lotDirections['lot5'], icon=folium.Icon(color='red',  icon='info-sign'),).add_to(m)
            if data[lot_name] == lotNames['lot6'].upper():
                folium.Marker(lotCoordinates['lot6'], popup=lotDirections['lot6'], icon=folium.Icon(color='red',  icon='info-sign'),).add_to(m)
            if data[lot_name] == lotNames['lot7'].upper():
                folium.Marker(lotCoordinates['lot7'], popup=lotDirections['lot7'], icon=folium.Icon(color='red',  icon='info-sign'),).add_to(m)
            if data[lot_name] == lotNames['lot8'].upper():
                folium.Marker(lotCoordinates['lot8'], popup=lotDirections['lot8'], icon=folium.Icon(color='red',  icon='info-sign'),).add_to(m)
            if data[lot_name] == lotNames['lot9'].upper():
                folium.Marker(lotCoordinates['lot9'], popup=lotDirections['lot9'], icon=folium.Icon(color='red',  icon='info-sign'),).add_to(m)
            if data[lot_name] == lotNames['lot10'].upper():
                folium.Marker(lotCoordinates['lot10'], popup=lotDirections['lot10'], icon=folium.Icon(color='red',  icon='info-sign'),).add_to(m)
            if data[lot_name] == lotNames['lot11'].upper():
                folium.Marker(lotCoordinates['lot11'], popup=lotDirections['lot11'], icon=folium.Icon(color='red',  icon='info-sign'),).add_to(m)
            if data[lot_name] == lotNames['lot12'].upper():
                folium.Marker(lotCoordinates['lot12'], popup=lotDirections['lot12'], icon=folium.Icon(color='red',  icon='info-sign'),).add_to(m)
            if data[lot_name] == lotNames['lot13'].upper():
                folium.Marker(lotCoordinates['lot13'], popup=lotDirections['lot13'], icon=folium.Icon(color='red',  icon='info-sign'),).add_to(m)
            if data[lot_name] == lotNames['lot14'].upper():
                folium.Marker(lotCoordinates['lot14'], popup=lotDirections['lot14'], icon=folium.Icon(color='red',  icon='info-sign'),).add_to(m)
            if data[lot_name] == lotNames['lot15'].upper():
                folium.Marker(lotCoordinates['lot15'], popup=lotDirections['lot15'], icon=folium.Icon(color='red',  icon='info-sign'),).add_to(m)
            if data[lot_name] == lotNames['lot16'].upper():
                folium.Marker(lotCoordinates['lot16'], popup=lotDirections['lot16'], icon=folium.Icon(color='red',  icon='info-sign'),).add_to(m)
            if data[lot_name] == lotNames['lot17'].upper():
                folium.Marker(lotCoordinates['lot17'], popup=lotDirections['lot17'], icon=folium.Icon(color='red',  icon='info-sign'),).add_to(m)
            
        
    # Output
    m = m._repr_html_()
    
    mapcontext = {
        'm': m
    }
        
    if request.method == "POST":
        q = request.POST['a']
        data = DeceasedInformation.objects.filter(id=q)   
                
        datacontext = {
        'data': data,
        'm': m
        }
        
        return render(request,'locator/index.html', datacontext, )
    else:
        return render(request, "locator/index.html", mapcontext)
    
def specificSearch(request, pk):
    url = (
    "locator/templates/locator/data"
    )
    
    lot_geo = f"{url}/map.geojson"
    lot_csv = f'{url}/testdata.csv'
    lot_data = pd.read_csv(lot_csv)
   
    data = geocoder.osm('Surigao Memorial Park')
    lat = data.lat 
    lng = data.lng
    
    m = folium.Map(location=[9.767206409981258, 125.49904571692107], zoom_start=17, max_zoom=17, min_zoom=14)
    
    style_function = lambda x: {
        'fillOpacity': 0.7, 'weight': 1, 'opacity': 0.5, 'color': '#000000',
        'fillColor': '#BDD9BF' if x['properties']['name'] == 'Garden of Peter' else '#00ff00' 
         and '#8dd3c7' if x['properties']['name'] == 'Garden of Paul' else '#00ff00'
         and '#ffffb3' if x['properties']['name'] == 'Garden of Andrew' else '#00ff00'
         and '#bebada' if x['properties']['name'] == 'Garden of James' else '#00ff00'
         and '#fb8072' if x['properties']['name'] == 'Garden of Philip' else '#00ff00'
         and '#80b1d3' if x['properties']['name'] == 'Garden of Nathaniel' else '#00ff00'
         and '#fdb462' if x['properties']['name'] == 'Garden of John' else '#00ff00'
         and '#b3de69' if x['properties']['name'] == 'Garden of Thomas' else '#00ff00'
         and '#fccde5' if x['properties']['name'] == 'Garden of Nicolas De Tolentino' else '#00ff00'
         and '#d9d9d9' if x['properties']['name'] == 'Garden of Joseph' else '#00ff00'
         and '#bc80bd' if x['properties']['name'] == 'Garden of Jude' else '#00ff00'
         and '#ccebc5' if x['properties']['name'] == 'Garden of Lorenzo Ruiz' else '#00ff00'
         and '#ffed6f' if x['properties']['name'] == 'Garden of Pedro Calungsod' else '#00ff00'
         and '#9e0142' if x['properties']['name'] == 'Garden of Mary' else '#00ff00'
         and '#1a9850' if x['properties']['name'] == 'Garden of Matthew' else '#00ff00'
         and '#543005' if x['properties']['name'] == 'Garden of Ignatius' else '#00ff00'
        }
    
    highlight_function = lambda x: {'fillColor': '#000000', 'color':'#000000', 'fillOpacity': 0.50, 'weight': 0.1}
    
    folium.GeoJson(lot_geo, name="geojson", style_function=style_function, highlight_function=highlight_function).add_to(m)
    folium.LayerControl().add_to(m)
    
    onHoverTooltip = folium.features.GeoJson(
        lot_geo,
        style_function=style_function,
        control=False,
        highlight_function=highlight_function,
        tooltip=folium.features.GeoJsonTooltip(
            fields=["name","lotnum"],
            aliases=['Lot Name: ','Lot Number: '],
            style=("background-color: white; color: #333333; font-family: arial; font-size: 12px; padding: 10px;") 
        )
    )
    
    m.add_child(onHoverTooltip)
    m.keep_in_front(m)
  
    # Marker Function
    
        # z = request.POST['a']
        # data = DeceasedInformation.objects.filter(name__iexact=z)
    data = DeceasedInformation.objects.filter(id=pk).values('name','location__grave_area')
    lotNames = {
        'lot1': 'Garden of Peter',
        'lot2':'Garden of Paul',
        'lot3':'Garden of Andrew',
        'lot4':'Garden of James',
        'lot5':'Garden of Philip',
        'lot6':'Garden of Nathanel',
        'lot7':'Garden of John',
        'lot8':'Garden of Thomas',
        'lot9':'Garden of Nicolas De Tolentino',
        'lot10':'Garden of Joseph',
        'lot11':'Garden of Jude',
        'lot12':'Garden of Lorenzo Ruiz',
        'lot13':'None',
        'lot14':'Garden of Pedro Calungsod',
        'lot15':'Garden of Mary',
        'lot16':'Garden of Matthew',
        'lot17':'Garden of Ignatius',
    }
    
    lotCoordinates = {
        'lot1': [9.767243416604591, 125.49654053369511],
        'lot2': [9.76694339148084, 125.49671085072434],
        'lot3': [9.767494429277574, 125.49703174187478],
        'lot4': [9.766965763152823, 125.49773984506957],
        'lot5': [9.767108277480373, 125.49905652765433],
        'lot6': [9.766939104223683, 125.49923355345639],
        'lot7': [9.767906562656655, 125.50051028484954],
        'lot8': [9.76742547711993, 125.49911017185333],
        'lot9': [9.767927709256048, 125.4991906381162],
        'lot10': [9.767251017359339, 125.50040299650408],
        'lot11': [9.766415723897579, 125.50030643699469],
        'lot12': [9.76819732830619, 125.50094480273268],
        'lot13': [0, 0],
        'lot14': [9.768681090642376, 125.50073831412882],
        'lot15': [9.76778103927861, 125.4982264254473],
        'lot16': [9.76503196862887, 125.49956752987396],
        'lot17': [9.766791077523944, 125.49547846101629]
    }
        
    lotDirections = {
        'lot1': '<a href=https://fr.wikipedia.org/wiki/Place_Guillaume_II></a>',
        'lot2': '',
        'lot3': '',
        'lot4': '',
        'lot5': '',
        'lot6': '',
        'lot7': '',
        'lot8': '',
        'lot9': '',
        'lot10': '',
        'lot11': '',
        'lot12': '',
        'lot13': '',
        'lot14': '',
        'lot15': '',
        'lot16': '',
        'lot17': '',
    }

    lot_name = 'location__grave_area'
        
    for data in data:
        if data[lot_name] == lotNames['lot1'].upper():    
            folium.Marker(lotCoordinates['lot1'], popup=lotDirections['lot1'], icon=folium.Icon(color='red',  icon='info-sign'),).add_to(m)
        if data[lot_name] == lotNames['lot2'].upper():
            folium.Marker(lotCoordinates['lot2'], popup=lotDirections['lot2'], icon=folium.Icon(color='red',  icon='info-sign'),).add_to(m)
        if data[lot_name] == lotNames['lot3'].upper():
            folium.Marker(lotCoordinates['lot3'], popup=lotDirections['lot3'], icon=folium.Icon(color='red',  icon='info-sign'),).add_to(m)
        if data[lot_name] == lotNames['lot4'].upper():
            folium.Marker(lotCoordinates['lot4'], popup=lotDirections['lot4'], icon=folium.Icon(color='red',  icon='info-sign'),).add_to(m)
        if data[lot_name] == lotNames['lot5'].upper():
            folium.Marker(lotCoordinates['lot5'], popup=lotDirections['lot5'], icon=folium.Icon(color='red',  icon='info-sign'),).add_to(m)
        if data[lot_name] == lotNames['lot6'].upper():
            folium.Marker(lotCoordinates['lot6'], popup=lotDirections['lot6'], icon=folium.Icon(color='red',  icon='info-sign'),).add_to(m)
        if data[lot_name] == lotNames['lot7'].upper():
            folium.Marker(lotCoordinates['lot7'], popup=lotDirections['lot7'], icon=folium.Icon(color='red',  icon='info-sign'),).add_to(m)
        if data[lot_name] == lotNames['lot8'].upper():
            folium.Marker(lotCoordinates['lot8'], popup=lotDirections['lot8'], icon=folium.Icon(color='red',  icon='info-sign'),).add_to(m)
        if data[lot_name] == lotNames['lot9'].upper():
            folium.Marker(lotCoordinates['lot9'], popup=lotDirections['lot9'], icon=folium.Icon(color='red',  icon='info-sign'),).add_to(m)
        if data[lot_name] == lotNames['lot10'].upper():
            folium.Marker(lotCoordinates['lot10'], popup=lotDirections['lot10'], icon=folium.Icon(color='red',  icon='info-sign'),).add_to(m)
        if data[lot_name] == lotNames['lot11'].upper():
            folium.Marker(lotCoordinates['lot11'], popup=lotDirections['lot11'], icon=folium.Icon(color='red',  icon='info-sign'),).add_to(m)
        if data[lot_name] == lotNames['lot12'].upper():
            folium.Marker(lotCoordinates['lot12'], popup=lotDirections['lot12'], icon=folium.Icon(color='red',  icon='info-sign'),).add_to(m)
        if data[lot_name] == lotNames['lot13'].upper():
            folium.Marker(lotCoordinates['lot13'], popup=lotDirections['lot13'], icon=folium.Icon(color='red',  icon='info-sign'),).add_to(m)
        if data[lot_name] == lotNames['lot14'].upper():
            folium.Marker(lotCoordinates['lot14'], popup=lotDirections['lot14'], icon=folium.Icon(color='red',  icon='info-sign'),).add_to(m)
        if data[lot_name] == lotNames['lot15'].upper():
            folium.Marker(lotCoordinates['lot15'], popup=lotDirections['lot15'], icon=folium.Icon(color='red',  icon='info-sign'),).add_to(m)
        if data[lot_name] == lotNames['lot16'].upper():
            folium.Marker(lotCoordinates['lot16'], popup=lotDirections['lot16'], icon=folium.Icon(color='red',  icon='info-sign'),).add_to(m)
        if data[lot_name] == lotNames['lot17'].upper():
            folium.Marker(lotCoordinates['lot17'], popup=lotDirections['lot17'], icon=folium.Icon(color='red',  icon='info-sign'),).add_to(m)
            
        
    # Output
    m = m._repr_html_()
    
    mapcontext = {
        'm': m
    }
        
    # q = request.POST['a']
    data = DeceasedInformation.objects.filter(id=pk)   
                
    datacontext = {
        'data': data,
        'm': m
    }
        
    return render(request,'locator/index.html', datacontext)

# End Folium

def searchResults(request):
    if request.method == 'POST':
        q = request.POST['q']
        data = DeceasedInformation.objects.filter(name__icontains=q).order_by('name')
        return render(request,'locator/index.html', {
            'results': data,
            'count': data.count,
            'item': q
            })