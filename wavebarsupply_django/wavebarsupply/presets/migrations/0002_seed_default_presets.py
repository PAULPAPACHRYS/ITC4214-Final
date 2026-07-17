from django.db import migrations


DEFAULTS = [
    ('Mojito', '#7BB661', [
        'Bacardi Carta Blanca', 'Fresh Mint Bunch', 'Lime Juice', 'Soda Water',
        'Kristal Crushed Ice 2kg']),
    ('Margarita', '#E6C84F', [
        'Jose Cuervo Silver', 'Triple Sec', 'Lime Juice', 'Salt',
        'Kristal Crushed Ice 2kg']),
    ('Mai Tai', '#E8833A', [
        'Bacardi Carta Blanca', 'Diplomatico Reserva', 'Orange Curacao Liqueur',
        'Orgeat Syrup', 'Lime Juice', 'Kristal Crushed Ice 2kg']),
    ('Sex on the Beach', '#FF6B6B', [
        'Absolut Original', 'Peach Schnapps Liqueur', 'Orange Juice',
        'Cranberry Juice', 'Kristal Crushed Ice 2kg']),
    ('Zombie', '#C0392B', [
        'Bacardi Carta Blanca', 'Diplomatico Reserva', 'Apricot Brandy',
        'Pineapple Juice', 'Orange Juice', 'Lime Juice', 'Grenadine Syrup',
        'Falernum Syrup', 'Angostura Aromatic Bitters', 'Kristal Crushed Ice 2kg']),
    ('Pornstar Martini', '#F4B6C2', [
        'Absolut Vanilla Vodka', 'Passoa Liqueur', 'Passion Fruit Juice',
        'Vanilla Syrup', 'Lime Juice', 'Fresh Passion Fruit',
        'Kristal Crushed Ice 2kg']),
]


def seed_defaults(apps, schema_editor):
    Preset = apps.get_model('presets', 'Preset')
    Product = apps.get_model('catalogue', 'Product')

    if Preset.objects.filter(user=None).exists():
        return

    needed = {name for _, _, ingredients in DEFAULTS for name in ingredients}
    by_name = {p.name: p for p in Product.objects.filter(name__in=needed)}
    if len(by_name) != len(needed):
        return

    for name, color, ingredients in DEFAULTS:
        preset = Preset.objects.create(name=name, color=color, user=None)
        preset.ingredients.set([by_name[n] for n in ingredients])


def remove_defaults(apps, schema_editor):
    Preset = apps.get_model('presets', 'Preset')
    Preset.objects.filter(user=None).delete()


class Migration(migrations.Migration):
    dependencies = [
        ('presets', '0001_initial'),
        ('catalogue', '0002_alter_category_name'),
    ]
    operations = [migrations.RunPython(seed_defaults, remove_defaults)]
