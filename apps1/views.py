import csv
import io
from datetime import datetime
from django.http import HttpResponse
from django.shortcuts import render
from faker.generator import random
from mimesis import Generic, Datetime
from mimesis.enums import Gender
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import DatasetModel, RowModel, ColumnModel
from .serializers import DatasetSerializer
import re
from mimesis.enums import CardType
from faker import Faker


g = Generic()
dt = Datetime('ru')
fake = Faker('ru_RU')
def get_gender_from_name(name):
    if re.search('[а-яА-Я]*[аоуыэяюёе]$', name):
        return ("Жен.")
    else:
        return ("Муж.")

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

        def generate_prices():
            price_int = random.randint(100, 1000)
            currency = 'RUB'
            price_str = str(price_int)
            return "{} {}".format(price_str, currency)

        def generate_contractors(num_rows):
            contractors = []
            for _ in range(num_rows):
                contractor = {
                    'name': fake.company(),
                    'inn': fake.random_number(digits=10),
                    'kpp': fake.random_number(digits=9),
                    'address': fake.address(),
                    'phone': fake.phone_number()
                }
                contractors.append(contractor)
            return contractors
        def generate_contracts():
            contract = {}
            contract['id'] = i + 1
            contract['supplier'] = fake.company()
            contract['customer'] = fake.company()
            contract['product'] = fake.word()
            contract['price'] = round(random.uniform(100, 1000), 2)
            contract['quantity'] = random.randint(1, 100)
            contract['delivery_date'] = fake.date_between(start_date='-1y', end_date='+1y').strftime('%Y-%m-%d')
            contract['status'] = random.choice(['draft', 'active', 'expired'])
            return contract
        def generate_financial_data():
            data = {}
            transaction_type = random.choice(['expense', 'income'])
            amount = round(random.uniform(10.0, 10000.0), 2)
            date = fake.date_between(start_date='-1y', end_date='today')
            description = fake.text(max_nb_chars=50)
            data['transaction_type']= transaction_type
            data['amount']= amount
            data['date']= date
            data['description']= description
            return data

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
                elif dtype == 'Contracts':
                    row[name] = generate_contracts()
                elif dtype == 'Last Name':
                    row[name] = g.person.last_name()
                elif dtype == 'Financial Data':
                    row[name] = generate_financial_data()
                elif dtype == 'Prices':
                    row[name] = generate_prices()
                elif dtype == 'Сontractors':
                    row[name] = generate_contractors(1)
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
                elif dtype == 'Full Name':
                    row[name] = f"{row['First Name']} {row['Last Name']}"
                elif dtype == 'Address':
                    row[name] = fake.address()
                elif dtype == 'Age':
                    row[name] = g.random.randint(18, 70)
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
