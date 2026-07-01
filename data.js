/* =============================================
   WAVEBAR SUPPLY — data.js
   Shared product catalogue
   ============================================= */

const PRODUCTS = [
  /* ── NON-ALCOHOLIC » Soft Drinks ── */
  { id:1,  name:"Coca-Cola Classic",       brand:"Coca-Cola",  category:"non-alcohol", subcategory:"Soft Drinks",    price:1.20, volume:"330ml", abv:"none",   emoji:"🥤", tags:["cola","classic","carbonated"] },
  { id:2,  name:"Coca-Cola Zero",          brand:"Coca-Cola",  category:"non-alcohol", subcategory:"Soft Drinks",    price:1.20, volume:"330ml", abv:"none",   emoji:"🥤", tags:["cola","zero sugar","carbonated"] },
  { id:3,  name:"Sprite Lemon-Lime",       brand:"Sprite",     category:"non-alcohol", subcategory:"Soft Drinks",    price:1.15, volume:"330ml", abv:"none",   emoji:"🥤", tags:["lemon","lime","carbonated"] },
  { id:4,  name:"Fanta Orange",            brand:"Fanta",      category:"non-alcohol", subcategory:"Soft Drinks",    price:1.15, volume:"330ml", abv:"none",   emoji:"🥤", tags:["orange","fruity","carbonated"] },
  { id:5,  name:"Pepsi Max",               brand:"Pepsi",      category:"non-alcohol", subcategory:"Soft Drinks",    price:1.10, volume:"500ml", abv:"none",   emoji:"🥤", tags:["cola","max","carbonated"] },

  /* ── NON-ALCOHOLIC » Water ── */
  { id:6,  name:"Souroti Sparkling",       brand:"Souroti",    category:"non-alcohol", subcategory:"Water",          price:0.80, volume:"500ml", abv:"none",   emoji:"💧", tags:["sparkling","mineral","greek"] },
  { id:7,  name:"Evian Still",             brand:"Evian",      category:"non-alcohol", subcategory:"Water",          price:1.20, volume:"750ml", abv:"none",   emoji:"💧", tags:["still","premium","mineral"] },
  { id:8,  name:"Vikos Natural",           brand:"Vikos",      category:"non-alcohol", subcategory:"Water",          price:0.60, volume:"500ml", abv:"none",   emoji:"💧", tags:["still","natural","greek"] },
  { id:9,  name:"San Pellegrino",          brand:"San Pellegrino", category:"non-alcohol", subcategory:"Water",      price:1.80, volume:"750ml", abv:"none",   emoji:"💧", tags:["sparkling","italian","premium"] },

  /* ── NON-ALCOHOLIC » Juices ── */
  { id:10, name:"Tropicana Orange",        brand:"Tropicana",  category:"non-alcohol", subcategory:"Juices",         price:2.20, volume:"1L",   abv:"none",   emoji:"🍊", tags:["orange","100% juice","no added sugar"] },
  { id:11, name:"Innocent Mango Smoothie", brand:"Innocent",   category:"non-alcohol", subcategory:"Juices",         price:2.80, volume:"750ml", abv:"none",  emoji:"🥭", tags:["mango","smoothie","tropical"] },
  { id:12, name:"Amita Peach Juice",       brand:"Amita",      category:"non-alcohol", subcategory:"Juices",         price:1.50, volume:"1L",   abv:"none",   emoji:"🍑", tags:["peach","nectar","greek"] },

  /* ── NON-ALCOHOLIC » Ice Teas ── */
  { id:13, name:"Lipton Peach Ice Tea",    brand:"Lipton",     category:"non-alcohol", subcategory:"Ice Teas",       price:1.30, volume:"500ml", abv:"none",  emoji:"🍵", tags:["peach","sweet","iced"] },
  { id:14, name:"Nestea Lemon",            brand:"Nestea",     category:"non-alcohol", subcategory:"Ice Teas",       price:1.25, volume:"500ml", abv:"none",  emoji:"🍵", tags:["lemon","classic","iced"] },
  { id:15, name:"Gold Peak Green Tea",     brand:"Gold Peak",  category:"non-alcohol", subcategory:"Ice Teas",       price:1.60, volume:"547ml", abv:"none",  emoji:"🍵", tags:["green","unsweetened","natural"] },

  /* ── NON-ALCOHOLIC » Coffee ── */
  { id:16, name:"Nescafé Freddo Espresso", brand:"Nescafé",    category:"non-alcohol", subcategory:"Coffee",         price:1.50, volume:"250ml", abv:"none",  emoji:"☕", tags:["espresso","cold","greek"] },
  { id:17, name:"Starbucks Cold Brew",     brand:"Starbucks",  category:"non-alcohol", subcategory:"Coffee",         price:3.20, volume:"325ml", abv:"none",  emoji:"☕", tags:["cold brew","premium","smooth"] },
  { id:18, name:"Lavazza Cappuccino Can",  brand:"Lavazza",    category:"non-alcohol", subcategory:"Coffee",         price:2.20, volume:"250ml", abv:"none",  emoji:"☕", tags:["cappuccino","can","italian"] },

  /* ── NON-ALCOHOLIC » Energy Drinks ── */
  { id:19, name:"Red Bull Original",       brand:"Red Bull",   category:"non-alcohol", subcategory:"Energy Drinks",  price:2.50, volume:"250ml", abv:"none",  emoji:"⚡", tags:["energy","taurine","original"] },
  { id:20, name:"Monster Energy Green",    brand:"Monster",    category:"non-alcohol", subcategory:"Energy Drinks",  price:2.30, volume:"500ml", abv:"none",  emoji:"⚡", tags:["energy","large","green"] },
  { id:21, name:"Celsius Tropical",        brand:"Celsius",    category:"non-alcohol", subcategory:"Energy Drinks",  price:2.80, volume:"355ml", abv:"none",  emoji:"⚡", tags:["energy","fitness","tropical"] },

  /* ── FERMENTED » Beer ── */
  { id:22, name:"Mythos Lager",            brand:"Mythos",     category:"fermented",   subcategory:"Beer",           price:1.80, volume:"500ml", abv:"low",   emoji:"🍺", tags:["lager","greek","refreshing"] },
  { id:23, name:"Fix Hellas",              brand:"Fix",        category:"fermented",   subcategory:"Beer",           price:1.90, volume:"500ml", abv:"low",   emoji:"🍺", tags:["pilsner","greek","classic"] },
  { id:24, name:"Heineken",               brand:"Heineken",   category:"fermented",   subcategory:"Beer",           price:2.20, volume:"330ml", abv:"low",   emoji:"🍺", tags:["lager","dutch","international"] },
  { id:25, name:"Corona Extra",            brand:"Corona",     category:"fermented",   subcategory:"Beer",           price:2.50, volume:"330ml", abv:"low",   emoji:"🍺", tags:["lager","mexican","beach"] },
  { id:26, name:"Alfa Lager",              brand:"Alfa",       category:"fermented",   subcategory:"Beer",           price:1.70, volume:"500ml", abv:"low",   emoji:"🍺", tags:["lager","greek","light"] },
  { id:27, name:"Craft IPA Beach Brew",    brand:"BrewDog",    category:"fermented",   subcategory:"Beer",           price:3.40, volume:"440ml", abv:"medium", emoji:"🍺", tags:["IPA","craft","hoppy"] },

  /* ── FERMENTED » Wine ── */
  { id:28, name:"Assyrtiko Santorini",     brand:"Boutari",    category:"fermented",   subcategory:"Wine",           price:12.00, volume:"750ml", abv:"medium", emoji:"🍷", tags:["white","dry","greek","volcanic"] },
  { id:29, name:"Agiorgitiko Red",         brand:"Gaia",       category:"fermented",   subcategory:"Wine",           price:10.00, volume:"750ml", abv:"medium", emoji:"🍷", tags:["red","dry","greek","nemea"] },
  { id:30, name:"Prosecco DOC",            brand:"Mionetto",   category:"fermented",   subcategory:"Wine",           price:9.00,  volume:"750ml", abv:"medium", emoji:"🥂", tags:["sparkling","italian","prosecco"] },
  { id:31, name:"Rosé de Provence",        brand:"Whispering Angel", category:"fermented", subcategory:"Wine",       price:18.00, volume:"750ml", abv:"medium", emoji:"🥂", tags:["rosé","french","premium"] },

  /* ── FERMENTED » Cider ── */
  { id:32, name:"Strongbow Original",      brand:"Strongbow",  category:"fermented",   subcategory:"Cider",          price:2.80, volume:"500ml", abv:"low",   emoji:"🍎", tags:["apple","dry","classic"] },
  { id:33, name:"Rekorderlig Strawberry",  brand:"Rekorderlig", category:"fermented",  subcategory:"Cider",          price:3.20, volume:"500ml", abv:"low",   emoji:"🍓", tags:["strawberry","sweet","fruity"] },
  { id:34, name:"Kopparberg Mixed Fruit",  brand:"Kopparberg", category:"fermented",   subcategory:"Cider",          price:3.10, volume:"500ml", abv:"low",   emoji:"🍏", tags:["mixed fruit","swedish","sweet"] },

  /* ── DISTILLED » Whisky ── */
  { id:35, name:"Jack Daniel's No.7",      brand:"Jack Daniel's", category:"distilled", subcategory:"Whisky",        price:24.00, volume:"700ml", abv:"high", emoji:"🥃", tags:["tennessee","american","classic"] },
  { id:36, name:"Johnnie Walker Black",    brand:"Johnnie Walker", category:"distilled", subcategory:"Whisky",       price:28.00, volume:"700ml", abv:"high", emoji:"🥃", tags:["blended","scotch","smoky"] },
  { id:37, name:"Glenfiddich 12yr",        brand:"Glenfiddich", category:"distilled", subcategory:"Whisky",         price:36.00, volume:"700ml", abv:"high", emoji:"🥃", tags:["single malt","scotch","premium"] },
  { id:38, name:"Jameson Irish",           brand:"Jameson",    category:"distilled",   subcategory:"Whisky",         price:22.00, volume:"700ml", abv:"high", emoji:"🥃", tags:["irish","smooth","blended"] },

  /* ── DISTILLED » Vodka ── */
  { id:39, name:"Absolut Original",        brand:"Absolut",    category:"distilled",   subcategory:"Vodka",          price:18.00, volume:"700ml", abv:"high", emoji:"🫙", tags:["swedish","neutral","classic"] },
  { id:40, name:"Grey Goose",              brand:"Grey Goose", category:"distilled",   subcategory:"Vodka",          price:34.00, volume:"700ml", abv:"high", emoji:"🫙", tags:["french","premium","smooth"] },
  { id:41, name:"Smirnoff No.21",          brand:"Smirnoff",   category:"distilled",   subcategory:"Vodka",          price:14.00, volume:"700ml", abv:"high", emoji:"🫙", tags:["russian","triple distilled","value"] },
  { id:42, name:"Belvedere Pure",          brand:"Belvedere",  category:"distilled",   subcategory:"Vodka",          price:38.00, volume:"700ml", abv:"high", emoji:"🫙", tags:["polish","rye","ultra-premium"] },

  /* ── DISTILLED » Rum ── */
  { id:43, name:"Bacardi Carta Blanca",    brand:"Bacardi",    category:"distilled",   subcategory:"Rum",            price:16.00, volume:"700ml", abv:"high", emoji:"🍹", tags:["white","light","cocktail"] },
  { id:44, name:"Captain Morgan Spiced",   brand:"Captain Morgan", category:"distilled", subcategory:"Rum",          price:18.00, volume:"700ml", abv:"high", emoji:"🍹", tags:["spiced","golden","sweet"] },
  { id:45, name:"Diplomatico Reserva",     brand:"Diplomatico", category:"distilled",  subcategory:"Rum",            price:32.00, volume:"700ml", abv:"high", emoji:"🍹", tags:["venezuelan","dark","premium","sipping"] },

  /* ── DISTILLED » Gin ── */
  { id:46, name:"Bombay Sapphire",         brand:"Bombay",     category:"distilled",   subcategory:"Gin",            price:22.00, volume:"700ml", abv:"high", emoji:"🌿", tags:["london dry","botanical","classic"] },
  { id:47, name:"Hendrick's",              brand:"Hendrick's", category:"distilled",   subcategory:"Gin",            price:30.00, volume:"700ml", abv:"high", emoji:"🌿", tags:["scottish","cucumber","floral","premium"] },
  { id:48, name:"Tanqueray No.Ten",        brand:"Tanqueray",  category:"distilled",   subcategory:"Gin",            price:28.00, volume:"700ml", abv:"high", emoji:"🌿", tags:["citrus","fresh","premium"] },
  { id:49, name:"Monkey 47",              brand:"Monkey 47",  category:"distilled",   subcategory:"Gin",            price:42.00, volume:"500ml", abv:"high", emoji:"🌿", tags:["german","47 botanicals","ultra-premium"] },

  /* ── DISTILLED » Tequila ── */
  { id:50, name:"Jose Cuervo Silver",      brand:"Jose Cuervo", category:"distilled",  subcategory:"Tequila",        price:20.00, volume:"700ml", abv:"high", emoji:"🌵", tags:["silver","blanco","cocktail"] },
  { id:51, name:"Patron Silver",           brand:"Patron",     category:"distilled",   subcategory:"Tequila",        price:40.00, volume:"700ml", abv:"high", emoji:"🌵", tags:["premium","100% agave","smooth"] },
  { id:52, name:"Don Julio Blanco",        brand:"Don Julio",  category:"distilled",   subcategory:"Tequila",        price:48.00, volume:"700ml", abv:"high", emoji:"🌵", tags:["ultra-premium","100% agave","clean"] },
];
