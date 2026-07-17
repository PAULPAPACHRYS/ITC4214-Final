from django.db import migrations, models
import django.db.models.deletion


def split_forwards(apps, schema_editor):
    Category = apps.get_model('catalogue', 'Category')
    Subcategory = apps.get_model('catalogue', 'Subcategory')
    Product = apps.get_model('catalogue', 'Product')

    old_pairs = list(Category.objects.all())

    parents = {}
    for pair in old_pairs:
        if pair.name not in parents:
            parents[pair.name] = Category.objects.create(name=pair.name)

    for pair in old_pairs:
        Subcategory.objects.create(
            id=pair.id,
            name=pair.subcategory,
            image=pair.image,
            category=parents[pair.name],
        )

    for product in Product.objects.all():
        product.subcategory_id = product.category_id
        product.save(update_fields=['subcategory'])


def split_backwards(apps, schema_editor):
    Category = apps.get_model('catalogue', 'Category')
    Subcategory = apps.get_model('catalogue', 'Subcategory')
    Product = apps.get_model('catalogue', 'Product')

    parents = list(Category.objects.all())

    for sub in Subcategory.objects.select_related('category'):
        pair = Category.objects.create(
            name=sub.category.name, subcategory=sub.name, image=sub.image)
        Product.objects.filter(subcategory_id=sub.id).update(category_id=pair.id)

    Product.objects.update(subcategory=None)
    Subcategory.objects.all().delete()
    for parent in parents:
        parent.delete()


def delete_old_pairs(apps, schema_editor):
    Category = apps.get_model('catalogue', 'Category')
    Category.objects.filter(subcategories__isnull=True).delete()


def noop(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('catalogue', '0003_remove_product_emoji_category_image'),
    ]

    operations = [
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

        migrations.RunPython(split_forwards, split_backwards),

        migrations.RemoveField(model_name='product', name='category'),

        migrations.RunPython(delete_old_pairs, noop),

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
