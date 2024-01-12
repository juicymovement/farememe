# Revised Python Script for Telegram Bot with FreeImage.host API Integration
# c:/Users/name/codefiles/farememe/telegram-env/Scripts/Activate.ps1

import io
import logging
import requests
from openai import OpenAI
from PIL import Image
from telegram.ext import Updater, CommandHandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
import urllib.parse
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Use environment variables
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')

# Set up logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Function to overlay branding on the generated image
def overlay_branding(image_data):
    base_image = Image.open(io.BytesIO(image_data))
    branding_image = Image.open(r'C:\Users\name\Downloads\overlay.png').convert("RGBA")
    base_image.paste(branding_image, (base_image.width - branding_image.width, 0), branding_image)
    final_buffer = io.BytesIO()
    base_image.save(final_buffer, format='PNG')
    final_buffer.seek(0)
    return final_buffer

# Function to send the final image to Telegram chat
def send_image_to_telegram(image_buffer, chat_id, bot):
    bot.send_photo(chat_id, photo=image_buffer)
    
    tweet_text = urllib.parse.quote("Check out this meme! [Attach Image] #YourHashtag")
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("Create Tweet", url=f"https://twitter.com/intent/tweet?text={tweet_text}")]
    ])
    bot.send_message(chat_id, "Click the button below to create a tweet with your meme:", reply_markup=keyboard)

# Function to generate an image using DALL·E
def generate_image_with_dalle(prompt):
    client = OpenAI(api_key=OPENAI_API_KEY)  # Replace with your OpenAI API key
    try:
        response = client.images.generate(model="dall-e-3", prompt=prompt, size="1024x1024", quality="standard", n=1)
        image_url = response.data[0].url
        image_response = requests.get(image_url)
        if image_response.status_code == 200:
            return image_response.content
        else:
            logger.error("Failed to download image from DALL·E")
            return None
    except Exception as e:
        logger.error(f"Error in generating image with DALL·E: {e}")
        return None

# Telegram Bot command handling for /farememe
def farememe(update, context):
    logger.info("Received /farememe command")
    prompt = "extremely high definition, different billionaire megalomaniacs aliens and space marine mobs ransacking a space casino"
    image_data = generate_image_with_dalle(prompt)
    if image_data:
        final_image_buffer = overlay_branding(image_data)
        send_image_to_telegram(final_image_buffer, update.message.chat_id, context.bot)
    else:
        update.message.reply_text("Sorry, I couldn't generate the image.")

# Initialize your Telegram bot
updater = Updater(TELEGRAM_BOT_TOKEN)
dp = updater.dispatcher
dp.add_handler(CommandHandler("farememe", farememe))
updater.start_polling()
updater.idle()
