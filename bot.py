import logging, os, re
from aiogram import Bot, Dispatcher, types, F
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters import Command
from config import LANGUAGES, TOKENS, AMOUNT
from utils.telegram_formatter import TelegramFormatter

logging.basicConfig(level=logging.INFO)
bot = Bot(token=TOKENS['main_bot'])
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

MAX_SUPPLY = 10000000000


class BotStates(StatesGroup):
    token_name = State()
    token_symbol = State()
    token_supply = State()
    token_logo = State()
    user_wallet = State()
    token_description = State()
    confirm_create = State()
    waiting_payment = State()
    creating_token = State()
    choosing_custom_address = State()
    confirm_custom_address = State()
    uploading_wallets = State()


@dp.message(Command("user_stats"))
async def cmd_user_stats(message: types.Message):
    """Admin command for viewing specific user statistics"""
    from config import ADMIN_ID
    from referrals.middleware import call_referral_db_safe

    if message.from_user.id != ADMIN_ID:
        await message.answer("❌ Access denied")
        return

    try:
        args = message.text.split()
        if len(args) != 2:
            await message.answer("Usage: /user_stats <user_id>")
            return

        user_id = int(args[1])
    except ValueError:
        await message.answer("❌ Invalid user_id format")
        return

    try:
        stats = await call_referral_db_safe('getUserStatsWithConnect', user_id)

        if not stats:
            await message.answer(f"❌ No data found for user {user_id}")
            return

        user_info = stats.get('userInfo')
        payments = stats.get('payments', [])

        text = f"👤 **User {user_id} Stats:**\n\n"

        if user_info:
            text += f"💰 **Total Earned Tokens:** {user_info.get('total_earned_tokens', 0):.6f} SOL\n"
            text += f"🎯 **Total Earned Custom:** {user_info.get('total_earned_custom', 0):.6f} SOL\n"
            text += f"👥 **Total Referrals:** {user_info.get('total_referrals', 0)}\n"
            text += f"💳 **Wallet:** `{user_info.get('wallet_address', 'Not set')}`\n\n"

        text += f"📋 **Payments ({len(payments)}):**\n"

        for payment in payments[:5]:
            amount = payment.get('amount', 0)
            p_type = payment.get('payment_type', 'unknown')
            tx_hash = payment.get('tx_hash', 'No hash')[:8] + '...'
            text += f"• {amount:.6f} SOL ({p_type}) - {tx_hash}\n"

        if len(payments) > 5:
            text += f"... and {len(payments) - 5} more\n"

        await message.answer(text, parse_mode="Markdown")

    except Exception as e:
        await message.answer(f"❌ Error: {str(e)}")


async def start_token_creation(message, state, user_data, tx_info):
    """Start token creation process"""
    from utils.js_manager import run_scripts_async, get_token_info, find_project_files
    from utils.payment_checker import save_transaction, mark_transaction_in_process
    from utils.handlers import get_create_again_keyboard, get_text, cleanup_user_files, save_memecoin_data, \
        update_memecoin_data
    from utils.wallet_protection import release_user_wallet

    user_info = user_data.get('user_info', '[unknown_user]')
    tx_signature = tx_info.get("signature")

    logging.info(f"{user_info} starting token creation for transaction {tx_signature[:8]}...")

    if tx_info.get("token_created", False):
        logging.info(f"{user_info} token already created for this transaction")
        await message.answer(LANGUAGES['token_already_created'])
        await state.set_state(BotStates.token_name)
        mark_transaction_in_process(tx_signature, False)
        await cleanup_user_files(user_data)
        if hasattr(message, 'from_user'):
            release_user_wallet(user_data, message.from_user.id)
            logging.info(f"🚫 {user_info} wallet released - token already created")
        return

    if not tx_info.get("in_process", False):
        mark_transaction_in_process(tx_signature)

    save_memecoin_data(user_data, tx_signature)

    try:
        logo_source = user_data['token_logo']
        if user_data.get('logo_type') == 'file':
            logo_source = os.path.abspath(logo_source)

        token_params = {
            'TOKEN_NAME': user_data['token_name'],
            'TOKEN_SYMBOL': user_data['token_symbol'],
            'TOTAL_SUPPLY': user_data['token_supply'],
            'LOGO_URL': logo_source,
            'USER_WALLET': user_data['user_wallet'],
            'TOKEN_DESCRIPTION': user_data.get('token_description', f"{user_data['token_name']} Meme Coin")
        }

        if user_data.get('custom_ending'):
            token_params['CUSTOM_ENDING'] = user_data['custom_ending']
            logging.info(f"{user_info} using custom ending: {user_data['custom_ending']}")

        logging.info(
            f"{user_info} token parameters: {user_data['token_name']} ({user_data['token_symbol']}) - {user_data['token_supply']}")

        if user_data.get('custom_ending'):
            custom_ending = user_data.get('custom_ending')
            params_text = LANGUAGES['token_params_preparation_with_custom'].format(
                user_data['token_name'],
                user_data['token_symbol'],
                user_data['token_supply'],
                "📷 Uploaded photo",
                user_data['user_wallet'],
                user_data.get('token_description', f"{user_data['token_name']} Meme Coin"),
                custom_ending
            )
        else:
            params_text = LANGUAGES['token_params_preparation'].format(
                user_data['token_name'],
                user_data['token_symbol'],
                user_data['token_supply'],
                "📷 Uploaded photo",
                user_data['user_wallet'],
                user_data.get('token_description', f"{user_data['token_name']} Meme Coin")
            )

        if user_data.get('logo_type') == 'file' and user_data.get('photo_file_id'):
            await message.answer_photo(
                photo=user_data['photo_file_id'],
                caption=TelegramFormatter.escape_text(params_text),
                parse_mode="MarkdownV2"
            )
        else:
            params_text = params_text.replace("📷 Uploaded photo", user_data['token_logo'])
            await message.answer(
                TelegramFormatter.escape_text(params_text),
                parse_mode="MarkdownV2"
            )

        config_path, _, _ = find_project_files()
        revoke_authorities = {"MINT": True, "FREEZE": True, "UPDATE": True}

        if config_path and os.path.exists(config_path):
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    config_content = f.read()
                    revoke_match = re.search(r'const REVOKE_AUTHORITIES = {([^}]+)};', config_content, re.DOTALL)
                    if revoke_match:
                        auth_block = revoke_match.group(1)
                        for auth in ["MINT", "FREEZE", "UPDATE"]:
                            if re.search(rf'{auth}:\s*(\w+)', auth_block):
                                value_match = re.search(rf'{auth}:\s*(\w+)', auth_block)
                                revoke_authorities[auth] = value_match.group(1).lower() == 'true'
            except Exception as e:
                logging.info(f"Error reading authority settings: {e}")

        async def log_callback(log_message):
            print(f"📝 JS LOG: {log_message}")
            for key, output in LANGUAGES['key_stages'].items():
                if key in log_message:
                    if key == "=== STARTING FULL TOKEN CREATION PROCESS ===":
                        logging.info(f"{user_info} starting full token creation process")
                        formatted_output = output.format(
                            'Yes' if revoke_authorities['MINT'] else 'No',
                            'Yes' if revoke_authorities['FREEZE'] else 'No',
                            'Yes' if revoke_authorities['UPDATE'] else 'No'
                        )
                        await message.answer(formatted_output)
                    elif 'creation script executed successfully' in key:
                        logging.info(f"{user_info} creation script executed successfully")
                        await message.answer(LANGUAGES['script_success'])
                    else:
                        stage_name = key.replace('=== ', '').replace(' ===', '')
                        logging.info(f"{user_info} stage: {stage_name}")
                        await message.answer(output)
                    break

        logging.info(f"{user_info} starting token creation script...")
        logging.info(f"🎯 JavaScript parameters: {token_params}")

        create_result = await run_scripts_async(action='create', params=token_params, log_callback=log_callback)

        logging.info(f"🎯 JavaScript execution result: {create_result}")
        logging.info(f"🔍 Checking token-info.json existence...")

        if not create_result:
            logging.error(f"{user_info} ❌ JavaScript returned error code")
            mark_transaction_in_process(tx_signature, False)
            await message.answer(await get_text('error', user_data, 'create'))
            await state.set_state(BotStates.token_name)
            await cleanup_user_files(user_data)
            if hasattr(message, 'from_user'):
                release_user_wallet(user_data, message.from_user.id)
                logging.info(f"❌ {user_info} wallet released due to JavaScript error")
            return

        token_info = get_token_info()
        logging.info(f"🔍 get_token_info() result: {token_info is not None}")

        if token_info:
            logging.info(f"✅ Token info obtained: {token_info.get('name')} ({token_info.get('symbol')})")
        else:
            logging.error(f"❌ token-info.json not found or empty")
            possible_paths = [
                'token-info.json',
                'scripts/token-info.json',
                os.path.join(os.getcwd(), 'token-info.json'),
                os.path.join(os.getcwd(), 'scripts', 'token-info.json')
            ]
            for path in possible_paths:
                if os.path.exists(path):
                    logging.info(f"🔍 Found token-info.json at: {path}")
                    break
            else:
                logging.error("🔍 token-info.json NOT found in any path")

        updated_tx_info = tx_info.copy()
        updated_tx_info["token_created"] = True
        updated_tx_info["in_process"] = False
        save_transaction(updated_tx_info, True)

        logging.info(f"{user_info} token successfully created")
        await message.answer(await get_text('success', user_data, 'create'))

        if hasattr(message, 'from_user'):
            release_user_wallet(user_data, message.from_user.id)
            logging.info(
                f"✅ {user_info} wallet {user_data.get('user_wallet', 'unknown')[:8]}...{user_data.get('user_wallet', 'unknown')[-8:]} released after successful token creation")

        if user_data.get('is_bonus_used') and user_data.get('custom_ending'):
            try:
                from referrals.middleware import call_referral_db_safe

                custom_ending = user_data.get('custom_ending')
                user_info_str = user_data.get('user_info', '')
                user_id_extracted = None

                if user_info_str and user_info_str.startswith('[') and ':' in user_info_str:
                    try:
                        user_id_extracted = int(user_info_str.split('[')[1].split(':')[0])
                        logging.info(f"DEBUG: Extracted user_id from user_info: {user_id_extracted}")
                    except (ValueError, IndexError):
                        logging.error(f"DEBUG: Failed to extract user_id from user_info: {user_info_str}")

                if user_id_extracted:
                    bonus_before = await call_referral_db_safe('getBonusCustomAddressesWithConnect', user_id_extracted)
                    logging.info(f"DEBUG: User {user_id_extracted} has {bonus_before} bonus addresses before deduction")

                    if bonus_before and bonus_before > 0:
                        bonus_used = await call_referral_db_safe('useBonusCustomAddressWithConnect', user_id_extracted)

                        if bonus_used:
                            bonus_after = await call_referral_db_safe('getBonusCustomAddressesWithConnect', user_id_extracted)
                            logging.info(f"✅ {user_info} bonus deducted successfully for ending: {custom_ending}")
                            logging.info(f"DEBUG: Bonus count: {bonus_before} → {bonus_after}")
                        else:
                            logging.warning(f"❌ {user_info} failed to deduct bonus - database operation failed")
                    else:
                        logging.warning(f"❌ {user_info} no bonus available to deduct (count: {bonus_before})")
                else:
                    logging.error(f"❌ {user_info} cannot deduct bonus - user_id not extracted from user_info")

            except Exception as bonus_error:
                logging.error(f"❌ {user_info} error deducting bonus custom address: {bonus_error}")

        try:
            from referrals.manager import process_referral_payment
            from referrals.middleware import ensure_user_cached

            if hasattr(message, 'from_user'):
                await ensure_user_cached(message.from_user)

            referral_result = await process_referral_payment(user_data, tx_info)

            if referral_result.get('success') and referral_result.get('referrer_id'):
                logging.info(
                    f"{user_info} referral payout processed: {referral_result.get('total_commission', 0):.6f} SOL")
            elif referral_result.get('message'):
                logging.info(f"{user_info} referral payout: {referral_result.get('message')}")
        except Exception as referral_error:
            logging.error(f"{user_info} referral payout error: {referral_error}")

        if token_info:
            update_memecoin_data(tx_signature, token_info)

            is_mainnet = "mainnet" in token_info.get('network', '').lower()

            cluster_param_solscan = "" if is_mainnet else "?cluster=devnet"
            solscan_url = f"https://solscan.io/token/{token_info['tokenMint']}{cluster_param_solscan}"

            cluster_param_explorer = "" if is_mainnet else "?cluster=devnet"
            explorer_url = f"https://explorer.solana.com/address/{token_info['tokenMint']}{cluster_param_explorer}"

            user_token_amount = token_info.get('userTokenAmount', token_info['totalSupply'])

            logging.info(f"{user_info} token created - address: {token_info['tokenMint']}")

            token_summary = await get_text('token_summary_with_user_tokens', user_data)
            token_summary = token_summary.format(
                token_info['name'],
                token_info['symbol'],
                token_info['tokenMint'],
                token_info['totalSupply'],
                user_token_amount,
                user_data.get('token_description', f"{user_data['token_name']} Meme Coin"),
                token_info.get('uri', 'N/A'),
                "",
                ""
            )

            escaped_summary = TelegramFormatter.escape_text(token_summary)

            final_message = f"""{escaped_summary}
[Solana Explorer]({explorer_url})
[Solscan]({solscan_url})"""

            await message.answer(
                final_message,
                reply_markup=get_create_again_keyboard(),
                parse_mode="MarkdownV2"
            )
        else:
            logging.info(f"{user_info} token created but failed to get information")
            await message.answer(await get_text('no_token_info', user_data), reply_markup=get_create_again_keyboard())

        await cleanup_user_files(user_data)

    except Exception as e:
        logging.info(f"{user_info} critical error during token creation: {e}")
        mark_transaction_in_process(tx_signature, False)
        await message.answer(f"❌ {LANGUAGES['payment_check_error'].format(str(e))}")
        await cleanup_user_files(user_data)
        if hasattr(message, 'from_user'):
            release_user_wallet(user_data, message.from_user.id)
            logging.info(f"💥 {user_info} wallet released due to critical error: {str(e)[:50]}...")
    finally:
        await state.set_state(BotStates.token_name)


from utils.handlers import cmd_help, process_during_creation, check_payment_button
from utils.state_handlers import (
    cmd_start, create_again, process_token_name, process_token_symbol,
    process_token_supply, process_user_wallet,
    process_confirmation, process_message, process_token_description,
    back_to_edit_from_payment
)
from utils.edit_handlers import (
    edit_data, change_name, change_symbol, change_supply,
    change_logo, change_wallet, change_description, back_to_confirmation_from_edit
)
from utils.custom_address_handlers import (
    buy_custom_address, select_custom_ending, confirm_custom_address,
    back_to_confirmation, cancel_custom_address, bonus_info
)
from utils.image_handlers import process_token_logo
from utils.payment_handler import check_payment

from utils.admin_handlers import cmd_upload_wallets, cmd_db_stats, process_admin_message

from referrals.handlers import (
    cmd_referral, ref_add_wallet, ref_change_wallet, process_wallet_input, ReferralStates
)

dp.message.register(cmd_start, Command("start"))
dp.message.register(cmd_help, Command("help"))
dp.message.register(cmd_referral, Command("referral"))

dp.message.register(cmd_upload_wallets, Command("upload_wallets"))
dp.message.register(cmd_db_stats, Command("db_stats"))


@dp.message(Command("wallet_stats"))
async def cmd_wallet_stats(message: types.Message):
    """Admin command for viewing wallet reservation statistics"""
    from config import ADMIN_ID
    from utils.wallet_protection import get_wallet_reservation_stats

    if message.from_user.id != ADMIN_ID:
        await message.answer("❌ Access denied")
        return

    stats_text = await get_wallet_reservation_stats()
    await message.answer(stats_text, parse_mode="MarkdownV2")


dp.callback_query.register(create_again, lambda c: c.data == "create_again")

dp.callback_query.register(edit_data, lambda c: c.data == "edit_data")
dp.callback_query.register(change_name, lambda c: c.data == "change_name")
dp.callback_query.register(change_symbol, lambda c: c.data == "change_symbol")
dp.callback_query.register(change_supply, lambda c: c.data == "change_supply")
dp.callback_query.register(change_logo, lambda c: c.data == "change_logo")
dp.callback_query.register(change_wallet, lambda c: c.data == "change_wallet")
dp.callback_query.register(change_description, lambda c: c.data == "change_description")
dp.callback_query.register(back_to_confirmation_from_edit, lambda c: c.data == "back_from_edit")

dp.callback_query.register(buy_custom_address, lambda c: c.data == "buy_custom_address")
dp.callback_query.register(select_custom_ending, lambda c: c.data.startswith("custom_ending:"))
dp.callback_query.register(back_to_confirmation, lambda c: c.data == "back_to_confirmation")
dp.callback_query.register(cancel_custom_address, lambda c: c.data == "cancel_custom_address")

dp.callback_query.register(process_confirmation, lambda c: c.data == "confirm_creation")
dp.callback_query.register(back_to_edit_from_payment, lambda c: c.data == "back_to_edit_from_payment")

dp.callback_query.register(ref_add_wallet, lambda c: c.data == "ref_add_wallet")
dp.callback_query.register(ref_change_wallet, lambda c: c.data == "ref_change_wallet")

dp.callback_query.register(bonus_info, lambda c: c.data == "bonus_info")

dp.callback_query.register(check_payment, lambda c: c.data == "check_payment")

dp.message.register(process_token_name, BotStates.token_name)
dp.message.register(process_token_symbol, BotStates.token_symbol)
dp.message.register(process_token_supply, BotStates.token_supply)
dp.message.register(process_token_logo, BotStates.token_logo)
dp.message.register(process_user_wallet, BotStates.user_wallet)
dp.message.register(process_token_description, BotStates.token_description)
dp.message.register(process_during_creation, BotStates.creating_token)

dp.message.register(process_admin_message, BotStates.uploading_wallets)

dp.message.register(process_wallet_input, ReferralStates.waiting_wallet)

dp.message.register(check_payment_button, BotStates.waiting_payment, F.text.in_(["Check payment"]))
dp.message.register(confirm_custom_address, BotStates.confirm_custom_address)

dp.message.register(process_message)