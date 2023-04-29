from aiogram import types, executor, Dispatcher, Bot
from aiogram.dispatcher import FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.types import ReplyKeyboardMarkup
from datetime import datetime
import time, random, os, docx, textract, PyPDF2
from forms import Form 
import openai, fitz
import networkx as nx
import matplotlib.pyplot as plt



TOKEN = '6096486458:AAGMUDsTrCCb9bV3kks2qJRfq1od9vbNFG4' #BOTFATHER ТОКЕН
openai.api_key = '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' #OPENAI ТОКЕН
bot = Bot(token=TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())



@dp.message_handler(commands=['start'])
async def get_text_messages(message: types.Message, state: FSMContext):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    await bot.send_message(message.chat.id, 'Привет, пришли документ😊', reply_markup=keyboard)
    await Form.start.set()


# ОБРАБОТКА И УСТАНОВКА ПОЛУЧЕННОГО ДОКУМЕНТА
@dp.message_handler(content_types=types.ContentType.DOCUMENT, state= Form.start)
async def adc_function(message: types.Message, state: FSMContext):

    document = message.document
    user_id = str(message.from_user.id)
    file_name = os.path.join("", document.file_name)
    file = document.file_name.split('.')[-1]
    await bot.download_file_by_id(document.file_id, f'{user_id}.{file}')
    msg = await message.answer(f"Подождите, я генерирую ответ ☺️")


    try:
    # РАЗБИТИЕ ДОКУМЕНТА ПО РАСШИРЕНИЮ

        #проверка документа на расширение docx/doc
        if (file == 'doc') or (file == 'docx'):
            doc = docx.Document(f'{user_id}.{file}')
            text = '\n'.join([para.text for para in doc.paragraphs])

        #проверка документа на расширение txt
        if file == 'txt':
            with open(f'{user_id}.txt', encoding='utf-8') as f:
                text = f.read()


        #проверка документа на расширение pdf
        if file == 'pdf':
            with fitz.open(f'{user_id}.pdf') as pdf_file:
                    for page in pdf_file:
                        text = str(page.get_text())


        #ОБРАЩЕНИЕ К CHAT-GPT. ОГЛАВЛЕНИЕ ТЕКСТА И ОПРЕДЕЛЕНИЕ ПОДТЕМ
        response = openai.Completion.create(
                model="text-davinci-003",
                prompt=f"Определи концепцию/идею текста в двух-трех словах. Кластеризировать текст, разбить каждый класс на подтемы или задачи и перечисли их через запятую:\n\nПример:\nНазвание/концепция текста\n 1. Название ключевой идеи: подпункт, подпункт, подпункт\n2. Название ключевой идеи: подпункт, подпункт, подпункт\n\n И так обработать весь текст\n\nтекст:{text}",
                temperature=0.5,
                max_tokens=1000,
                top_p=1.0,
                frequency_penalty=0.5, 
                presence_penalty=0.0,
                    )
        

        #ГЕНЕРАЦИЯ ИНТЕЛЕКТУАЛЬНОЙ КАРТЫ
        try:
            #СОЗДАНИЕ ФАЙЛА ДЛЯ ПРОСМОТРА ИНТЕЛЕКТУАЛЬНОЙ КАРТЫ
            with open('graf.txt', 'w', encoding='utf-8') as document:
                document.write(response['choices'][0]['text'])
            with open(f'{user_id}.py', 'w', encoding='utf-8') as pw:
                    with open('graf.txt', 'r', encoding='utf-8') as gr:
                        graf_text = gr.read().split('\n')
                    pw.write(f"import os\nos.system('pip install matplotlib')\nos.system('pip install networkx')\nimport networkx as nx\nimport matplotlib.pyplot as plt\nG = nx.Graph()\nresult = {graf_text}\nheading = result[0].split(':')[-1]\nG.add_node(heading)\ndel result[0]\nfor x in result:\n  head = x.split(':')[0]\n  G.add_node(head)\n  G.add_edge(head, heading)\n  edges = x.split(':')[-1].split(',')\n  for i in edges:\n      G.add_node(i)\n      G.add_edge(i, head)\npos = nx.spring_layout(G, seed=42)  # Определяем расположение узлов на плоскости\nnx.draw(G, pos, with_labels=True)  # Рисуем граф с названиями узлов\nplt.show()")

            #СОЗДАНИЕ ИЗОБРАЖЕНИЯ ИНТЕЛЕКТУАЛЬНОЙ КАРТЫ
            G = nx.Graph()
            result = str(response['choices'][0]['text']).split('\n')
            heading = result[0].split(':')[-1]
            G.add_node(heading)
            del result[0]
            for x in result:
                head = x.split(':')[0]
                G.add_node(head)
                G.add_edge(head, heading)
                edges = x.split(':')[-1].split(',')
                for i in edges:
                    G.add_node(i)
                    G.add_edge(i, head)

            pos = nx.spring_layout(G, seed=42)  # Определяем расположение узлов на плоскости
            nx.draw(G, pos, with_labels=True)  # Рисуем граф с названиями узлов
            plt.savefig(f'{user_id}.png')
            plt.close()

            photo = open(f"{user_id}.png", 'rb')
            response = response['choices'][0]['text']
            await msg.delete()

            with open(f'{user_id}.py', 'rb') as info_doc:
                f = info_doc.read()
            await bot.send_document(message.chat.id, f, caption='⬆️Выше вы можете найти код для просмотра изображения без потерь\n\n✅Выполните его в удобной вам среде')

            await bot.send_photo(message.chat.id, photo=photo, caption=f'❗️🗺️ может быть некорректна❗️\n{response}')

        except:
            result = str(response['choices'][0]['text'])
            await msg.delete()
            await bot.send_message(message.chat.id, f'Неудалось составить интелектуальную карту, но я смог разобрать текст на пункты и подпункты!\n\n{result}')

        #УДАЛЕНИЕ ФАЙЛОВ ПОЛЬЗОВАТЕЛЯ, ДЛЯ КОНТРОЛЯ ПАМЯТИ
        os.remove(f'{user_id}.{file}')
        os.remove(f'{user_id}.png')
        os.remove(f'{user_id}.py')
        os.remove('graf.txt')



    #СООБЩЕНИЕ ОБ ОШИБКЕ
    except:
        await msg.delete()
        await bot.send_message(message.chat.id, 'ОЙ что-то пошло не так, попробуйте заново!')
    

    await Form.start.set()


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)