# Description
Surf Forecast bot on Telegram allows to check today's weather for surfing at different regions and districts of Indonesia.
I used Beautiful Soup library and regular expressions for parsing regions and districts from website: https://www.surf-forecast.com/countries/Indonesia/breaks

User chooses a spot with two steps using keyboard: types.InlineKeyboardMarkup().

The answer shows detailed hourly weather forecast including wave height, wave period and today average sea temperature at the spot.

# Link on Telegram
Link to the bot: https://t.me/surf_forecast_bot

# Used libraries
* telebot
* bs4
* requests
* re
* dotenv
* os
