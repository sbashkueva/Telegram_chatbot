import telebot
from telebot import types
from bs4 import BeautifulSoup
import requests
import re
from dotenv import load_dotenv
import os

load_dotenv() # hiding telegram token
bot = telebot.TeleBot(os.getenv('TOKEN'));

# Extracting regions with corresponding links to dict
regions = {}
region = 0
districts = {}
url = 'https://www.surf-forecast.com/countries/Indonesia/breaks'
r = requests.get(url)
soup = BeautifulSoup(r.text, "html.parser")
data_regions = soup.findAll(href=re.compile("regions")) # with BS region objects are found by attribute href
# For a list of regions find url for each region and add it to the dict
for i in data_regions:
    region = re.findall(r'/\w+/.+">(\w+[^<]*)', str(i)) # name of the region with regular expression
    link_region = re.findall(r'(/\w+/.+)">', str(i)) # region's url with regular expression
    regions[region[0]] = link_region[0]


# 1st step: if user enters /start, they're offered to choose region with a keyboard
@bot.message_handler(content_types=['text'])
def start(message):
    if message.text == '/start':
        keyboard = types.InlineKeyboardMarkup()
        for k in regions.keys():
            key = types.InlineKeyboardButton(text=k, callback_data=k);
            keyboard.add(key);
        bot.send_message(message.from_user.id,
                         "Please select the region of Indonesia you are interested in:",
                         reply_markup=keyboard);
    else:
        bot.send_message(message.from_user.id, 'Press /start');


# 2nd step: with the chosen region's url corresponding districts are found
# User is offered to choose a district with a keyboard
@bot.callback_query_handler(func=lambda call: True)
def callback_worker(call):
    if call.data in regions.keys():
        districts.clear()
        global region
        region = call.data
        url = 'https://www.surf-forecast.com' + regions[call.data]
        r = requests.get(url)
        soup = BeautifulSoup(r.text, "html.parser")
        data_districts = soup.findAll('div', class_='break-name')  # with BS district objects are found by class
        for i in data_districts:
            district = re.findall(r'/\w+/.+">(\w+[^<]*)', str(i))  # name of the district with regular expression
            link_district = re.findall(r'(/\w+/.+)">', str(i))  # district's url with regular expression
            districts[district[0]] = link_district[0]  # all districts with their url --> to the dict
        keyboard = types.InlineKeyboardMarkup(row_width=2)
        for k in districts.keys():
            key = types.InlineKeyboardButton(text=k, callback_data=k);
            keyboard.add(key);
        bot.send_message(call.from_user.id,
                         f'Please select the district of *{region}* you are interested in:',
                         reply_markup=keyboard, parse_mode='Markdown');

    # Answer with temperature and wave height and period in a table
    elif call.data in districts.keys():
        url1 = 'https://www.surf-forecast.com' + districts[call.data] + '/forecasts/latest'
        url2 = 'https://www.surf-forecast.com/' + districts[call.data]
        r1 = requests.get(url1)
        r2 = requests.get(url2)
        soup1 = BeautifulSoup(r1.text, "html.parser")
        soup2 = BeautifulSoup(r2.text, "html.parser")

        # Extracting sea temperature with BS
        temperature = soup1.find(class_='break-header__temperature break-header__temperature--tablet').b.text
        # Extracting wave height with BS and regular expression
        table_height = soup2.findAll('div',
                                     class_='swell-icon')
        wave_height = []
        for i in table_height:
            wave = re.findall(r'data-height="(\d.\d)"', str(i))
            wave_height.append(str(wave[0] + 'm'))
        # Extracting wave period with BS and regular expression
        table_period = soup2.findAll('tr', class_='lar')
        wave_period = re.findall(r'([0-9]+)\n', str(table_period))

        # Formatting answer into a table
        time = ['11 AM', '2 PM', '5 PM', '8 PM']
        header = 'Time      |Wave Height |Wave Period'
        text = ''
        for i in range(4):
            text += f'{time[i]:10s}|{wave_height[i]:12s}|{wave_period[i]}s\n'
        bot.send_message(call.from_user.id,
                         f'{temperature} \U0001F30A\n\n```\n{header}\n{text}\n```',
                         parse_mode='Markdown');

    # If district from another region (previous request) was chosen, then ask user once again
    elif call.data not in districts.keys() and districts != {}:
        bot.send_message(call.from_user.id,
                         f'You need to select the district of *{region}*. To select a new region press /start.',
                         parse_mode='Markdown')

# Start bot
bot.polling(none_stop=True, interval=0)