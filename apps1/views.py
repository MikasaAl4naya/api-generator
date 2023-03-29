import csv
import io
from datetime import datetime
from django.http import HttpResponse
from django.shortcuts import render
from mimesis import Generic, Datetime
from mimesis.enums import Gender
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import DatasetModel, RowModel, ColumnModel
from .serializers import DatasetSerializer
import re
from mimesis.enums import CardType
from faker import Faker

fake = Faker('ru_RU')
g = Generic()


def get_gender_from_name(name):
    if re.search('[а-яА-Я]*[аоуыэяюёе]$', name):
        return ("Жен.")
    else:
        return ("Муж.")
g = Generic('ru')
dt = Datetime('ru')
class DatasetApiView(APIView):
    def get(self, request):
        d = DatasetModel.objects.all()
        return Response({'datasets': DatasetSerializer(d, many=True).data})


    def post(self, request):
        # Получаем данные из запроса
        title = request.data.get('title')
        num_rows = int(request.data.get('num_rows', 0))  # количество строк
        num_columns = int(request.data.get('num_columns', 0))  # количество столбцов
        column_names = request.data.get('column_names', [])  # список с названиями столбцов
        column_types = request.data.get('column_types', [])  # список с типами данных
        file_format = request.data.get('file_format', 'json')  # формат файла, по умолчанию - json


        # Создаем список с описанием столбцов
        columns = []
        for name, dtype in zip(column_names, column_types):
            column = {
                'name': name,
                'dtype': dtype
            }
            columns.append(column)

        # Генерируем таблицу
        data = []
        for i in range(num_rows):
            row = {}
            first_name = g.person.first_name()
            for col in columns:
                name = col['name']
                dtype = col['dtype']
                if dtype == 'Auto-increment':
                    row[name] = i + 1
                elif dtype == 'First Name':
                    row[name] = first_name
                elif dtype == 'Last Name':
                    row[name] = g.person.last_name()
                elif dtype == 'Gender':
                    row[name] = str(get_gender_from_name(first_name))
                elif dtype == 'Phone Number':
                    row[name] = g.person.telephone()
                elif dtype == 'Credit Card Number':
                    row[name] = g.payment.credit_card_number(card_type=CardType.VISA)
                elif dtype == 'Job Title':
                    row[name] = g.business.job_title()
                elif dtype == 'Company':
                    row[name] = fake.company()
                elif dtype == 'Country':
                    row[name] = g.address.country()
                elif dtype == 'Random Number':
                    row[name] = g.random.randint(0, 100)
                elif dtype == 'Email':
                    row[name] = g.person.email()
                elif dtype == 'Username':
                    row[name] = g.person.username()
                elif dtype == 'Date':
                    date_str = "2022-03-21"
                    row[name] = datetime.strptime(date_str, "%Y-%m-%d")
                elif dtype == 'SNILS':
                    row[name] = fake.ssn()
            data.append(row)

        # Сохраняем таблицу в базу данных
        dataset = DatasetModel.objects.create(
            title=title,
            num_rows=num_rows,
            num_columns=num_columns
        )
        self.create_rows_and_columns(dataset, data)

        # Отправляем ответ
        serializer = DatasetSerializer(instance=dataset)

        if file_format == 'csv':
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = f'attachment; filename="{title}.csv"'
            writer = csv.DictWriter(response, fieldnames=column_names)
            writer.writeheader()

            for row in data:
                writer.writerow({column_name: row[column_name] for column_name in column_names})

            return response

        return Response(serializer.data)

    def create_rows_and_columns(self, dataset, data):
        file_format = dataset.file_format
        if file_format == 'csv':
            # write the data to a StringIO buffer
            buffer = io.StringIO()
            writer = csv.DictWriter(buffer, fieldnames=dataset.column_names)
            writer.writeheader()
            for row in data:
                writer.writerow(row)
            # save the buffer content to a file
            filename = f'{dataset.title}.csv'
            with open(filename, 'w', newline='') as file:
                file.write(buffer.getvalue())
            # create rows and columns from the file
            with open(filename, 'r', newline='') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    row_model = RowModel.objects.create(
                        dataset=dataset,
                        values=row
                    )
                    for col_name, col_value in row.items():
                        ColumnModel.objects.create(
                            dataset=dataset,
                            row=row_model,
                            name=col_name,
                            value=col_value
                        )
        else:
            for row in data:
                row_model = RowModel.objects.create(
                    dataset=dataset,
                    values=row
                )
                for col_name, col_value in row.items():
                    ColumnModel.objects.create(
                        dataset=dataset,
                        row=row_model,
                        name=col_name,
                        value=col_value
                    )
    # def put(self, request, *args, **kwargs):
    #     pk = kwargs.get('pk', None)
    #     if not pk:
    #         return Response({"error":"Method PUT not allowed"})
    #
    #     try:
    #         instance = DatasetModel.objects.get(pk=pk)
    #     except:
    #         return Response({"error":"Object does not exist"})
    #
    #     serializer = DatasetSerializer(data=request.data,instance=instance)
    #     serializer.is_valid(raise_exception=True)
    #     serializer.save()
    #     return Response({"post": serializer.data})

        # post_new = DatasetModel.objects.create(
        #     title=request.data['title'],
        #     num_rows = request.data['num_rows'],
        #     num_columns = request.data['num_columns']
        # )
    # def put(self, request, *args, **kwargs):
    #     pk = kwargs.get('pk', None)
    #     if not pk:
    #         return Response({"error":"Method PUT not allowed"})
    #
    #     try:
    #         instance = DatasetModel.objects.get(pk=pk)
    #     except:
    #         return Response({"error":"Object does not exist"})
    #
    #     serializer = DatasetSerializer(data=request.data,instance=instance)
    #     serializer.is_valid(raise_exception=True)
    #     serializer.save()
    #     return Response({"post": serializer.data})



# class DatasetApiView(generics.ListAPIView):
#     queryset = DatasetModel.objects.all()
#     serializer_class = DatasetSerializer