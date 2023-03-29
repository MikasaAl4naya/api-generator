import csv
import json
from django.db import models

class DatasetModel(models.Model):
    title = models.CharField(max_length=255)
    time_create = models.DateTimeField(auto_now_add=True)
    num_rows = models.IntegerField()
    num_columns = models.IntegerField()
    file_format = models.CharField(
        max_length=10,
        choices=(('json', 'JSON'), ('csv', 'CSV')),
        default='json'
    )

    def __str__(self):
        return self.title

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


class RowModel(models.Model):
    dataset = models.ForeignKey(DatasetModel, on_delete=models.CASCADE)
    values = models.JSONField(null=True, blank=True)
    def __str__(self):
        return f"Row {self.pk} of dataset {self.dataset.title}"


class ColumnModel(models.Model):
    dataset = models.ForeignKey(DatasetModel, on_delete=models.CASCADE, related_name='dataset_columns')
    row = models.ForeignKey(RowModel, on_delete=models.CASCADE, related_name='columns')
    name = models.CharField(max_length=255)
    value = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.name} of {self.row} in dataset {self.dataset.title}"
