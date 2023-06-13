from import_export import resources,widgets,fields
from search.models import DeceasedInformation, Location

class DeceasedInformationResource(resources.ModelResource):
    location = fields.Field(column_name='location', attribute='location', widget=widgets.ForeignKeyWidget(Location, 'grave_area'),saves_null_values=False)
    class Meta:
        model = DeceasedInformation
        fields = ('id','reference_number','name','born','died','location','graveimage')