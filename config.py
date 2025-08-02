"""Configuration for memecoin bot"""

# MAIN TOGGLE - SINGLE POINT FOR MODE CONTROL
DEBUG_MODE = False  # True = test/devnet, False = production/mainnet

# USE MEME WALLETS FROM DATABASE
USE_MEME_MINT_DATABASE = True  # True = get mint from DB with meme addresses, False = standard logic

# TEST MODE (direct script execution)
TEST_MODE = False  # True = run script directly, False = through bot

# USE PREDEFINED MINT ADDRESS
USE_PREDEFINED_MINT = False  # True = use pre-generated mint, False = random

# Predefined mint - Base58 encoded seed (32 bytes)
PREDEFINED_MINT_PRIVATE_KEY = "your-predefined-mint-private-key-here"  # Base58 seed

# Test parameters (used when TEST_MODE = True)
TEST_PARAMS = {
    "TOKEN_NAME": "Test Token",
    "TOKEN_SYMBOL": "TEST",
    "TOTAL_SUPPLY": 1000000000,
    "LOGO_URL": "https://example.com/logo.png",
    "TOKEN_DESCRIPTION": "Test Token Description",
    "USER_WALLET": "11111111111111111111111111111111"
}

# Payment settings
AMOUNT = 0.09  # SOL
AMOUNT_TEXT = f"{AMOUNT:.2f} SOL"

# Referral commissions (configurable)
REFERRAL_TOKEN_COMMISSION = 0.10  # 10% of token cost
REFERRAL_CUSTOM_COMMISSION = 0.50  # 50% of custom address cost

# Bonus system for new users
BONUS_CUSTOM_ADDRESSES = 3  # number of free 4-character addresses for all new users

# Supported image formats for IPFS
SUPPORTED_IMAGE_FORMATS = ['png', 'jpg', 'jpeg', 'gif', 'webp', 'svg']

# Custom address prices (in SOL) - progressive scale
CUSTOM_ADDRESS_PRICES = {
    4: 0.03,   # 4 characters = 0.03 SOL
    5: 0.10,   # 5 characters = 0.10 SOL
    6: 0.20,   # 6 characters = 0.20 SOL
    7: 0.35,   # 7 characters = 0.35 SOL
    8: 0.50,   # 8 characters = 0.50 SOL
    9: 0.75,   # 9 characters = 0.75 SOL
    10: 1.00   # 10 characters = 1.00 SOL
}

# Emojis for custom addresses
CUSTOM_ADDRESS_EMOJIS = {
    4: "💎",   # for 4 characters
    5: "💸",   # for 5 characters
    6: "🔥",   # for 6 characters
    7: "⭐",   # for 7 characters
    8: "👑",   # for 8 characters
    9: "🚀",   # for 9 characters
    10: "🏆"   # for 10 characters
}

# Default custom address endings for example
DEFAULT_CUSTOM_ENDINGS = ["Meme", "meme"]

# Text formatting for custom addresses
def get_custom_address_cost_text(total_amount, custom_price):
    """Returns formatted cost text with custom address"""
    return f"Creation cost: *{total_amount:.2f} SOL* ({AMOUNT:.2f} token + {custom_price:.2f} address)"

def get_default_custom_address_text():
    """Returns text with default custom address for example"""
    return f"🎯 Custom address ending: meme"

# Function to format custom address in summary
def format_custom_address_summary(summary, custom_ending=None):
    """Adds custom address information to summary right after Description"""
    if custom_ending:
        custom_text = f"🎯 Custom address ending: *{custom_ending}*"
    else:
        # For default display always show "meme" in lowercase
        custom_text = f"🎯 Custom address ending: *meme*"

    import re

    # Look for Description line and add custom address ending right after it
    # Pattern looks for "Description: something" until end of line
    pattern = r"(Description: [^\n]*)"
    match = re.search(pattern, summary)

    if match:
        # Insert custom address ending right after Description with one newline
        description_end = match.end()
        # Add custom address with one \n after Description and one \n before Creation cost
        result = summary[:description_end] + f"\n{custom_text}" + summary[description_end:]
        return result
    else:
        # If Description not found, add before Creation cost
        cost_pattern = r"(\n\nCreation cost:)"
        cost_match = re.search(cost_pattern, summary)
        if cost_match:
            cost_start = cost_match.start()
            result = summary[:cost_start] + f"\n{custom_text}" + summary[cost_start:]
            return result
        else:
            # Fallback - add at the end
            return f"{summary}\n{custom_text}"

# Bot tokens - REPLACE WITH YOUR OWN
TOKENS = {
    'main_bot': 'your-main-bot-token-here',
    'support_bot': 'your-support-bot-token-here'
}

# Solana network
SOLANA_NETWORK = 'devnet' if DEBUG_MODE else 'mainnet-beta'

# Admin ID - REPLACE WITH YOUR TELEGRAM ID
ADMIN_ID = 123456789

LANGUAGES = {
    'choose_language': 'Welcome to Memecoin Creator bot!',
    'language_selected': 'Language: English',
    'help_text': 'Bot for creating memecoins on Solana blockchain.\n\nCommands:\n'
                 '/start - Start over\n'
                 '/help - Show this help\n'
                 'Support - @your_support_bot',
    'unknown_command': 'Unknown command. Use /start to begin or /help for assistance.',
    'please_wait': 'Please wait. Token creation process is already running and may take some time.',
    'enter_token_name': '🎁 You have been gifted 3 FREE custom 4-character address endings!\n\nEnter your memecoin name (e.g., "Doge Coin"):',
    'enter_token_name_no_bonus': 'Enter your memecoin name (e.g., "Doge Coin"):',
    'invalid_name': 'Name is too long. Max. 32 bytes. Please enter a shorter name:',

    'media_not_allowed': 'Videos, GIFs, documents and other media files (except photos) are not allowed.',
    'media_not_allowed_in_name': 'Videos, GIFs, documents and other media files are not allowed. Enter name again',
    'media_not_allowed_in_symbol': 'Videos, GIFs, documents and other media files are not allowed. Enter symbol again',

    'emoji_not_allowed': 'Emojis and stickers are not allowed.',
    'emoji_not_allowed_in_name': 'Emojis and stickers are not allowed. Enter name again',
    'emoji_not_allowed_in_symbol': 'Emojis and stickers are not allowed. Enter symbol again',
    'enter_token_symbol': 'Enter token symbol (short name, e.g., "DOGE"):',

    'token_params_preparation': 'Preparing parameters for memecoin creation:\n• `{}`\n• `{}`\n• `{}`\n• Logo: {}\n• Your wallet: `{}`\n• Description: `{}`',
    'token_params_preparation_with_custom': 'Preparing parameters for memecoin creation:\n• `{}`\n• `{}`\n• `{}`\n• Logo: {}\n• Your wallet: `{}`\n• Description: `{}`\n🎯 Custom address ending: {}',

    'invalid_symbol': 'Symbol is too long. Max. 10 bytes. Please enter a shorter symbol:',
    'enter_supply': 'Enter total token supply (e.g., 1000000000):',
    'invalid_supply': 'Please enter a valid integer number from 1 to 10,000,000,000:',
    'enter_logo': 'Send photo or image URL (starting with https://):',
    'invalid_url': 'Please enter a valid URL starting with http:// or https://:',
    'invalid_logo_media': 'Videos, GIFs, documents and other media files (except photos) are not supported.\n Please send a photo or enter a valid URL:',
    'invalid_image_format': f'Unsupported image format. Please use one of the supported formats: {", ".join(SUPPORTED_IMAGE_FORMATS).upper()}\n'
                            f'✅But you can screen an image and send like a photo from gallery',
    'checking_image_url': '🔍 Checking image URL...',
    'url_check_failed': 'Unable to verify image URL. Please make sure the link leads to a valid image file.',
    'processing_photo': '📷 Processing photo...',
    'photo_too_large': 'Photo is too large. Maximum size is 4 MB. Please send a smaller photo:',
    'photo_download_error': 'Error downloading photo. Please try again or send a URL:',
    'enter_wallet': 'Enter your Solana wallet address where tokens will be sent:',
    'invalid_wallet': 'Please enter a valid Solana address:',
    'invalid_wallet_length': 'Invalid address length. Solana addresses must be 32-44 characters long:',
    'invalid_wallet_characters': 'Invalid characters detected. Please use only valid base58 characters (no 0, O, I, l):',
    'short_address_warning': '⚠️ Warning: {}-character address is rare for Solana (usually 43-44). Please verify correctness!',
    'invalid_wallet_media': 'Videos, GIFs, documents and other media files are not supported. Please enter a valid Solana address:',
    'confirm': 'Confirm',
    'cancel': 'Cancel',
    'confirm_summary_with_payment': f'Check the information about the token being created:'
                                    f'\n\n🟢 All authorities revoked: update, mint, freeze (immutable)'
                                    f'\n\nName: `{{}}`\nSymbol: `{{}}`\nSupply: `{{}}`\nLogo: {{}}\nYour wallet: `{{}}`'
                                    f'\n\nCreation cost: {AMOUNT:.2f} SOL',

    'confirm_summary_with_description': f'Check the information about the token being created:'
                                        f'\n\n🟢 All authorities revoked: update, mint, freeze (immutable)'
                                        f'\n\nName: `{{}}`\nSymbol: `{{}}`\nSupply: `{{}}`\nLogo: {{}}\nYour wallet: `{{}}`\nDescription: `{{}}`'
                                    f''
                                    f'\n\nCreation cost: {AMOUNT:.2f} SOL',

    'enter_description': 'Enter token description (current: {}).\n\nMax 500 characters:',
    'edit_data_button': '✏️ Edit Data',
    'change_name_button': '📝 Name',
    'change_symbol_button': '🔤 Symbol',
    'change_supply_button': '💰 Supply',
    'change_logo_button': '🖼️ Logo',
    'change_wallet_button': '👤 Wallet',
    'change_description_button': '📄 Description',
    'edit_data_menu': '⚙️ Edit data:',
    'media_not_allowed_in_description': 'Videos, GIFs, documents and other media files are not allowed. Enter description again',
    'empty_description_not_allowed': 'Description cannot be empty. Please enter a description:',
    'description_too_long': 'Description is too long. Max. 500 bytes. Please enter a shorter description:',
    'cancelled': 'Token creation cancelled. Let\'s start over.',
    'payment_instructions': f'To create the token, send {AMOUNT_TEXT} to the address:\n\n{{}}\n\nImportant: transfer must be made from the wallet you specified: {{}}',
    'payment_instructions_with_custom': 'To create the token with address ending {}\n send *{:.2f} SOL* to the address:'
                                        '\n\n{}'
                                        '\n\nImportant: transfer must be made from the wallet you specified: {}',
    'checking_payment': 'Click the button below to check payment status:',
    'token_summary_with_user_tokens': 'Your token has been successfully created!\n\nToken Information:\nName: `{}`\nSymbol: `{}`\nToken Address: `{}`\nTotal Supply: `{}`\nSent to you: `{}`\nDescription: `{}`\nMetadata URI: {}\n\nView token on blockchain:',
    'no_token_info': 'Token created, but failed to get information about it. Please check your wallet.',
    'actions': {
        'create': 'token creation',
        'mint': 'additional token minting',
        'revoke': 'authority revocation',
        'metadata': 'metadata update'
    },
    'running': '{} is in progress...',
    'success': '{} completed successfully!',
    'error': 'Error performing operation: {}',
    'check_payment_button': '🔍 Check transaction',
    'create_again_button': '🚀 Create new coin',
    'animation_symbols': ['🔍 Checking...', '🔎 Checking...', '🔍 Checking...', '🔎 Checking...'],
    'transaction_already_used': '⚠️ This transaction has already been used to create a memecoin!\n\nAmount: {} SOL\nDate: {}\n\nSender: {}\nReceiver: {}\nSignature: {}',
    'transaction_in_process': '⏳ This transaction is already being used to create a memecoin!\n\nAmount: {} SOL\nDate: {}\n\nSender: {}\nReceiver: {}\nSignature: {}\n\nToken creation process is already running. Please wait.',
    'transaction_confirmed_again': '✅ Transaction successfully confirmed again!\n\nAmount: {} SOL\nDate: {}\n\nSender: {}\nReceiver: {}\nSignature: {}',
    'new_transaction_found': '✅ New transaction found!\n\nAmount: {} SOL\nDate: {}\n\nSender: {}\nReceiver: {}\nSignature: {}',
    'transaction_not_found': f'❌ Transaction not found!\n\nPossible reasons:\n• Transaction not yet confirmed\n• Incorrect amount\n• Incorrect addresses\n• Transaction expired (> 30 min)\n\nMake sure you sent {AMOUNT_TEXT} to {{}} from wallet {{}}',
    'transaction_not_found_with_custom': '❌ Transaction not found!\n\nPossible reasons:\n• Transaction not yet confirmed\n• Incorrect amount (expected *{:.2f} SOL*: {:.2f} + {:.2f} for custom address ...{})\n• Incorrect addresses\n• Transaction expired (> 30 min)\n\nMake sure you sent *{:.2f} SOL* to {} from wallet {}',
    'payment_check_error': '❌ Error checking payment: {}. Please try again later.',
    'payment_confirmed_start_creation': '✅ Payment confirmed! Starting token creation...',
    'token_already_created': '⚠️ A memecoin has already been created for this transaction. No new token will be created.',
    'token_params_preparation': 'Preparing parameters for memecoin creation:\n• `{}`\n• `{}`\n• `{}`\n• Logo: {}\n• Your wallet: `{}`\n• Description: `{}`',
    'script_success': '✅ creation script executed successfully!',
    'key_stages': {
        '=== STARTING FULL TOKEN CREATION PROCESS ===': '📄 === STARTING FULL TOKEN CREATION PROCESS ===\nAuthority revocation settings:\n• MINT: {} (creating new tokens)\n• FREEZE: {} (freezing accounts)\n• UPDATE: {} (updating metadata)',
        'Checking user payment': f'🔎 Checking payment of {AMOUNT_TEXT}...',
        'Payment confirmed': f'✅ Payment of {AMOUNT_TEXT} confirmed!',
        'Payment not confirmed': f'❌ Payment not found. Please send {AMOUNT_TEXT} and try again.',
        'Creating token...': '📄 Creating token...',
        'Token created successfully': '📄 Token created successfully',
        'Uploading metadata to IPFS': '📄 Uploading metadata to IPFS...',
        'Metadata uploaded to IPFS': '📄 Metadata successfully uploaded to IPFS',
        'Setting token metadata': '📄 Setting token metadata...',
        'Revoking token authorities': '📄 Revoking token authorities...',
        'Tokens successfully minted': '📄 Tokens successfully minted',
        'tokens successfully sent to user': '✅ Tokens successfully sent to your wallet!',
        'creation script executed successfully': '✅ creation script executed successfully!'
    },

    # Custom address texts
    'buy_custom_address': '🎯 Buy custom address',
    'available_custom_addresses': '🎯 Available custom address endings (e.g. 7x8y...*meme*):',
    'custom_address_selected': '✅ Custom address selected: ...{}',
    'total_cost_with_custom': 'Total cost: {} SOL ({} + {} for custom address)',
    'no_custom_addresses': '❌ No custom addresses available at the moment.',
    'back_to_confirmation': '⬅️ Back to confirmation',
    'custom_address_info': 'Address ending: {} (+{} SOL)',
    'confirm_custom_purchase': 'Confirm purchase of custom address ending ...{} for {} SOL?',
    'custom_address_purchase_cancelled': 'Custom address purchase cancelled.'
}