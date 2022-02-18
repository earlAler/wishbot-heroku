import os
import config
import logging
import uuid
import psycopg2
from aiogram import Bot, types, Dispatcher, executor
from aiogram.utils.callback_data import CallbackData
from aiogram.utils.exceptions import MessageNotModified
from aiogram.dispatcher import FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.utils.executor import start_webhook
from contextlib import suppress
from datetime import datetime
# from flask import flask, request

try:

    # conn = psycopg2.connect(host=config.host,
    #                         user=config.user,
    #                         password=config.password,
    #                         port=config.port,
    #                         database=config.db_name)
    conn = psycopg2.connect(config.DB_URI, sslmode = "require")
    conn.autocommit = True

    bot = Bot(token=config.BOT_TOKEN)
    # server = flask(__name__)
    dp = Dispatcher(bot, storage=MemoryStorage())
    logging.basicConfig(level=logging.INFO)
    WEBHOOK_HOST = f'https://boxwishesbot.herokuapp.com/'
    WEBHOOK_PATH = f'/{config.BOT_TOKEN}'
    WEBHOOK_URL = f'{WEBHOOK_HOST}{WEBHOOK_PATH}'

    callback_direct = CallbackData("enum", "action")


    # Форма и поля к ней
    class Form(StatesGroup):
        name = State()
        topic = State()
        text = State()
        img = State()
        # fin = State()
        back = State()


    def get_keyboard():  # Кнопки направления завки
        buttons = [
            types.InlineKeyboardButton(text="Русская кожа", callback_data=callback_direct.new(action="rk")),
            types.InlineKeyboardButton(text="Инвест", callback_data=callback_direct.new(action="inv")),
            types.InlineKeyboardButton(text="Теплоприбор", callback_data=callback_direct.new(action="tpr")),
            types.InlineKeyboardButton(text="Точинвест", callback_data=callback_direct.new(action="tinv"))
        ]
        keyboard = types.InlineKeyboardMarkup(row_width=1)
        keyboard.add(*buttons)
        return keyboard


    def get_back():  # Для кнопки назад
        buttons = [
            types.InlineKeyboardButton(text="Отмена", callback_data=callback_direct.new(action="back"))
        ]
        keyboard = types.InlineKeyboardMarkup(row_width=1)
        keyboard.add(*buttons)
        return keyboard

    def get_option():  # Для кнопки назад
        buttons = [
            types.InlineKeyboardButton(text="Да", callback_data=callback_direct.new(action="yes")),
            types.InlineKeyboardButton(text="Нет", callback_data=callback_direct.new(action="no"))
        ]
        keyboard = types.InlineKeyboardMarkup(row_width=2)
        keyboard.add(*buttons)
        return keyboard


    # @dp.callback_query_handler(text="back", state=Form.back)
    # async def callback_back(call: types.CallbackQuery):
    #     await cmd_switch(call.message)
    #     # await call.message.edit_reply_markup()
    #     # await state.reset_state(with_data=False)

    # @dp.message_handler(text="back", state=Form.back)
    # async def cmd_switch(message: types.Message):
    #     #user_data["username"] = 0
    #     # await state.reset_state()
    #     await Form.name.set()
    #     await message.answer("Куда хочешь направить:", reply_markup=get_keyboard())

    @dp.message_handler(commands=["start", "s"], state=None)
    async def cmd_switch(message: types.Message):
        # user_data["username"] = 0
        await Form.name.set()
        await message.answer("Куда хочешь направить: ", reply_markup=get_keyboard())


    # Добавляем возможность отмены
    @dp.callback_query_handler(callback_direct.filter(action="back"), state='*')
    @dp.message_handler(state='*', commands='cancel')
    @dp.message_handler(Text(equals='отмена', ignore_case=True), state='*')
    async def cancel_handler(message: types.Message, state: FSMContext):
        current_state = await state.get_state()
        if current_state is None:
            return
        await state.finish()
        await message.message.answer('Действия отменены. Для начала введите /start или /s')
        await message.answer()
        # await cmd_switch(message)


    @dp.callback_query_handler(callback_direct.filter(action=["rk", "inv", "tpr", "tinv"]), state=Form.name)
    async def callback_directs(call: types.CallbackQuery, callback_data: dict, state: FSMContext):
        action = callback_data["action"]
        directs = {"rk": "Русская кожа", "inv": "Инвест", "tpr": "Теплоприбор", "tinv": "Точинвест"}
        if action == "rk":
            async with state.proxy() as user_data:
                user_data["username"] = call.from_user.first_name
                user_data["Direction"] = action
            await Form.next()
            await call.message.edit_text("Выбранное направление: " + directs[action] + "\nВведите тему пожелания:",
                                         reply_markup=get_back())
            # await update_text(call.message, action)
        elif action == "inv":
            async with state.proxy() as user_data:
                user_data["username"] = call.from_user.first_name
                user_data["Direction"] = action
            await Form.next()
            await call.message.edit_text("Выбранное направление: " + directs[action] + "\nВведите тему пожелания:",
                                         reply_markup=get_back())
        elif action == "tpr":
            async with state.proxy() as user_data:
                user_data["username"] = call.from_user.first_name
                user_data["Direction"] = action
            await Form.next()
            await call.message.edit_text("Выбранное направление: " + directs[action] + "\nВведите тему пожелания:",
                                         reply_markup=get_back())
        elif action == "tinv":
            async with state.proxy() as user_data:
                user_data["username"] = call.from_user.first_name
                user_data["Direction"] = action
            await Form.next()
            await call.message.edit_text("Выбранное направление: " + directs[action] + "\nВведите тему пожелания:",
                                         reply_markup=get_back())
        await call.answer()


    # Общая функция для обновления текста после выбора напр.
    # @dp.message_handler(state=Form.back)
    # async def update_text(message: types.Message, action: str):
    #     with suppress(MessageNotModified):
    #         directs = {"rk":"Русская кожа","inv":"Инвест","tpr":"Теплоприбор","tinv":"Точинвест"}
    #         await message.edit_text("Выбранное направление: "+directs[action]+"\nВведите тему:", reply_markup=get_back())
    #         # await Form.next()


    @dp.message_handler(state=Form.topic)
    async def topic_text(message: types.Message, state: FSMContext):
        with suppress(MessageNotModified):
            async with state.proxy() as user_data:
                user_data["Topic"] = message.text
            await message.answer("Напишите пожелание:", reply_markup=get_back())
            await Form.next()


    # @dp.message_handler(content_types=["photo"], state=Form.text)
    # async def photo_handler(message: types.Message):
    #     photo = message.photo.pop()
    #     await photo.download('img/test.jpg')
    #     # await print(f"YES")




    @dp.message_handler(state=Form.text)
    async def text_write(message: types.Message, state: FSMContext):
        with suppress(MessageNotModified):
            async with state.proxy() as user_data:
                user_data["Text"] = message.text
                # user_data["img"] = message.photo[0].file_id
                user_data["UID"] = str(uuid.uuid1())
                user_data["Datetime"] = datetime.now(tz=None)+datetime.timedelta(hours = 3)  # по времени gmt+3
            await Form.next()
            await message.answer("Желаете прикрепить изображение?", reply_markup=get_option())

                # filename, file_ext = os.path.split(file_img.file_path)
                # download_img = bot.download_file(file_img.file_path)
                # src = 'img/' + user_data["img"] + file_ext
                # photo = message.photo.pop()
                # await photo.download('img/' + user_data["img"] + '.jpg')


    @dp.callback_query_handler(callback_direct.filter(action="yes"), state=Form.img)
    async def send_img(call: types.CallbackQuery):
        with suppress(MessageNotModified):
            await call.message.edit_text("Прикрепите изображение")
            await call.answer()
            # await Form.next()
            # content_types = ["photo"]


    @dp.message_handler(content_types = ["photo"], state = Form.img)
    async def get_img(message: types.InputMediaPhoto, state: FSMContext):
        with suppress(MessageNotModified):
            imgs = []
            img_id = await bot.get_file(message.photo[-1].file_id)
            imgs.append(img_id.file_id)
            print("VOT ONO: ", imgs)
            # images = types.MediaGroup()
            # img.append(message.photo[-1].file_id)
            # for img_id in img:
            #     images.attach_photo(img_id)
            # print(img)
            # print(images.media)
            # async with state.proxy() as user_data:
            #     user_data["img"] = img #message.photo[-1].file_id   # photo[0] - миниатюра
            # async with state.proxy() as user_data:
            #     print(user_data)
            keys = ["UID", "Datetime", "Topic", "Text", "img", "Direction",
                    "username"]  # для формирования верной последовательности вставки
            async with state.proxy() as user_data:
                user_data["img"] = imgs
                print(user_data)
                with conn.cursor() as cursor:
                    cursor.execute(
                        """INSERT INTO "BoxWishes" ("ID","Datetime","Topic", "Text", "img","Direction", "UserID")
                        values (%s, %s, %s, %s, %s, %s, %s); """, [user_data.get(key) for key in keys]
                    )
                    print(f"INSERTED")
            with conn.cursor() as cursor:
                cursor.execute(
                    """SELECT COUNT(DISTINCT "ID") FROM "BoxWishes";"""
                )
                count_wish = cursor.fetchone()
                await message.answer("Пожелание принято. Номер Вашего пожелания: " + str(count_wish[0]))
            # photo = message.photo.pop()  #для скачивания
            # print(message.photo[-1].get_file())
            # await photo.download('img/' + user_data["img"] + '.jpg')
            # print(f"YES")
            # await out_app(message.text)
            # await Form.next()
            await state.finish()



    # @dp.callback_query_handler(callback_direct.filter(action="no"), state=Form.img)
    # async def send_without_img(call: types.CallbackQuery):
    #     with suppress(MessageNotModified):
    #         await call.answer()
    #         await Form.next()
    #         # content_types = ["photo"]



    @dp.callback_query_handler(callback_direct.filter(action="no"), state=Form.img)
    async def out_without_img(call: types.callback_query, state: FSMContext):
        with suppress(MessageNotModified):
            with conn.cursor() as cursor:
                cursor.execute(
                    """SELECT COUNT(DISTINCT "ID") FROM "BoxWishes";"""
                )
                count_wish = cursor.fetchone()
            await call.message.answer("Пожелание принято. Номер Вашего пожелания: "+ str(count_wish[0]))
            await call.answer()
            async with state.proxy() as user_data:
                print(user_data)
            keys = ["UID","Datetime","Topic", "Text", "img","Direction", "username"]  #для формирования верной последовательности вставки
            async with state.proxy() as user_data:
                # file_img = bot.get_file(user_data["img"])
                # filename, file_ext = os.path.split(file_img.file_path)
                # download_img = bot.download_file(file_img.file_path)
                # src = 'img/' + user_data["img"] + file_ext
                # with open(src, 'wb') as nf:
                #     nf.write(download_img)
                with conn.cursor() as cursor:
                    cursor.execute(
                        """INSERT INTO "BoxWishes" ("ID","Datetime","Topic", "Text", "img","Direction", "UserID")
                        values (%s, %s, %s, %s, %s, %s, %s); """, [user_data.get(key) for key in keys]
                    )
                    print(f"INSERTED")
            await state.finish()


    async def on_startup(dp):
        logging.warning('Starting connection. ')
        await bot.set_webhook(WEBHOOK_URL, drop_pending_updates=True)

    async def on_shutdown(dp):
        logging.warning('Shutting down..')
        await bot.delete_webhook()
        await dp.storage.close()
        await dp.storage.wait_closed()

    # @dp.message_handler(state=Form.img)
    # async def topic_text(message: types.Message, state: FSMContext):
    #     with suppress(MessageNotModified):
    #         async with state.proxy() as user_data:
    #             user_data["Topic"] = message.text
    #         await message.answer("Желаете прикрепить изображение или файл:", reply_markup=get_back())
    #         await Form.next()

    if __name__ == "__main__":
        # executor.start_webhook (
        #     dispatcher = dp,
        #     webhook_path = WEBHOOK_PATH,
        #     on_startup=on_startup,
        #     on_shutdown = on_shutdown,
        #     skip_updates = True,
        #     host = '0.0.0.0',
        #     port = os.environ.get('PORT')
        # )
        # executor.start_webhook()
        # bot.remove_webhook()
        # bot.set_webhook(url = config.APP_URL)
        # server.run(host = '0.0.0.0', port = int(os.environ.get("PORT", 5000))
        executor.start_polling(dp, skip_updates=True)


except Exception as exc:
    print("Error while working: ", exc)
# finally:
#     if conn:
#         conn.close()
#         print("Connection closed")



