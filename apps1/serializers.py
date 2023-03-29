import csv
import io
import json

from rest_framework import serializers, generics
from rest_framework.parsers import JSONParser
from rest_framework.renderers import JSONRenderer

from .models import DatasetModel, ColumnModel, RowModel


class ColumnSerializer(serializers.ModelSerializer):
    class Meta:
        model = ColumnModel
        fields = ('name', 'value')

class DatasetSerializer(serializers.ModelSerializer):
    columns = serializers.SerializerMethodField()

    class Meta:
        model = DatasetModel
        fields = ('id', 'title', 'time_create', 'num_rows', 'num_columns', 'file_format', 'columns')

    def get_columns(self, obj):
        rows = RowModel.objects.filter(dataset=obj)
        columns = {}
        for row in rows:
            for column in row.values.keys():
                columns[column] = columns.get(column, []) + [row.values[column]]
        return [{name: value} for name, value in columns.items()]


    # title = serializers.CharField(max_length=255)
    # time_create = serializers.DateTimeField(read_only=True)
    # num_rows = serializers.IntegerField()
    # num_columns = serializers.IntegerField()
    #
    #
    def create(self, *args, **kwargs):
        if self.file_format == 'csv':
            # сохраняем данные в формате CSV
            with open(f'{self.title}.csv', mode='w', newline='') as file:
                writer = csv.DictWriter(file, fieldnames=self.column_names)
                writer.writeheader()
                for row in self.data:
                    writer.writerow(row)
        else:
            # сохраняем данные в формате JSON
            json_data = json.dumps(self.data)
            self.data = json_data

        super().create(*args, **kwargs)


# def encode():
#     model = DataModel('Data test')
#     model_sr = DataSerializer(model)
#     print(model_sr.data, type(model_sr.data),sep='\n')
#     json = JSONRenderer().render(model_sr.data)
#     print(json)
# def decode():
#     stream = io.BytesIO(b'{"title":"Data test"}')
#     data = JSONParser().parse(stream)
#     serializer=DataSerializer(data=data)
#     serializer.is_valid()
#     print(serializer.validated_data)
