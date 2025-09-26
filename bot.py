import os
from dotenv import load_dotenv
import telebot
from stegano import lsb
import io
import tempfile


from ciphers.ciphers import *
from ciphers.hashing import get_str_hash, get_file_hash

# Load environment variables from .env file
load_dotenv()
# Get token from environment variable
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
if not TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN not found in environment variables")


bot = telebot.TeleBot(TOKEN)


@bot.message_handler(commands=["help"])
def help_command(message):
    help_text = """🤖 <b>Bot Help - Available Commands</b>

    <b>🔐 HASH COMMANDS</b>
    • <code>/hash &lt;text&gt;</code> - Generate multiple hashes for text
    Example: <code>/hash hello world</code>

    <b>📎 FILE HASHING</b>
    • Upload any file to generate hashes
    • <b>Maximum file size: 20MB</b>
    • Supported: documents, images, videos, audio

    <b>🔒 CIPHER COMMANDS</b>
    • <code>/cipher &lt;algorithm&gt; &lt;text&gt;</code> - Encrypt text
    • <code>/encrypt &lt;algorithm&gt; &lt;text&gt;</code> - Same as cipher
    • <code>/decipher &lt;algorithm&gt; &lt;text&gt;</code> - Decrypt text  
    • <code>/decrypt &lt;algorithm&gt; &lt;text&gt;</code> - Same as decipher

    <b>📋 AVAILABLE ALGORITHMS</b>
    • <code>atbash</code> - Simple letter reversal cipher
    • <code>caesar</code> - Classic Caesar shift cipher
    • <code>simple_substitution</code> - Basic substitution cipher
    • <code>baconian</code> - Bacon's cipher encoding
    • <code>rot13</code> - ROT13 rotation cipher
    • <code>shift</code> - Custom shift cipher
    • <code>mixed_alphabet</code> - Requires keyword

    <b>💡 EXAMPLES</b>
    <code>/hash secret message</code>
    <code>/cipher atbash hello world</code>
    <code>/encrypt mixed_alphabet mykey secret text</code>
    <code>/decrypt caesar encrypted text</code>

    <b>ℹ️ OTHER COMMANDS</b>
    • <code>/start</code> - Start the bot
    • <code>/help</code> - Show this help message

    <b>🔧 SPECIAL NOTES</b>
    • Mixed alphabet cipher requires a keyword
    • All operations support both encryption and decryption
    • Hash command generates 12 different hash types"""

    bot.reply_to(message, help_text, parse_mode="HTML")


@bot.message_handler(commands=["start"])
def start_command(message):
    bot.send_message(
        message.chat.id,
        "* Bot started successfully! *\n`/help` to get help",
        parse_mode="Markdown",
    )


@bot.message_handler(commands=["hash"])
def hash_command(message):
    text = message.text.split()[1:]
    text = "".join(text)

    # Check if arguments are provided FIRST
    if not text:
        bot.reply_to(message, "❌ Please provide text to hash!\nExample: /hash example")
        return

    result = get_str_hash(text)

    # Create formatted response
    response = f"🔐 **Hash results for:** `{text}`\n\n"

    for hash_algo, value in result.items():
        response += f"*{hash_algo.upper()}* : `{value}`\n\n"

    bot.reply_to(message, response, parse_mode="Markdown")


@bot.message_handler(content_types=["photo", "document", "video", "audio"])
def file_hash_command(message):
    """Handle uploaded files and generate hashes"""
    try:
        # Get file info
        if message.document:
            file_info = bot.get_file(message.document.file_id)
            file_name = message.document.file_name or "unknown_file"
        elif message.photo:
            file_info = bot.get_file(message.photo[-1].file_id)
            file_name = "photo.jpg"
        elif message.video:
            file_info = bot.get_file(message.video.file_id)
            file_name = message.video.file_name or "video.mp4"
        elif message.audio:
            file_info = bot.get_file(message.audio.file_id)
            file_name = message.audio.file_name or "audio.mp3"
        else:
            bot.reply_to(message, "❌ Unsupported file type")
            return

        # Send processing message
        processing_msg = bot.reply_to(message, "⏳ Processing file... Please wait.")
        # Download file
        downloaded_file = bot.download_file(file_info.file_path)

        # Create temporary file
        with tempfile.NamedTemporaryFile() as temp_file:
            temp_file.write(downloaded_file)
            temp_file.seek(0)

            # Generate hashes
            hashes = get_file_hash(temp_file)

        # Format response
        response = f"📎 <b>File Hash Results</b>\n\n"
        response += f"<b>File:</b> <code>{file_name}</code>\n"

        for algo, hash_value in hashes.items():
            response += f"<b>{algo.upper()}:</b>\n<code>{hash_value}</code>\n\n"

        # Delete processing message and send result
        bot.delete_message(message.chat.id, processing_msg.message_id)
        bot.reply_to(message, response, parse_mode="HTML")

    except Exception as e:
        bot.reply_to(message, f"❌ Error processing file: {str(e)}")


@bot.message_handler(content_types=["photo"])
def handle_photo_without_command(message):
    """Handle photos sent without steganography command"""
    bot.reply_to(message, 
        "📸 **Photo received!**\n\n"
        "💡 **For steganography operations:**\n"
        "• Send photo with caption: `/stegano cipher keyword secret message`\n"
        "• Or: `/stegano decipher` to reveal hidden message\n\n"
        "ℹ️ Use `/help` for other commands", 
        parse_mode="Markdown")

@bot.message_handler(commands=["stegano", "steganography"])
def stegano_command_only(message):
    """Handle steganography commands without photo"""
    help_text = """🔐 **Steganography Help**

**Hide message in image:**
1. Send photo with caption: `/stegano cipher keyword your_secret_message`

**Reveal hidden message:**
1. Send photo with caption: `/stegano decipher keyword`

**Example:**
📸 Send photo + `/stegano cipher mykey Hello World!`
📸 Send encoded photo + `/stegano decipher mykey`

⚠️ **Note:** Both operations require sending a photo!"""
    
    bot.reply_to(message, help_text, parse_mode="Markdown")

@bot.message_handler(content_types=["photo"])
def handle_photo_with_caption(message):
    """Handle photos with captions that might contain steganography commands"""
    if not message.caption:
        return  # Let the other handler deal with it
    
    caption = message.caption.strip()
    if not caption.startswith('/stegano') and not caption.startswith('/steganography'):
        return  # Not a steganography command
    
    try:
        # Parse the caption command
        args = caption.split()
        if len(args) < 2:
            bot.reply_to(message, 
                "❌ **Invalid command format**\n\n"
                "**Usage:**\n"
                "• `/stegano cipher keyword secret_message`\n"
                "• `/stegano decipher keyword`", 
                parse_mode="Markdown")
            return

        operation = args[1].lower()  # 'cipher' or 'decipher'
        
        if operation not in ['cipher', 'decipher']:
            bot.reply_to(message, 
                "❌ **Invalid operation!**\n\n"
                "Use `cipher` to hide or `decipher` to reveal", 
                parse_mode="Markdown")
            return

        # Get the largest photo (highest resolution)
        file_info = bot.get_file(message.photo[-1].file_id)
        downloaded_file = bot.download_file(file_info.file_path)

        # Processing message
        processing_msg = bot.reply_to(message, "⏳ Processing steganography operation...")

        if operation == "cipher":
            # Hide message
            if len(args) < 4:
                bot.edit_message_text(
                    "❌ **Missing arguments for cipher operation**\n\n"
                    "**Usage:** `/stegano cipher keyword secret_message`",
                    message.chat.id, processing_msg.message_id, parse_mode="Markdown")
                return

            keyword = args[2]
            secret_message = " ".join(args[3:])  # Join all remaining words
            
            # Create cipher object
            mix = MixedAlphabet(keyword)
            encrypted_message = mix.cipher(secret_message)

            # Create temporary file for input image
            with tempfile.NamedTemporaryFile(suffix='.png') as temp_file:
                temp_file.write(downloaded_file)
                temp_file.flush()  # Ensure data is written
                
                # Hide the encrypted message in the image
                secret_image = lsb.hide(temp_file.name, encrypted_message)
                
                # Create output buffer
                output_buffer = io.BytesIO()
                secret_image.save(output_buffer, format='PNG')
                output_buffer.seek(0)  # Reset to beginning
                
                # Send the steganographed image
                bot.delete_message(message.chat.id, processing_msg.message_id)
                bot.send_document(
                    message.chat.id,
                    output_buffer,
                    visible_file_name="steganographed_image.png",
                    caption=f"🔐 **Message hidden successfully!**\n\n"
                           f"🔑 **Keyword:** `{keyword}`\n"
                           f"📝 **Original message:** `{secret_message}`\n"
                           f"🔒 **Encrypted message:** `{encrypted_message}`\n\n"
                           f"💡 **To reveal:** Send this image with `/stegano decipher {keyword}`",
                    parse_mode="Markdown"
                )

        elif operation == "decipher":
            # Reveal message
            if len(args) < 3:
                bot.edit_message_text(
                    "❌ **Missing keyword for decipher operation**\n\n"
                    "**Usage:** `/stegano decipher keyword`",
                    message.chat.id, processing_msg.message_id, parse_mode="Markdown")
                return

            keyword = args[2]
            
            # Create cipher object
            mix = MixedAlphabet(keyword)

            # Create temporary file for processing
            with tempfile.NamedTemporaryFile(suffix='.png') as temp_file:
                temp_file.write(downloaded_file)
                temp_file.flush()
                
                try:
                    # Reveal the hidden encrypted message
                    encrypted_message = lsb.reveal(temp_file.name)
                    
                    if not encrypted_message:
                        bot.edit_message_text(
                            "❌ **No hidden message found!**\n\n"
                            "This image doesn't contain steganographic data or "
                            "was processed with different settings.",
                            message.chat.id, processing_msg.message_id)
                        return
                    
                    # Decrypt the message
                    decrypted_message = mix.decipher(encrypted_message)
                    
                    # Send results
                    bot.edit_message_text(
                        f"🔓 **Message revealed successfully!**\n\n"
                        f"🔑 **Keyword:** `{keyword}`\n"
                        f"🔒 **Encrypted:** `{encrypted_message}`\n"
                        f"📝 **Decrypted:** `{decrypted_message}`",
                        message.chat.id, processing_msg.message_id, parse_mode="Markdown")
                    
                except Exception as e:
                    bot.edit_message_text(
                        f"❌ **Error revealing message:**\n\n"
                        f"• No hidden message found, or\n"
                        f"• Wrong keyword used, or\n"
                        f"• Image wasn't processed with steganography\n\n"
                        f"**Error details:** `{str(e)}`",
                        message.chat.id, processing_msg.message_id, parse_mode="Markdown")

    except Exception as e:
        bot.reply_to(message, f"❌ **Steganography error:** {str(e)}")

@bot.message_handler(commands=["cipher", "decipher", "encrypt", "decrypt"])
def cipher_command(message):
    args = message.text.split()

    # Extract operation
    op = args[0][1:].lower()

    if len(args) < 3:
        help_text = """❌ Usage: /{operation} <algorithm> [keyword] <text>

        *Operations:* cipher, decipher, encrypt, decrypt
        *Algorithms:* atbash, caesar, simple_substitution, baconian, rot13, shift, mixed_alphabet

        *Examples:*
        • /cipher atbash hello world
        • /encrypt mixed_alphabet secret hello world
        • /decrypt caesar hello world"""
        bot.reply_to(message, help_text)
        return

    algo = args[1].lower()

    cipher_classes = {
        "atbash": Atbash,
        "caesar": Caesar,
        "simple_substitution": SimpleSubstitution,
        "baconian": Baconian,
        "rot13": Rot13,
        "shift": Shift,
        "mixed_alphabet": MixedAlphabet,
    }

    cipher_class = cipher_classes.get(algo)

    if not cipher_class:
        available = ", ".join(cipher_classes.keys())
        result = f"❌ Algorithm '{algo}' not supported\nAvailable: {available}"
        bot.reply_to(message, result)
        return

    try:
        # Handle special cases that require parameters
        if algo == "mixed_alphabet":
            if len(args) < 4:
                bot.reply_to(
                    message,
                    f"❌ Mixed alphabet requires keyword!\nUsage: /{op} mixed_alphabet <keyword> <text>",
                )
                return

            keyword = args[2]
            text = " ".join(args[3:])
            cipher_instance = cipher_class(keyword)

        else:
            text = " ".join(args[2:])
            cipher_instance = cipher_class()

        if not text.strip():
            bot.reply_to(message, "❌ Please provide text to process!")
            return

        # Call the correct method based on operation
        if op in ["cipher", "encrypt"]:
            result = cipher_instance.cipher(text=text)
        elif op in ["decipher", "decrypt"]:
            result = cipher_instance.decipher(text=text)
        else:
            result = "❌ Invalid operation. Use: cipher, decipher, encrypt, or decrypt"

        # Format response
        response = f"🔐 <b>Algorithm:</b> {algo.upper()}\n"
        response += f"<b>Operation:</b> {op.upper()}\n"
        if algo == "mixed_alphabet":
            response += f"<b>Keyword:</b> <code>{keyword}</code>\n"
        response += f"<b>Input:</b> <code>{text}</code>\n"
        response += f"<b>Output:</b> <code>{result}</code>"

        bot.reply_to(message, response, parse_mode="HTML")

    except Exception as e:
        result = f"❌ Error during {op}: {str(e)}"
        bot.reply_to(message, result)


bot.infinity_polling()
