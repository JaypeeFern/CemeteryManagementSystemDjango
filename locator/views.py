from functools import lru_cache

import folium
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.views.decorators.http import require_POST

from search.models import DeceasedInformation


MAP_GEOJSON_PATH = "locator/templates/locator/data/map.geojson"
MAP_CENTER = [9.767206409981258, 125.49904571692107]
MAP_COLORS = {
    'Garden of Peter': '#BDD9BF',
    'Garden of Paul': '#8dd3c7',
    'Garden of Andrew': '#ffffb3',
    'Garden of James': '#bebada',
    'Garden of Philip': '#fb8072',
    'Garden of Nathaniel': '#80b1d3',
    'Garden of John': '#fdb462',
    'Garden of Thomas': '#b3de69',
    'Garden of Nicolas De Tolentino': '#fccde5',
    'Garden of Joseph': '#d9d9d9',
    'Garden of Jude': '#bc80bd',
    'Garden of Lorenzo Ruiz': '#ccebc5',
    'Garden of Pedro Calungsod': '#ffed6f',
    'Garden of Mary': '#9e0142',
    'Garden of Matthew': '#1a9850',
    'Garden of Ignatius': '#543005',
}
MAP_MARKERS = {
    'GARDEN OF PETER': [9.767243416604591, 125.49654053369511],
    'GARDEN OF PAUL': [9.76694339148084, 125.49671085072434],
    'GARDEN OF ANDREW': [9.767494429277574, 125.49703174187478],
    'GARDEN OF JAMES': [9.766965763152823, 125.49773984506957],
    'GARDEN OF PHILIP': [9.767108277480373, 125.49905652765433],
    'GARDEN OF NATHANIEL': [9.766939104223683, 125.49923355345639],
    'GARDEN OF JOHN': [9.767906562656655, 125.50051028484954],
    'GARDEN OF THOMAS': [9.76742547711993, 125.49911017185333],
    'GARDEN OF NICOLAS DE TOLENTINO': [9.767927709256048, 125.4991906381162],
    'GARDEN OF JOSEPH': [9.767251017359339, 125.50040299650408],
    'GARDEN OF JUDE': [9.766415723897579, 125.50030643699469],
    'GARDEN OF LORENZO RUIZ': [9.76819732830619, 125.50094480273268],
    'GARDEN OF PEDRO CALUNGSOD': [9.768681090642376, 125.50073831412882],
    'GARDEN OF MARY': [9.76778103927861, 125.4982264254473],
    'GARDEN OF MATTHEW': [9.76503196862887, 125.49956752987396],
    'GARDEN OF IGNATIUS': [9.766791077523944, 125.49547846101629],
}
KNOWN_MAP_AREAS = frozenset((*MAP_MARKERS, 'GARDEN OF NATHANEL'))


def _normalize_map_area(grave_area):
    if not grave_area:
        return None

    normalized_area = grave_area.strip().upper()
    if normalized_area not in KNOWN_MAP_AREAS:
        return None
    if normalized_area == 'GARDEN OF NATHANEL':
        return 'GARDEN OF NATHANIEL'
    return normalized_area


@lru_cache(maxsize=17)
def _render_grave_map(normalized_area):
    map_view = folium.Map(
        location=MAP_CENTER,
        zoom_start=17,
        max_zoom=17,
        min_zoom=14,
    )

    def style_function(feature):
        garden_name = feature['properties']['name']
        return {
            'fillOpacity': 0.7,
            'weight': 1,
            'opacity': 0.5,
            'color': '#000000',
            'fillColor': MAP_COLORS.get(garden_name, '#00ff00'),
        }

    highlight_function = lambda feature: {
        'fillColor': '#000000',
        'color': '#000000',
        'fillOpacity': 0.50,
        'weight': 0.1,
    }

    folium.GeoJson(
        MAP_GEOJSON_PATH,
        name='geojson',
        style_function=style_function,
        highlight_function=highlight_function,
    ).add_to(map_view)
    folium.LayerControl().add_to(map_view)
    map_view.add_child(
        folium.features.GeoJson(
            MAP_GEOJSON_PATH,
            style_function=style_function,
            control=False,
            highlight_function=highlight_function,
            tooltip=folium.features.GeoJsonTooltip(
                fields=['name', 'lotnum'],
                aliases=['Lot Name: ', 'Lot Number: '],
                style=(
                    'background-color: white; color: #333333; font-family: arial; '
                    'font-size: 12px; padding: 10px;'
                ),
            ),
        )
    )
    map_view.keep_in_front(map_view)

    if normalized_area in MAP_MARKERS:
        folium.Marker(
            MAP_MARKERS[normalized_area],
            popup='',
            icon=folium.Icon(color='red', icon='info-sign'),
        ).add_to(map_view)

    return map_view._repr_html_()


@login_required(login_url='Home')
def renderGraveLocator(request):
    selected_area = None
    selected_record_id = None
    if request.method == 'POST':
        selected_record_id = request.POST.get('a')
        if selected_record_id and selected_record_id.isdecimal():
            selected_area = DeceasedInformation.objects.filter(
                id=selected_record_id,
            ).values_list('location__grave_area', flat=True).first()
        else:
            selected_record_id = None

    map_html = _render_grave_map(_normalize_map_area(selected_area))
    if selected_record_id:
        return render(request, 'locator/index.html', {
            'data': DeceasedInformation.objects.filter(id=selected_record_id),
            'm': map_html,
        })

    return render(request, 'locator/index.html', {'m': map_html})


@login_required(login_url='Home')
def specificSearch(request, pk):
    selected_area = DeceasedInformation.objects.filter(
        id=pk,
    ).values_list('location__grave_area', flat=True).first()
    map_html = _render_grave_map(_normalize_map_area(selected_area))
    return render(request, 'locator/index.html', {
        'data': DeceasedInformation.objects.filter(id=pk),
        'm': map_html,
    })


@login_required(login_url='Home')
@require_POST
def searchResults(request):
    query = request.POST.get('q', '').strip()
    if not query:
        return render(request, 'locator/index.html', {
            'results': [],
            'count': 0,
            'item': query,
        })

    results = DeceasedInformation.objects.filter(
        name__icontains=query,
    ).order_by('name')
    return render(request, 'locator/index.html', {
        'results': results,
        'count': results.count,
        'item': query,
    })
