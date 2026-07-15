"""Turn the free-text product tags into a Tag table.

Before: products.tags was a JSON column holding a list of typed-in strings, so
        the same idea could be spelled several ways with no warning.
After:  tags are rows in a 'tags' table, and a product links to the tags it has
        through a many-to-many join table. Adding a tag is now a deliberate act.

The existing tags are carried across: every distinct tag string already used by a
product becomes a Tag row (tidied up: trimmed and lowercased), and every product
is linked to exactly the tags it had before.

This migration also adds the range checks and the duplicate protection.
"""
from decimal import Decimal

import django.core.validators
import django.db.models.deletion
from django.db import migrations, models

import catalogue.models


def tags_forwards(apps, schema_editor):
    """Copy the tag strings out of the JSON column into the new table."""
    Product = apps.get_model('catalogue', 'Product')
    Tag = apps.get_model('catalogue', 'Tag')

    for product in Product.objects.all():
        tag_objects = []
        for raw in (product.tags_old or []):
            # Tidy the tag on the way in: trim it, collapse inner spaces and
            # lowercase it, so 'IPA' and 'ipa' become the same single tag.
            name = ' '.join(str(raw).split()).lower()
            if not name:
                continue
            tag, _ = Tag.objects.get_or_create(name=name)
            tag_objects.append(tag)
        if tag_objects:
            product.tags.set(tag_objects)


def tags_backwards(apps, schema_editor):
    """Write the tag names back into the JSON column."""
    Product = apps.get_model('catalogue', 'Product')
    for product in Product.objects.prefetch_related('tags'):
        product.tags_old = [t.name for t in product.tags.all()]
        product.save(update_fields=['tags_old'])


class Migration(migrations.Migration):

    dependencies = [
        ('catalogue', '0005_alter_category_name'),
    ]

    operations = [
        # --- the new table ---
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

        # --- move the tags across ---
        # The JSON column is renamed out of the way first, so the new
        # many-to-many field can take the 'tags' name the rest of the code uses.
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

        # --- range checks on the numbers ---
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

        # --- the category name must be a slug ---
        migrations.AlterField(
            model_name='category',
            name='name',
            field=models.CharField(
                max_length=20, unique=True,
                validators=[catalogue.models.slug_validator]),
        ),

        # --- duplicate protection ---
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
