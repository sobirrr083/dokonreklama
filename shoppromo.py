import logging
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, CallbackQueryHandler, filters

# Logging sozlamalari
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

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

# Bot token
BOT_TOKEN = '7668891438:AAG5Mj55BP6ZoGjCBS3EPd7Wf2ZXglz_1pY'

# Start buyrug'i uchun handler
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    await update.message.reply_html(
        f"Assalomu alaykum, {user.mention_html()}! 👋\n\n"
        f"Do'konlarimiz botiga xush kelibsiz! Bu bot orqali siz:\n"
        f"- Do'konlarimiz haqida ma'lumot olishingiz\n"
        f"- Mahsulotlarni ko'rishingiz\n"
        f"- Aktsiyalar va chegirmalar haqida bilib turishingiz mumkin\n\n"
        f"Boshlash uchun quyidagi tugmalardan birini tanlang:",
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
async def promotions(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message_text = "*🔥 AKTUAL AKTSIYALAR 🔥*\n\n"
    message_text += "1. *Hafta aksiyasi* - Juma-Yakshanba kunlari barcha elektronika mahsulotlariga 15% chegirma!\n\n"
    message_text += "2. *1+1=3* - Ikki dona kiyim xarid qilsangiz, uchinchisi sovg'a!\n\n"
    message_text += "3. *Tug'ilgan kun aksiyasi* - Tug'ilgan kuningizda 20% chegirma!\n\n"
    message_text += "Aktsiyalar vaqtinchalik. Batafsil ma'lumot olish uchun do'konlarimizga tashrif buyuring."
    
    await update.message.reply_text(
        message_text,
        parse_mode='Markdown'
    )

# Bog'lanish
async def contact_us(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message_text = "*Biz bilan bog'lanish*\n\n"
    message_text += "📞 Call-markaz: +998 71 123 45 67\n"
    message_text += "📱 Telegram: @YourCompany\n"
    message_text += "📧 Email: info@yourcompany.uz\n"
    message_text += "🌐 Veb-sayt: www.yourcompany.uz\n\n"
    message_text += "Ish vaqti: 09:00 - 18:00, Dushanba-Shanba"
    
    await update.message.reply_text(
        message_text,
        parse_mode='Markdown'
    )

# Matnli xabarlar bilan ishlash
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    
    if text == '🏪 Do\'konlar':
        await show_stores(update, context)
    elif text == '🛍 Mahsulotlar':
        keyboard = []
        for store_id, store_info in stores.items():
            keyboard.append([InlineKeyboardButton(f"{store_info['name']} mahsulotlari", callback_data=f"products_{store_id}")])
        
        keyboard.append([InlineKeyboardButton("⬅️ Orqaga", callback_data="back_to_main")])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            "Qaysi do'kon mahsulotlarini ko'rmoqchisiz:",
            reply_markup=reply_markup
        )
    elif text == '🔥 Aktsiyalar':
        await promotions(update, context)
    elif text == '💬 Biz haqimizda':
        await about_us(update, context)
    elif text == '📞 Bog\'lanish':
        await contact_us(update, context)
    else:
        await update.message.reply_text(
            "Tushunarsiz buyruq. Iltimos, quyidagi tugmalardan foydalaning.",
            reply_markup=get_main_menu()
        )

# Tugmalar bosilganda
async def button_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data
    
    if data == "back_to_main":
        await query.message.delete()
        await query.message.reply_text(
            "Asosiy menyu",
            reply_markup=get_main_menu()
        )
    elif data == "back_to_stores":
        keyboard = []
        for store_id, store_info in stores.items():
            keyboard.append([InlineKeyboardButton(store_info['name'], callback_data=f"store_{store_id}")])
        
        keyboard.append([InlineKeyboardButton("⬅️ Orqaga", callback_data="back_to_main")])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            "Quyidagi do'konlarimizdan birini tanlang:",
            reply_markup=reply_markup
        )
    elif data.startswith("store_"):
        await store_info(update, context)
    elif data.startswith("products_"):
        await store_products(update, context)
    elif data.startswith("location_"):
        await store_location(update, context)
    elif data.startswith("order_"):
        await order_products(update, context)

# Bog'lanish uchun ma'lumotlarni olish
async def contact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Iltimos, ismingizni, telefon raqamingizni va qiziqtirgan mahsulotingizni yozing. "
        "Masalan:\n\n"
        "Ism: Aziz\n"
        "Telefon: +998901234567\n"
        "Mahsulot: iPhone 15"
    )
    context.user_data['waiting_for_contact'] = True

# Asosiy funksiya
def main():
    application = ApplicationBuilder().token(BOT_TOKEN).build()
    
    # Buyruqlar uchun handlerlar
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("contact", contact))
    
    # Tugmalar uchun handlerlar
    application.add_handler(CallbackQueryHandler(button_click))
    
    # Xabarlar uchun handler
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # Botni ishga tushirish
    application.run_polling()

if __name__ == '__main__':
    main()
