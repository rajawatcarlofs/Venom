from telethon import TelegramClient, events
from telethon.errors import SessionPasswordNeededError
import os
import asyncio
import time
from datetime import datetime, timedelta
import logging
from config import Config

logger = logging.getLogger(__name__)

class TelegramHandler:
    def __init__(self, db):
        self.db = db
        self.clients = {}
        self.config = Config.get_config()
        self.api_id = self.config.API_ID
        self.api_hash = self.config.API_HASH
        self.session_path = self.config.SESSION_PATH
        
        if not self.api_id or not self.api_hash:
            logger.error("API_ID and API_HASH not configured")
    
    def get_session_file(self, phone):
        os.makedirs(self.session_path, exist_ok=True)
        return os.path.join(self.session_path, f"{phone}")
    
    def create_client(self, phone):
        try:
            session_file = self.get_session_file(phone)
            client = TelegramClient(session_file, self.api_id, self.api_hash)
            return client
        except Exception as e:
            logger.error(f"Error creating client: {str(e)}")
            return None
    
    def start_login(self, phone):
        try:
            client = self.create_client(phone)
            if not client:
                return {'success': False, 'error': 'Failed to create client'}
            
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            async def login():
                await client.connect()
                await client.send_code_request(phone)
                return {'success': True, 'message': 'Code sent to Telegram app'}
            
            result = loop.run_until_complete(login())
            loop.close()
            return result
        except Exception as e:
            logger.error(f"Error starting login: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def complete_login(self, phone, code):
        try:
            client = self.create_client(phone)
            if not client:
                return {'success': False, 'error': 'Failed to create client'}
            
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            async def verify():
                await client.connect()
                try:
                    await client.sign_in(phone, code)
                except SessionPasswordNeededError:
                    return {'success': False, 'error': 'Two-factor authentication required'}
                
                user = await client.get_me()
                await client.disconnect()
                return {
                    'success': True,
                    'user_id': user.id,
                    'user_name': user.first_name or 'User'
                }
            
            result = loop.run_until_complete(verify())
            loop.close()
            return result
        except Exception as e:
            logger.error(f"Error completing login: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def disconnect_account(self, account_id):
        try:
            account = self.db.get_account(account_id)
            if not account:
                return {'success': False, 'error': 'Account not found'}
            
            session_file = self.get_session_file(account.phone)
            if os.path.exists(session_file):
                os.remove(session_file)
            
            self.db.update_account_status(account_id, 'offline')
            return {'success': True}
        except Exception as e:
            logger.error(f"Error disconnecting account: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def get_account_status(self, account_id):
        try:
            account = self.db.get_account(account_id)
            if not account:
                return {'success': False, 'error': 'Account not found'}
            
            session_file = self.get_session_file(account.phone)
            is_connected = os.path.exists(session_file)
            
            status = 'online' if is_connected else 'offline'
            self.db.update_account_status(account_id, status)
            
            return {
                'success': True,
                'account_id': account_id,
                'status': status
            }
        except Exception as e:
            logger.error(f"Error getting account status: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def load_groups_for_accounts(self, account_ids):
        groups = []
        try:
            for account_id in account_ids:
                account = self.db.get_account(account_id)
                if not account:
                    continue
                
                client = self.create_client(account.phone)
                if not client:
                    continue
                
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                
                async def fetch_groups():
                    result = []
                    try:
                        await client.connect()
                        async for dialog in client.iter_dialogs():
                            if dialog.is_group or dialog.is_channel:
                                result.append({
                                    'name': dialog.name,
                                    'chat_id': dialog.id,
                                    'type': 'channel' if dialog.is_channel else 'group',
                                    'members': dialog.entity.participants_count if hasattr(dialog.entity, 'participants_count') else 0
                                })
                        await client.disconnect()
                    except Exception as e:
                        logger.error(f"Error fetching groups: {str(e)}")
                    return result
                
                groups.extend(loop.run_until_complete(fetch_groups()))
                loop.close()
            
            return groups
        except Exception as e:
            logger.error(f"Error loading groups: {str(e)}")
            return []
    
    def execute_campaign(self, campaign_id):
        try:
            campaign = self.db.get_campaign(campaign_id)
            if not campaign:
                logger.error(f"Campaign {campaign_id} not found")
                return
            
            account_ids = campaign.account_ids
            group_ids = campaign.group_ids
            message = campaign.message
            
            for account_id in account_ids:
                if not self._can_continue_campaign(campaign_id):
                    break
                
                account = self.db.get_account(account_id)
                if not account:
                    continue
                
                client = self.create_client(account.phone)
                if not client:
                    continue
                
                for group_id in group_ids:
                    if not self._can_continue_campaign(campaign_id):
                        break
                    
                    group = self.db.get_group(group_id)
                    if not group:
                        continue
                    
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    
                    async def send_message():
                        try:
                            await client.connect()
                            await client.send_message(group.chat_id, message)
                            await client.disconnect()
                            self.db.increment_stat('messages_sent')
                            self.db.update_campaign_stats(campaign_id, messages_sent=1)
                            logger.info(f"Message sent to {group.name}")
                            return True
                        except Exception as e:
                            logger.error(f"Error sending message: {str(e)}")
                            self.db.increment_stat('failed_deliveries')
                            self.db.update_campaign_stats(campaign_id, failed_sends=1)
                            return False
                    
                    try:
                        loop.run_until_complete(send_message())
                    finally:
                        loop.close()
                    
                    delay = self.config.MESSAGE_DELAY
                    time.sleep(delay)
        except Exception as e:
            logger.error(f"Error executing campaign: {str(e)}")
            self.db.log_activity(f'Campaign execution error: {str(e)}', 'error')
    
    def _can_continue_campaign(self, campaign_id):
        campaign = self.db.get_campaign(campaign_id)
        return campaign and campaign.status not in ['stopped', 'completed']
