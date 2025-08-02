"""FSM handlers for token image processing"""
import os
from aiogram import types
from aiogram.fsm.context import FSMContext
from utils.handlers import get_user_info, log_user_action, get_text
from utils.image_security import (
    check_telegram_photo_security, check_url_image_security,
    is_valid_image_format, verify_image_url
)


async def download_telegram_photo(message, bot):
    """Download photo from Telegram"""
    try:
        file_info = await bot.get_file(message.photo[-1].file_id)

        if file_info.file_size > 4 * 1024 * 1024:
            return None, "file_too_large"

        temp_dir = 'temp_images'
        os.makedirs(temp_dir, exist_ok=True)

        file_path = file_info.file_path
        extension = file_path.split('.')[-1] if '.' in file_path else 'jpg'
        local_filename = f"temp_images/tg_photo_{message.from_user.id}_{message.message_id}.{extension}"

        await bot.download_file(file_info.file_path, local_filename)
        return local_filename, "success"
    except Exception as e:
        print(f"Error downloading photo: {e}")
        return None, "download_error"


async def process_token_logo(message: types.Message, state: FSMContext):
    """Token logo URL or photo input handler"""
    from bot import BotStates, bot

    user_data = await state.get_data()

    if any([message.video, message.animation, message.document, message.sticker, message.voice, message.video_note]):
        await message.answer(await get_text('invalid_logo_media', user_data))
        return

    if message.photo:
        checking_msg = await message.answer(await get_text('processing_photo', user_data))

        local_file, status = await download_telegram_photo(message, bot)
        await checking_msg.delete()

        if status == "file_too_large":
            await message.answer(await get_text('photo_too_large', user_data))
            return
        elif status != "success" or not local_file:
            await message.answer(await get_text('photo_download_error', user_data))
            return

        security_msg = await message.answer("🔍 Checking image security...")
        is_safe, security_result = await check_telegram_photo_security(local_file)
        await security_msg.delete()

        if not is_safe:
            if os.path.exists(local_file):
                os.remove(local_file)
            await message.answer(security_result)
            return

        log_user_action(message.from_user, "uploaded photo for logo")
        await state.update_data(
            token_logo=local_file,
            logo_type='file',
            photo_file_id=message.photo[-1].file_id
        )

        user_data = await state.get_data()
        required_fields = ['token_name', 'token_symbol', 'token_supply', 'user_wallet', 'token_description']
        has_all_fields = all(field in user_data for field in required_fields)

        if has_all_fields:
            from utils.edit_handlers import show_confirmation_after_edit
            await show_confirmation_after_edit(message, state, user_data)
            user_info = user_data.get('user_info', get_user_info(message.from_user))
            print(f"{user_info} photo logo changed during editing, returning to confirmation")
        else:
            await message.answer(await get_text('enter_wallet', user_data))
            await state.set_state(BotStates.user_wallet)
        return

    if not message.text:
        await message.answer(await get_text('invalid_url', user_data))
        return

    url = message.text.strip()

    is_safe, security_result = await check_url_image_security(url)
    if not is_safe:
        await message.answer(security_result)
        return

    if security_result != url:
        direct_url_msg = (f"✅ Found direct image link:\n{security_result}\n\n"
                         f"💡 Tip: For faster processing, you can use direct image links like this instead of Google Images links.")
        await message.answer(direct_url_msg)
        url = security_result

    if not is_valid_image_format(url):
        checking_msg = await message.answer(await get_text('checking_image_url', user_data))
        http_check = await verify_image_url(url)
        await checking_msg.delete()

        if http_check is False:
            await message.answer(await get_text('invalid_image_format', user_data))
            return
        elif http_check is None:
            await message.answer(await get_text('url_check_failed', user_data))
            return

    log_user_action(message.from_user, f"entered logo URL: {url}")
    await state.update_data(token_logo=url, logo_type='url')

    user_data = await state.get_data()
    required_fields = ['token_name', 'token_symbol', 'token_supply', 'user_wallet', 'token_description']
    has_all_fields = all(field in user_data for field in required_fields)

    if has_all_fields:
        from utils.edit_handlers import show_confirmation_after_edit
        await show_confirmation_after_edit(message, state, user_data)
        user_info = user_data.get('user_info', get_user_info(message.from_user))
        print(f"{user_info} URL logo changed during editing, returning to confirmation")
    else:
        await message.answer(await get_text('enter_wallet', user_data))
        await state.set_state(BotStates.user_wallet)