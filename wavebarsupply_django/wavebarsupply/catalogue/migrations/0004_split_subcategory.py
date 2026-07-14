"""Split the sub-category out of Category into its own table.

Before: one 'categories' row per (category, sub-category) pair, and each Product
        pointed straight at that pair.
After:  'categories' holds one row per category (9 rows),
        'subcategories' holds one row per sub-category (38 rows) with a foreign
        key to its category, and each Product points at a sub-category.

The data is carried across, so nothing is lost: existing products keep the exact
sub-category they had, and each sub-category keeps its picture.
"""
from django.db import migrations, models
import django.db.models.deletion


def split_forwards(apps, schema_editor):
    """Copy the old (category, sub-category) pairs into the new structure."""
    Category = apps.get_model('catalogue', 'Category')
    Subcategory = apps.get_model('catalogue', 'Subcategory')
    Product = apps.get_model('catalogue', 'Product')

    old_pairs = list(Category.objects.all())

    # 1. One Category row per distinct category name. These are new rows; the
    #    old pair-rows are still present and are deleted further down, once
    #    nothing points at them any more.
    parents = {}
    for pair in old_pairs:
        if pair.name not in parents:
            parents[pair.name] = Category.objects.create(name=pair.name)

    # 2. One Subcategory row per old pair, keeping the SAME id. Keeping the id
    #    is what lets step 3 be a straight copy of the foreign key.
    for pair in old_pairs:
        Subcategory.objects.create(
            id=pair.id,
            name=pair.subcategory,
            image=pair.image,
            category=parents[pair.name],
        )

    # 3. Every product now points at the sub-category with the same id its old
    #    category pointed at.
    for product in Product.objects.all():
        product.subcategory_id = product.category_id
        product.save(update_fields=['subcategory'])


def split_backwards(apps, schema_editor):
    """Rebuild the old pair-rows from the new tables."""
    Category = apps.get_model('catalogue', 'Category')
    Subcategory = apps.get_model('catalogue', 'Subcategory')
    Product = apps.get_model('catalogue', 'Product')

    # The 9 parent categories; they are removed once the pairs are rebuilt.
    parents = list(Category.objects.all())

    for sub in Subcategory.objects.select_related('category'):
        pair = Category.objects.create(
            name=sub.category.name, subcategory=sub.name, image=sub.image)
        Product.objects.filter(subcategory_id=sub.id).update(category_id=pair.id)

    # Detach the products first: the foreign key is PROTECT, so the
    # sub-categories cannot be deleted while products still point at them.
    Product.objects.update(subcategory=None)
    Subcategory.objects.all().delete()
    for parent in parents:
        parent.delete()


def delete_old_pairs(apps, schema_editor):
    """Remove the leftover pair-rows: they are the categories no sub-category
    points at (the 9 new parent rows each have at least one)."""
    Category = apps.get_model('catalogue', 'Category')
    Category.objects.filter(subcategories__isnull=True).delete()


def noop(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('catalogue', '0003_remove_product_emoji_category_image'),
    ]

    operations = [
        # --- new table, nullable for now so the data can be moved into it ---
        migrations.CreateModel(
            name='Subcategory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True,
                                           serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('image', models.CharField(
                    blank=True, default='',
                    help_text='File name inside static/images/, e.g. soft_drinks.jpg',
                    max_length=100)),
                ('category', models.ForeignKey(
                    null=True, on_delete=django.db.models.deletion.PROTECT,
                    related_name='subcategories', to='catalogue.category')),
            ],
            options={
                'verbose_name_plural': 'subcategories',
                'db_table': 'subcategories',
            },
        ),
        migrations.AddField(
            model_name='product',
            name='subcategory',
            field=models.ForeignKey(
                null=True, on_delete=django.db.models.deletion.PROTECT,
                related_name='products', to='catalogue.subcategory'),
        ),

        # --- relax the old columns before the move ---
        # Both are made nullable / given a default so that REVERSING this
        # migration can re-add them to rows that already exist without tripping
        # a NOT NULL constraint. Their real values are put back by
        # split_backwards, and the tightening is re-applied afterwards.
        migrations.AlterField(
            model_name='product',
            name='category',
            field=models.ForeignKey(
                null=True, on_delete=django.db.models.deletion.PROTECT,
                to='catalogue.category'),
        ),
        migrations.AlterField(
            model_name='category',
            name='subcategory',
            field=models.CharField(blank=True, default='', max_length=50),
        ),

        # --- move the data across ---
        migrations.RunPython(split_forwards, split_backwards),

        # --- the old link is no longer needed ---
        migrations.RemoveField(model_name='product', name='category'),

        # --- now that nothing points at them, drop the old pair-rows ---
        migrations.RunPython(delete_old_pairs, noop),

        # --- Category keeps only its name ---
        migrations.RemoveField(model_name='category', name='subcategory'),
        migrations.RemoveField(model_name='category', name='image'),
        migrations.AlterField(
            model_name='category',
            name='name',
            field=models.CharField(
                choices=[('non-alcohol', 'Non-Alcoholic'), ('fermented', 'Fermented'),
                         ('distilled', 'Distilled'), ('cocktail', 'Cocktail Ingredients'),
                         ('ice', 'Ice'), ('dairy', 'Dairy Products'),
                         ('fresh', 'Fresh Products'), ('disposable', 'Disposable Products'),
                         ('snacks', 'Bar Snacks')],
                max_length=20, unique=True),
        ),

        # --- both foreign keys are required from now on ---
        migrations.AlterField(
            model_name='subcategory',
            name='category',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name='subcategories', to='catalogue.category'),
        ),
        migrations.AlterField(
            model_name='product',
            name='subcategory',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name='products', to='catalogue.subcategory'),
        ),
    ]
