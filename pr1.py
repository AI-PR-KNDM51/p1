import logging
from telegram import (
    Update,
    ReplyKeyboardMarkup,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    ConversationHandler,
    CallbackQueryHandler,
    filters,
)

# Налаштування логування для відстеження подій та помилок
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

logger = logging.getLogger(__name__)

# Визначення станів для розмови
SELL, RENT, HELP, SELL_DETAILS, RENT_DETAILS = range(5)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Обробляє команду /start та відображає головне меню з варіантами дій.
    """
    # Створення клавіатури з варіантами
    reply_keyboard = [['Продати житло', 'Орендувати житло', 'Інформація']]
    await update.message.reply_text(
        'Вітаємо! Оберіть опцію:',
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True, resize_keyboard=True
        ),
    )
    return SELL  # Переходить до стану SELL

async def main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Обробляє вибір користувача з головного меню та переходить до відповідних станів.
    """
    choice = update.message.text  # Отримання тексту вибору
    if choice == 'Продати житло':
        context.user_data['action'] = 'sell'  # Зберігає дію користувача
        # Створення клавіатури з типами житла
        reply_keyboard = [['Квартира', 'Будинок', 'Гараж'], ['Будка', 'Тент']]
        await update.message.reply_text(
            'Оберіть тип житла:',
            reply_markup=ReplyKeyboardMarkup(
                reply_keyboard, one_time_keyboard=True, resize_keyboard=True
            ),
        )
        return SELL_DETAILS  # Переходить до стану SELL_DETAILS
    elif choice == 'Орендувати житло':
        context.user_data['action'] = 'rent'  # Зберігає дію користувача
        await update.message.reply_text(
            'Введіть бажану локацію або натисніть "Назад":',
            reply_markup=ReplyKeyboardMarkup(
                [['Назад']], one_time_keyboard=True, resize_keyboard=True
            ),
        )
        return RENT_DETAILS  # Переходить до стану RENT_DETAILS
    elif choice == 'Інформація':
        await inform_command(update, context)  # Викликає функцію інформації
        return SELL  # Залишається в стані SELL
    elif choice == 'Назад':
        return await start(update, context)  # Повертається до старту
    else:
        await update.message.reply_text('Будь ласка, оберіть опцію з меню.')
        return SELL  # Залишається в стані SELL

async def sell_details(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Обробляє деталі для продажу житла, збирає інформацію поетапно.
    """
    text = update.message.text  # Отримання тексту повідомлення
    if text == 'Назад':
        return await start(update, context)  # Повертається до старту
    user_data = context.user_data  # Доступ до даних користувача

    # Перевірка та збереження типу житла
    if 'property_type' not in user_data:
        user_data['property_type'] = text
        await update.message.reply_text('Введіть площу або натисніть "Назад":',
                                        reply_markup=ReplyKeyboardMarkup(
                                            [['Назад']], one_time_keyboard=True, resize_keyboard=True
                                        ),
                                        )
    # Перевірка та збереження площі
    elif 'area' not in user_data:
        if text == 'Назад':
            del user_data['property_type']  # Видаляє збережений тип житла
            # Відображає клавіатуру з типами житла та опцією "Назад"
            reply_keyboard = [['Квартира', 'Будинок', 'Гараж'], ['Назад']]
            await update.message.reply_text(
                'Оберіть тип житла:',
                reply_markup=ReplyKeyboardMarkup(
                    reply_keyboard, one_time_keyboard=True, resize_keyboard=True
                ),
            )
            return SELL_DETAILS
        user_data['area'] = text
        await update.message.reply_text('Введіть кількість кімнат або натисніть "Назад":',
                                        reply_markup=ReplyKeyboardMarkup(
                                            [['Назад']], one_time_keyboard=True, resize_keyboard=True
                                        ),
                                        )
    # Перевірка та збереження кількості кімнат
    elif 'rooms' not in user_data:
        if text == 'Назад':
            del user_data['area']  # Видаляє збережену площу
            await update.message.reply_text('Введіть площу або натисніть "Назад":',
                                            reply_markup=ReplyKeyboardMarkup(
                                                [['Назад']], one_time_keyboard=True, resize_keyboard=True
                                            ),
                                            )
            return SELL_DETAILS
        user_data['rooms'] = text
        await update.message.reply_text('Введіть локацію або натисніть "Назад":',
                                        reply_markup=ReplyKeyboardMarkup(
                                            [['Назад']], one_time_keyboard=True, resize_keyboard=True
                                        ),
                                        )
    # Перевірка та збереження локації
    elif 'location' not in user_data:
        if text == 'Назад':
            del user_data['rooms']  # Видаляє збережену кількість кімнат
            await update.message.reply_text('Введіть кількість кімнат або натисніть "Назад":',
                                            reply_markup=ReplyKeyboardMarkup(
                                                [['Назад']], one_time_keyboard=True, resize_keyboard=True
                                            ),
                                            )
            return SELL_DETAILS
        user_data['location'] = text
        await update.message.reply_text('Введіть ціну або натисніть "Назад":',
                                        reply_markup=ReplyKeyboardMarkup(
                                            [['Назад']], one_time_keyboard=True, resize_keyboard=True
                                        ),
                                        )
    # Перевірка та збереження ціни
    elif 'price' not in user_data:
        if text == 'Назад':
            del user_data['location']  # Видаляє збережену локацію
            await update.message.reply_text('Введіть локацію або натисніть "Назад":',
                                            reply_markup=ReplyKeyboardMarkup(
                                                [['Назад']], one_time_keyboard=True, resize_keyboard=True
                                            ),
                                            )
            return SELL_DETAILS
        user_data['price'] = text
        await update.message.reply_text('Дякуємо! Ваші дані збережено.')
        user_data.clear()  # Очищує дані користувача
        return ConversationHandler.END  # Завершує розмову
    return SELL_DETAILS  # Продовжує стан SELL_DETAILS

async def rent_details(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Обробляє деталі для оренди житла, збирає інформацію поетапно.
    """
    text = update.message.text  # Отримання тексту повідомлення
    if text == 'Назад':
        return await start(update, context)  # Повертається до старту
    user_data = context.user_data  # Доступ до даних користувача

    # Перевірка та збереження локації
    if 'location' not in user_data:
        user_data['location'] = text
        # Створення клавіатури з варіантами площі
        reply_keyboard = [['До 50м²', '50-100м²', '>100м²'], ['Назад']]
        await update.message.reply_text(
            'Оберіть бажану площу або натисніть "Назад":',
            reply_markup=ReplyKeyboardMarkup(
                reply_keyboard, one_time_keyboard=True, resize_keyboard=True
            ),
        )
    # Перевірка та збереження площі
    elif 'area' not in user_data:
        if text == 'Назад':
            del user_data['location']  # Видаляє збережену локацію
            await update.message.reply_text(
                'Введіть бажану локацію або натисніть "Назад":',
                reply_markup=ReplyKeyboardMarkup(
                    [['Назад']], one_time_keyboard=True, resize_keyboard=True
                ),
            )
            return RENT_DETAILS
        user_data['area'] = text
        await update.message.reply_text('Введіть кількість кімнат або натисніть "Назад":',
                                        reply_markup=ReplyKeyboardMarkup(
                                            [['Назад']], one_time_keyboard=True, resize_keyboard=True
                                        ),
                                        )
    # Перевірка та збереження кількості кімнат
    elif 'rooms' not in user_data:
        if text == 'Назад':
            del user_data['area']  # Видаляє збережену площу
            # Відображає клавіатуру з варіантами площі та опцією "Назад"
            reply_keyboard = [['До 50м²', '50-100м²', '>100м²'], ['Назад']]
            await update.message.reply_text(
                'Оберіть бажану площу або натисніть "Назад":',
                reply_markup=ReplyKeyboardMarkup(
                    reply_keyboard, one_time_keyboard=True, resize_keyboard=True
                ),
            )
            return RENT_DETAILS
        user_data['rooms'] = text
        await update.message.reply_text('Введіть діапазон цін або натисніть "Назад":',
                                        reply_markup=ReplyKeyboardMarkup(
                                            [['Назад']], one_time_keyboard=True, resize_keyboard=True
                                        ),
                                        )
    # Перевірка та збереження діапазону цін
    elif 'price_range' not in user_data:
        if text == 'Назад':
            del user_data['rooms']  # Видаляє збережену кількість кімнат
            await update.message.reply_text('Введіть кількість кімнат або натисніть "Назад":',
                                            reply_markup=ReplyKeyboardMarkup(
                                                [['Назад']], one_time_keyboard=True, resize_keyboard=True
                                            ),
                                            )
            return RENT_DETAILS
        user_data['price_range'] = text
        # Відображає список доступних варіантів оренди
        await update.message.reply_text('Ось список доступних варіантів:\n1. Квартира на вул. Шевченка, 50м², $300\n2. Будинок на вул. Лесі Українки, 100м², $500')
        user_data.clear()  # Очищує дані користувача
        return ConversationHandler.END  # Завершує розмову
    return RENT_DETAILS  # Продовжує стан RENT_DETAILS

async def inform_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Відправляє повідомлення з кнопкою для отримання зображення.
    """
    # Створення кнопки з callback_data
    button = InlineKeyboardButton('Натисніть, щоб отримати зображення', callback_data='get_image')
    reply_markup = InlineKeyboardMarkup([[button]])
    await update.message.reply_text('Натисніть кнопку нижче, щоб отримати зображення.', reply_markup=reply_markup)

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Обробляє натискання кнопок у повідомленнях з inline-клавіатурою.
    """
    query = update.callback_query  # Отримання запиту
    await query.answer()  # Відповідає на запит, щоб уникнути таймауту
    if query.data == 'get_image':
        # Відправляє фотографію за посиланням
        await query.message.reply_photo(photo='https://www.cambridgemaths.org/Images/The-trouble-with-graphs.jpg')
        await query.message.reply_text('Ось ваше зображення!')

def main() -> None:
    """
    Основна функція запуску бота, налаштовує обробники та запускає поллінг.
    """
    # Створення об'єкту додатку з токеном бота
    application = ApplicationBuilder().token('8137252780:AAGrFqlpmOXe00EyQjc3cs3D_Ub3Q29FNpE').build()

    # Налаштування ConversationHandler з різними станами
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],  # Початковий обробник
        states={
            SELL: [
                MessageHandler(
                    filters.TEXT & ~filters.COMMAND & filters.Regex('^(Продати житло|Орендувати житло|Інформація|Назад)$'), main_menu
                )
            ],
            SELL_DETAILS: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, sell_details),
            ],
            RENT_DETAILS: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, rent_details),
            ],
        },
        fallbacks=[CommandHandler('inform', inform_command)],  # Обробники для fallback
    )

    # Додавання обробників до додатку
    application.add_handler(conv_handler)
    application.add_handler(CommandHandler('inform', inform_command))
    application.add_handler(CallbackQueryHandler(button_callback))

    # Запуск бота з поллінгом
    application.run_polling()

if __name__ == '__main__':
    main()