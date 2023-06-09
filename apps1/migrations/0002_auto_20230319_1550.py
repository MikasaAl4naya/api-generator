# Generated by Django 3.1.7 on 2023-03-19 07:50

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('apps1', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='datasetmodel',
            name='file_format',
            field=models.CharField(default='json', max_length=10),
        ),
        migrations.CreateModel(
            name='RowModel',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('values', models.JSONField(blank=True, null=True)),
                ('dataset', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='apps1.datasetmodel')),
            ],
        ),
        migrations.CreateModel(
            name='ColumnModel',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('value', models.CharField(max_length=255)),
                ('dataset', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='dataset_columns', to='apps1.datasetmodel')),
                ('row', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='columns', to='apps1.rowmodel')),
            ],
        ),
        migrations.AddField(
            model_name='datasetmodel',
            name='columns',
            field=models.ManyToManyField(related_name='datasets', to='apps1.ColumnModel'),
        ),
        migrations.AddField(
            model_name='datasetmodel',
            name='rows',
            field=models.ManyToManyField(related_name='datasets', to='apps1.RowModel'),
        ),
    ]
