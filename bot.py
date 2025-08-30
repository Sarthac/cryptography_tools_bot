import os
from dotenv import load_dotenv
import telebot

from ciphers.ciphers import *
from ciphers.hashing import get_str_hash

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
