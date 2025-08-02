"""User input validators for token creation"""
import logging
from utils.handlers import contains_emoji, get_user_info


def validate_media_message(message):
    """Check for media content in message"""
    return any([
        message.video, message.animation, message.document,
        message.sticker, message.voice, message.video_note
    ])


def validate_token_name(text):
    """Token name validation"""
    if not text:
        return False, "empty_text"

    if contains_emoji(text):
        return False, "emoji_not_allowed"

    if len(text.encode('utf-8')) > 32:
        return False, "name_too_long"

    return True, text.strip()


def validate_token_symbol(text):
    """Token symbol validation"""
    if not text:
        return False, "empty_text"

    if contains_emoji(text):
        return False, "emoji_not_allowed"

    symbol = text.strip().upper()
    if len(symbol.encode('utf-8')) > 10:
        return False, "symbol_too_long"

    return True, symbol


def validate_token_supply(text, max_supply):
    """Token supply validation"""
    if not text:
        return False, "empty_text"

    if text == "1 billion":
        return True, 1000000000

    clean_text = text.replace(',', '').replace(' ', '')

    if not clean_text.isdigit():
        return False, "not_a_number"

    supply = int(clean_text)
    if supply <= 0 or supply > max_supply:
        return False, "invalid_range"

    return True, supply


def validate_user_wallet(text):
    """Solana wallet validation"""
    if not text:
        return False, "empty_text"

    wallet = ''.join(text.split())

    if len(wallet) < 32 or len(wallet) > 44:
        return False, "invalid_length"

    base58_chars = set('123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz')

    if not all(char in base58_chars for char in wallet):
        return False, "invalid_characters"

    if len(wallet) < 43:
        return False, "short_address", wallet

    return True, wallet


def validate_token_description(text):
    """Token description validation"""
    if not text:
        return False, "empty_text"

    description = text.strip()
    if len(description.encode('utf-8')) > 500:
        return False, "description_too_long"

    return True, description