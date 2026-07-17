from decimal import Decimal
import django.core.validators
import django.db.models.deletion
from django.db import migrations, models
import catalogue.models


def tags_forwards(apps, schema_editor):
    Product = apps.get_model('catalogue', 'Product')
    Tag = apps.get_model('catalogue', 'Tag')

    for product in Product.objects.all():
        tag_objects = []
        for raw in (product.tags_old or []):
            name = ' '.join(str(raw).split()).lower()
            if not name:
                continue
            tag, _ = Tag.objects.get_or_create(name=name)
            tag_objects.append(tag)
        if tag_objects:
            product.tags.set(tag_objects)


def tags_backwards(apps, schema_editor):
    Product = apps.get_model('catalogue', 'Product')
    for product in Product.objects.prefetch_related('tags'):
        product.tags_old = [t.name for t in product.tags.all()]
        product.save(update_fields=['tags_old'])


class Migration(migrations.Migration):

    dependencies = [
        ('catalogue', '0005_alter_category_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True,
                                           serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=30, unique=True)),
            ],
            options={
                'db_table': 'tags',
                'ordering': ['name'],
            },
        ),

        migrations.RenameField(model_name='product', old_name='tags',
                               new_name='tags_old'),
        migrations.AddField(
            model_name='product',
            name='tags',
            field=models.ManyToManyField(blank=True, related_name='products',
                                         to='catalogue.tag'),
        ),
        migrations.RunPython(tags_forwards, tags_backwards),
        migrations.RemoveField(model_name='product', name='tags_old'),

        migrations.AlterField(
            model_name='product',
            name='price',
            field=models.DecimalField(
                decimal_places=2, max_digits=6,
                validators=[django.core.validators.MinValueValidator(Decimal('0.01'))]),
        ),
        migrations.AlterField(
            model_name='product',
            name='volume',
            field=models.PositiveIntegerField(
                help_text='Volume in millilitres',
                validators=[django.core.validators.MinValueValidator(1),
                            django.core.validators.MaxValueValidator(20000)]),
        ),
        migrations.AlterField(
            model_name='product',
            name='abv',
            field=models.DecimalField(
                decimal_places=1, max_digits=4,
                help_text='Alcohol by volume, %',
                validators=[django.core.validators.MinValueValidator(Decimal('0')),
                            django.core.validators.MaxValueValidator(Decimal('100'))]),
        ),

        migrations.AlterField(
            model_name='category',
            name='name',
            field=models.CharField(
                max_length=20, unique=True,
                validators=[catalogue.models.slug_validator]),
        ),

        migrations.AlterField(
            model_name='brand',
            name='name',
            field=models.CharField(max_length=100, unique=True),
        ),
        migrations.AddConstraint(
            model_name='subcategory',
            constraint=models.UniqueConstraint(
                fields=('category', 'name'),
                name='unique_subcategory_per_category'),
        ),
        migrations.AddConstraint(
            model_name='product',
            constraint=models.UniqueConstraint(
                fields=('name', 'brand', 'volume'),
                name='unique_product_name_brand_volume'),
        ),
    ]
