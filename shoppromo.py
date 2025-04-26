import logging
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ConversationHandler

# Logging sozlamalari
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Admin IDs ro'yxati
ADMIN_IDS = [12345678, 87654321]  # Bu yerga adminlarning telegram ID larini qo'shing

# Conversation handler states
EDIT_STORE_NAME, EDIT_STORE_DESC, EDIT_STORE_ADDRESS, EDIT_STORE_PHONE, EDIT_STORE_HOURS = range(5)
ADD_PRODUCT_NAME, ADD_PRODUCT_PRICE, ADD_PRODUCT_IMAGE = range(5, 8)
ADD_PROMOTION_TITLE, ADD_PROMOTION_DESC = range(8, 10)
ADD_STORE_NAME, ADD_STORE_DESC, ADD_STORE_ADDRESS, ADD_STORE_PHONE, ADD_STORE_HOURS = range(10, 15)

# Bizning do'konlar ma'lumotlari
stores = {
    'electronics': {
        'name': 'Elektron Dunyo',
        'description': 'Eng so\'nggi elektronika mahsulotlarini taklif etuvchi do\'kon',
        'address': 'Toshkent sh., Chilonzor tumani, 15-mavze, 37-uy',
        'phone': '+998 90 123 45 67',
        'working_hours': '09:00 - 21:00',
        'products': [
            {'name': 'iPhone 15', 'price': '12,000,000 so\'m', 'image': 'https://example.com/iphone15.jpg'},
            {'name': 'Samsung Galaxy S24', 'price': '10,500,000 so\'m', 'image': 'https://example.com/s24.jpg'},
            {'name': 'MacBook Pro', 'price': '18,000,000 so\'m', 'image': 'https://example.com/macbook.jpg'},
        ],
        'location': [41.2995, 69.2401],
    },
    'clothing': {
        'name': 'Fashion Uz',
        'description': 'Zamonaviy kiyimlar va aksessuarlar do\'koni',
        'address': 'Toshkent sh., Yunusobod tumani, 4-mavze, 12-uy',
        'phone': '+998 90 987 65 43',
        'working_hours': '10:00 - 22:00',
        'products': [
            {'name': 'Ko\'ylak klassik', 'price': '350,000 so\'m', 'image': 'https://example.com/shirt.jpg'},
            {'name': 'Jinsi shimlar', 'price': '450,000 so\'m', 'image': 'https://example.com/jeans.jpg'},
            {'name': 'Sport krossovkalari', 'price': '650,000 so\'m', 'image': 'https://example.com/sneakers.jpg'},
        ],
        'location': [41.3456, 69.2845],
    },
    'grocery': {
        'name': 'Makro Market',
        'description': 'Kundalik oziq-ovqat va uy uchun mahsulotlar',
        'address': 'Toshkent sh., Mirzo Ulug\'bek tumani, 6-mavze, 24-uy',
        'phone': '+998 90 456 78 90',
        'working_hours': '08:00 - 23:00',
        'products': [
            {'name': 'Go\'sht mahsulotlari', 'price': '80,000 so\'m/kg', 'image': 'https://example.com/meat.jpg'},
            {'name': 'Sut mahsulotlari', 'price': '15,000 so\'m', 'image': 'https://example.com/dairy.jpg'},
            {'name': 'Mevalar', 'price': '25,000 so\'m/kg', 'image': 'https://example.com/fruits.jpg'},
        ],
        'location': [41.3245, 69.2654],
    }
}

# Aktsiyalar ma'lumotlari
promotions = [
    {
        'title': 'Hafta aksiyasi',
        'description': 'Juma-Yakshanba kunlari barcha elektronika mahsulotlariga 15% chegirma!'
    },
    {
        'title': '1+1=3',
        'description': 'Ikki dona kiyim xarid qilsangiz, uchinchisi sovg\'a!'
    },
    {
        'title': 'Tug\'ilgan kun aksiyasi',
        'description': 'Tug\'ilgan kuningizda 20% chegirma!'
    }
]

# Bog'lanish ma'lumotlari
contact_info = {
    'phone': '+998 71 123 45 67',
    'telegram': '@YourCompany',
    'email': 'info@yourcompany.uz',
    'website': 'www.yourcompany.uz',
    'working_hours': '09:00 - 18:00, Dushanba-Shanba'
}

# Bot token
BOT_TOKEN = '7668891438:AAG5Mj55BP6ZoGjCBS3EPd7Wf2ZXglz_1pY'

# Start buyrug'i uchun handler
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_id = user.id
    
    context.user_data['is_admin_mode'] = False
    
    if user_id in ADMIN_IDS:
        await update.message.reply_html(
            f"Assalomu alaykum, {user.mention_html()}! 👋\n\n"
            f"Do'konlarimiz botiga xush kelibsiz! Bu bot orqali siz:\n"
            f"- Do'konlarimiz haqida ma'lumot olishingiz\n"
            f"- Mahsulotlarni ko'rishingiz\n"
            f"- Aktsiyalar va chegirmalar haqida bilib turishingiz mumkin\n\n"
            f"Siz ADMIN sifatida ro'yxatdan o'tgansiz. Admin panelga kirish uchun /admin buyrug'ini yuboring.\n\n"
            f"Oddiy foydalanuvchi sifatida davom etish uchun quyidagi tugmalardan birini tanlang:",
            reply_markup=get_main_menu()
        )
    else:
        await update.message.reply_html(
            f"Assalomu alaykum, {user.mention_html()}! 👋\n\n"
            f"Do'konlarimiz botiga xush kelibsiz! Bu bot orqali siz:\n"
            f"- Do'konlarimiz haqida ma'lumot olishingiz\n"
            f"- Mahsulotlarni ko'rishingiz\n"
            f"- Aktsiyalar va chegirmalar haqida bilib turishingiz mumkin\n\n"
            f"Boshlash uchun quyidagi tugmalardan birini tanlang:",
            reply_markup=get_main_menu()
        )

# Admin panelga kirish
async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    if user_id not in ADMIN_IDS:
        await update.message.reply_text("Siz admin emas ekansiz. Bu buyruq faqat adminlar uchun.")
        return
    
    context.user_data['is_admin_mode'] = True
    
    await update.message.reply_text(
        "Admin panelga xush kelibsiz! Nimani o'zgartirmoqchisiz?",
        reply_markup=get_admin_menu()
    )

# Admin paneldan chiqish
async def exit_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['is_admin_mode'] = False
    
    await update.message.reply_text(
        "Admin paneldan chiqildi. Oddiy foydalanuvchi rejimiga o'tildi.",
        reply_markup=get_main_menu()
    )

# Asosiy menyu uchun klaviatura
def get_main_menu():
    keyboard = [
        ['🏪 Do\'konlar', '🛍 Mahsulotlar'],
        ['🔥 Aktsiyalar', '💬 Biz haqimizda'],
        ['📞 Bog\'lanish']
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

# Admin menyu uchun klaviatura
def get_admin_menu():
    keyboard = [
        ['🏪 Do\'konlarni boshqarish', '🛍 Mahsulotlarni boshqarish'],
        ['🔥 Aktsiyalarni boshqarish', '📞 Bog\'lanish ma\'lumotlarini boshqarish'],
        ['👤 Oddiy rejimga qaytish']
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

# Do'konlar ro'yxatini ko'rsatish
async def show_stores(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = []
    for store_id, store_info in stores.items():
        keyboard.append([InlineKeyboardButton(store_info['name'], callback_data=f"store_{store_id}")])
    
    keyboard.append([InlineKeyboardButton("⬅️ Orqaga", callback_data="back_to_main")])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "Quyidagi do'konlarimizdan birini tanlang:",
        reply_markup=reply_markup
    )

# Do'kon haqidagi ma'lumotlarni ko'rsatish
async def store_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    store_id = query.data.split('_')[1]
    store = stores[store_id]
    
    message_text = f"*{store['name']}*\n\n"
    message_text += f"*Ma'lumot:* {store['description']}\n"
    message_text += f"*Manzil:* {store['address']}\n"
    message_text += f"*Telefon:* {store['phone']}\n"
    message_text += f"*Ish vaqti:* {store['working_hours']}\n\n"
    
    keyboard = [
        [InlineKeyboardButton("📦 Mahsulotlar", callback_data=f"products_{store_id}")],
        [InlineKeyboardButton("📍 Lokatsiya", callback_data=f"location_{store_id}")],
        [InlineKeyboardButton("⬅️ Orqaga", callback_data="back_to_stores")]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        text=message_text,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

# Do'kondagi mahsulotlarni ko'rsatish
async def store_products(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    store_id = query.data.split('_')[1]
    store = stores[store_id]
    
    message_text = f"*{store['name']} do'konidagi mahsulotlar:*\n\n"
    
    for product in store['products']:
        message_text += f"*{product['name']}*\n"
        message_text += f"Narx: {product['price']}\n\n"
    
    keyboard = [
        [InlineKeyboardButton("🛒 Buyurtma berish", callback_data=f"order_{store_id}")],
        [InlineKeyboardButton("⬅️ Orqaga", callback_data=f"store_{store_id}")]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        text=message_text,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

# Do'kon lokatsiyasini yuborish
async def store_location(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    store_id = query.data.split('_')[1]
    store = stores[store_id]
    
    # Avval joriy xabarni o'chiramiz
    await query.delete_message()
    
    # So'ng lokatsiyani yuboramiz
    await context.bot.send_location(
        chat_id=query.message.chat_id,
        latitude=store['location'][0],
        longitude=store['location'][1]
    )
    
    # Ma'lumotlarni yana yuboramiz
    message_text = f"*{store['name']}* lokatsiyasi yuqorida ko'rsatilgan.\n"
    message_text += f"*Manzil:* {store['address']}"
    
    keyboard = [
        [InlineKeyboardButton("⬅️ Orqaga", callback_data=f"store_{store_id}")]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await context.bot.send_message(
        chat_id=query.message.chat_id,
        text=message_text,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

# Buyurtma berish
async def order_products(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    store_id = query.data.split('_')[1]
    store = stores[store_id]
    
    message_text = "Buyurtma berish uchun quyidagi raqamga qo'ng'iroq qiling:\n\n"
    message_text += f"📞 *{store['phone']}*\n\n"
    message_text += "Yoki ma'lumotlaringizni qoldiring, operatorimiz siz bilan bog'lanadi.\n"
    message_text += "Buning uchun /contact buyrug'ini yuboring."
    
    keyboard = [
        [InlineKeyboardButton("⬅️ Orqaga", callback_data=f"products_{store_id}")]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        text=message_text,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

# Biz haqimizda
async def about_us(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message_text = "*Biz haqimizda*\n\n"
    message_text += "Bizning kompaniyamiz 2010 yildan beri O'zbekiston bozorida faoliyat yuritib kelmoqda. "
    message_text += "Bizning maqsadimiz - mijozlarimizga yuqori sifatli mahsulotlarni qulay narxlarda taqdim etish.\n\n"
    message_text += "Bizning afzalliklarimiz:\n"
    message_text += "✅ Hamyonbop narxlar\n"
    message_text += "✅ Yuqori sifatli mahsulotlar\n"
    message_text += "✅ Tez yetkazib berish\n"
    message_text += "✅ Mijozlar uchun qo'llab-quvvatlash xizmati\n\n"
    message_text += "Bizni tanlaganingiz uchun rahmat!"
    
    await update.message.reply_text(
        message_text,
        parse_mode='Markdown'
    )

# Aktsiyalar
async def promotions_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message_text = "*🔥 AKTUAL AKTSIYALAR 🔥*\n\n"
    
    for i, promo in enumerate(promotions, 1):
        message_text += f"{i}. *{promo['title']}* - {promo['description']}\n\n"
    
    message_text += "Aktsiyalar vaqtinchalik. Batafsil ma'lumot olish uchun do'konlarimizga tashrif buyuring."
    
    await update.message.reply_text(
        message_text,
        parse_mode='Markdown'
    )

# Bog'lanish
async def contact_us(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message_text = "*Biz bilan bog'lanish*\n\n"
    message_text += f"📞 Call-markaz: {contact_info['phone']}\n"
    message_text += f"📱 Telegram: {contact_info['telegram']}\n"
    message_text += f"📧 Email: {contact_info['email']}\n"
    message_text += f"🌐 Veb-sayt: {contact_info['website']}\n\n"
    message_text += f"Ish vaqti: {contact_info['working_hours']}"
    
    await update.message.reply_text(
        message_text,
        parse_mode='Markdown'
    )

# Admin: Do'konlarni boshqarish
async def manage_stores(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = []
    for store_id, store_info in stores.items():
        keyboard.append([InlineKeyboardButton(store_info['name'], callback_data=f"admin_store_{store_id}")])
    
    keyboard.append([InlineKeyboardButton("➕ Yangi do'kon qo'shish", callback_data="admin_add_store")])
    keyboard.append([InlineKeyboardButton("⬅️ Orqaga", callback_data="back_to_admin")])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "Do'konlarni boshqarish paneli. Quyidagi do'konlardan birini tanlang yoki yangi do'kon qo'shing:",
        reply_markup=reply_markup
    )

# Admin: Do'kon ma'lumotlarini ko'rsatish
async def admin_store_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    store_id = query.data.split('_')[2]
    store = stores[store_id]
    
    message_text = f"*{store['name']}*\n\n"
    message_text += f"*Ma'lumot:* {store['description']}\n"
    message_text += f"*Manzil:* {store['address']}\n"
    message_text += f"*Telefon:* {store['phone']}\n"
    message_text += f"*Ish vaqti:* {store['working_hours']}\n\n"
    
    keyboard = [
        [InlineKeyboardButton("✏️ Nomini o'zgartirish", callback_data=f"edit_store_name_{store_id}")],
        [InlineKeyboardButton("✏️ Ma'lumotini o'zgartirish", callback_data=f"edit_store_desc_{store_id}")],
        [InlineKeyboardButton("✏️ Manzilni o'zgartirish", callback_data=f"edit_store_address_{store_id}")],
        [InlineKeyboardButton("✏️ Telefonni o'zgartirish", callback_data=f"edit_store_phone_{store_id}")],
        [InlineKeyboardButton("✏️ Ish vaqtini o'zgartirish", callback_data=f"edit_store_hours_{store_id}")],
        [InlineKeyboardButton("📦 Mahsulotlarni boshqarish", callback_data=f"admin_products_{store_id}")],
        [InlineKeyboardButton("❌ Do'konni o'chirish", callback_data=f"delete_store_{store_id}")],
        [InlineKeyboardButton("⬅️ Orqaga", callback_data="back_to_manage_stores")]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        text=message_text,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

# Admin: Do'kon nomini o'zgartirish
async def edit_store_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    store_id = query.data.split('_')[3]
    context.user_data['editing_store'] = store_id
    
    await query.edit_message_text(
        f"Iltimos, \"{stores[store_id]['name']}\" do'koni uchun yangi nomni kiriting:",
        parse_mode='Markdown'
    )
    
    return EDIT_STORE_NAME

async def process_edit_store_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    store_id = context.user_data['editing_store']
    new_name = update.message.text
    
    stores[store_id]['name'] = new_name
    
    await update.message.reply_text(
        f"Do'kon nomi muvaffaqiyatli o'zgartirildi: *{new_name}*",
        parse_mode='Markdown',
        reply_markup=get_admin_menu()
    )
    
    return ConversationHandler.END

# Admin: Do'kon ma'lumotini o'zgartirish
async def edit_store_desc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    store_id = query.data.split('_')[3]
    context.user_data['editing_store'] = store_id
    
    await query.edit_message_text(
        f"Iltimos, \"{stores[store_id]['name']}\" do'koni uchun yangi ma'lumotni kiriting:",
        parse_mode='Markdown'
    )
    
    return EDIT_STORE_DESC

async def process_edit_store_desc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    store_id = context.user_data['editing_store']
    new_desc = update.message.text
    
    stores[store_id]['description'] = new_desc
    
    await update.message.reply_text(
        f"Do'kon ma'lumoti muvaffaqiyatli o'zgartirildi.",
        reply_markup=get_admin_menu()
    )
    
    return ConversationHandler.END

# Admin: Do'kon manzilini o'zgartirish
async def edit_store_address(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    store_id = query.data.split('_')[3]
    context.user_data['editing_store'] = store_id
    
    await query.edit_message_text(
        f"Iltimos, \"{stores[store_id]['name']}\" do'koni uchun yangi manzilni kiriting:",
        parse_mode='Markdown'
    )
    
    return EDIT_STORE_ADDRESS

async def process_edit_store_address(update: Update, context: ContextTypes.DEFAULT_TYPE):
    store_id = context.user_data['editing_store']
    new_address = update.message.text
    
    stores[store_id]['address'] = new_address
    
    await update.message.reply_text(
        f"Do'kon manzili muvaffaqiyatli o'zgartirildi.",
        reply_markup=get_admin_menu()
    )
    
    return ConversationHandler.END

# Admin: Do'kon telefonini o'zgartirish
async def edit_store_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    store_id = query.data.split('_')[3]
    context.user_data['editing_store'] = store_id
    
    await query.edit_message_text(
        f"Iltimos, \"{stores[store_id]['name']}\" do'koni uchun yangi telefon raqamini kiriting:",
        parse_mode='Markdown'
    )
    
    return EDIT_STORE_PHONE

async def process_edit_store_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    store_id = context.user_data['editing_store']
    new_phone = update.message.text
    
    stores[store_id]['phone'] = new_phone
    
    await update.message.reply_text(
        f"Do'kon telefon raqami muvaffaqiyatli o'zgartirildi.",
        reply_markup=get_admin_menu()
    )
    
    return ConversationHandler.END

# Admin: Do'kon ish vaqtini o'zgartirish
async def edit_store_hours(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    store_id = query.data.split('_')[3]
    context.user_data['editing_store'] = store_id
    
    await query.edit_message_text(
        f"Iltimos, \"{stores[store_id]['name']}\" do'koni uchun yangi ish vaqtini kiriting:",
        parse_mode='Markdown'
    )
    
    return EDIT_STORE_HOURS

async def process_edit_store_hours(update: Update, context: ContextTypes.DEFAULT_TYPE):
    store_id = context.user_data['editing_store']
    new_hours = update.message.text
    
    stores[store_id]['working_hours'] = new_hours
    
    await update.message.reply_text(
        f"Do'kon ish vaqti muvaffaqiyatli o'zgartirildi.",
        reply_markup=get_admin_menu()
    )
    
    return ConversationHandler.END

# Admin: Do'konni o'chirish
async def delete_store(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    store_id = query.data.split('_')[2]
    store_name = stores[store_id]['name']
    
    del stores[store_id]
    
    await query.edit_message_text(
        f"*{store_name}* do'koni muvaffaqiyatli o'chirildi!",
        parse_mode='Markdown'
    )
    
    # Qayta do'konlar ro'yxatini ko'rsatamiz
    keyboard = []
    for store_id, store_info in stores.items():
        keyboard.append([InlineKeyboardButton(store_info['name'], callback_data=f"admin_store_{store_id}")])
    
    keyboard.append([InlineKeyboardButton("➕ Yangi do'kon qo'shish", callback_data="admin_add_store")])
    keyboard.append([InlineKeyboardButton("⬅️ Orqaga", callback_data="back_to_admin")])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await context.bot.send_message(
        chat_id=query.message.chat_id,
        text="Do'konlarni boshqarish paneli. Quyidagi do'konlardan birini tanlang yoki yangi do'kon qo'shing:",
        reply_markup=reply_markup
    )

# Admin: Yangi do'kon qo'shish
async def add_store(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    await query.edit_message_text(
        "Yangi do'kon qo'shish. Iltimos, do'kon nomini kiriting:",
        parse_mode='Markdown'
    )
    
    return ADD_STORE_NAME

async def process_add_store_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    new_store_name = update.message.text
    context.user_data['new_store'] = {'name': new_store_name, 'products': []}
    
    await update.message.reply_text(
        f"Do'kon nomi: *{new_store_name}*\n\nEndi do'kon tavsifini kiriting:",
        parse_mode='Markdown'
    )
    
    return ADD_STORE_DESC

async def process_add_store_desc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    new_store_desc = update.message.text
    context.user_data['new_store']['description'] = new_store_desc
    
    await update.message.reply_text(
        f"Do'kon tavsifi saqlandi.\n\nEndi do'kon manzilini kiriting:"
    )
    
    return ADD_STORE_ADDRESS

async def process_add_store_address(update: Update, context: ContextTypes.DEFAULT_TYPE):
    new_store_address = update.message.text
    context.user_data['new_store']['address'] = new_store_address
    
    await update.message.reply_text(
        f"Do'kon manzili saqlandi.\n\nEndi do'kon telefon raqamini kiriting:"
    )
    
    return ADD_STORE_PHONE

async def process_add_store_phone(update: Update
