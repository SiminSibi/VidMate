import os
import yt_dlp
import instaloader
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, CallbackQueryHandler

# Function to download video from YouTube
def download_youtube_video(url: str, quality: str):
    ydl_opts = {
        'outtmpl': 'downloads/%(title)s.%(ext)s',  # Save video in 'downloads' folder
        'format': quality,  # Download with selected quality
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(url, download=True)
        video_file = ydl.prepare_filename(info_dict)
    return video_file

# Function to download video from Instagram
def download_instagram_video(url: str):
    loader = instaloader.Instaloader()
    loader.download_post(instaloader.Post.from_url(url), target='downloads')
    # Video will be saved in 'downloads' folder
    return 'downloads/'  # Here you need to specify the exact downloaded file

# Function to handle quality selection for downloading
def quality_selection(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    quality = query.data
    url = context.user_data.get('video_url')

    try:
        video_file = download_youtube_video(url, quality)
        query.message.reply_document(document=open(video_file, 'rb'))
        os.remove(video_file)  # Delete the video after sending
    except Exception as e:
        query.message.reply_text(f"Error downloading video: {str(e)}")

# Function to ask for download quality after previewing video
def ask_download_quality(update: Update, context: CallbackContext):
    keyboard = [
        [InlineKeyboardButton("Best Quality", callback_data='best')],
        [InlineKeyboardButton("High Quality", callback_data='22')],
        [InlineKeyboardButton("Low Quality", callback_data='18')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text("Do you want to download the video? Please select the quality:", reply_markup=reply_markup)

# Function to handle incoming messages and process URLs
def handle_message(update: Update, context: CallbackContext):
    text = update.message.text
    chat_id = update.message.chat_id

    if 'youtube.com' in text or 'youtu.be' in text:
        context.user_data['video_url'] = text
        try:
            video_file = download_youtube_video(text, 'best')
            update.message.reply_video(video=open(video_file, 'rb'))
            os.remove(video_file)  # Delete the video after sending
            ask_download_quality(update, context)
        except Exception as e:
            update.message.reply_text(f"Error processing YouTube video: {str(e)}")
    elif 'instagram.com' in text:
        try:
            video_file = download_instagram_video(text)
            update.message.reply_text("Instagram video has been downloaded! Further processing is needed to display it.")
        except Exception as e:
            update.message.reply_text(f"Error downloading video from Instagram: {str(e)}")
    else:
        update.message.reply_text("Please send a YouTube or Instagram video link.")

# Function to send a welcome message when the bot is started
def start(update: Update, context: CallbackContext):
    update.message.reply_text('Welcome! 🎉 Send me a YouTube or Instagram video link to download.')

# Function to show help message
def help_command(update: Update, context: CallbackContext):
    update.message.reply_text('Here is the list of commands:\n'
                              '/start - Start the bot and receive instructions\n'
                              'Send a YouTube video link - Download and send the video from YouTube\n'
                              'Send an Instagram video link - Download and send the video from Instagram\n'
                              'For any issues, send the video link again.')

# Function to display developer information
def developer_command(update: Update, context: CallbackContext):
    update.message.reply_text(
        "This bot is developed by SIMIN. ✨\n\n"
        "Welcome to a world of automation and creativity! 🌟 Feel free to explore and enjoy. 😊"
    )

# Main function to set up and run the bot
def main():
    # Your bot's token
    token = '7967739908:AAGxG9LRU9nFxDjqUS3TGfc33ji4-FKDz_s'
    
    # Set up the Updater and Dispatcher
    updater = Updater(token, use_context=True)
    dispatcher = updater.dispatcher

    # Add handlers for commands and messages
    dispatcher.add_handler(CommandHandler('start', start))
    dispatcher.add_handler(CommandHandler('help', help_command))
    dispatcher.add_handler(CommandHandler('developer', developer_command))
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))
    dispatcher.add_handler(CallbackQueryHandler(quality_selection))
    
    # Start polling for updates
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
