# bot.py
import asyncio
import random
import re
import json
import os
from datetime import datetime, timedelta
from collections import defaultdict
from abc import ABC, abstractmethod
from typing import List, Tuple, Optional, Dict
from telethon import TelegramClient, events
from pydub import AudioSegment
from difflib import SequenceMatcher


# ---- CONFIGURATION ----
class Config:
    """Centralized configuration management"""

    def __init__(self):
        self.api_id = 1            # your api_id
        self.api_hash = ""  # your api_hash
        self.session_name = "session"
        self.proxy = ('socks5', '127.0.0.1', 10808)
        self.group_name = "clashcity"
        self.chat_data_file = "result.json"

        # Feature-specific configs
        self.trigger_words = ["مهدی"]
        self.trigger_responses = ["بله👻"]
        self.stats_word = "آمار"
        self.audio_command = "آهنگ"
        self.download_dir = "downloaded_audios"


# ---- BASE FEATURE CLASS ----
class Feature(ABC):
    """Abstract base class for bot features"""

    def __init__(self, config: Config):
        self.config = config

    @abstractmethod
    async def can_handle(self, event, message_text: str, chat, sender) -> bool:
        """Check if this feature can handle the given message"""
        pass

    @abstractmethod
    async def handle(self, event, message_text: str, chat, sender, client) -> bool:
        """Handle the message. Return True if handled, False otherwise"""
        pass

    @abstractmethod
    def get_description(self) -> str:
        """Get feature description for help command"""
        pass


# ---- CHAT DATA PROCESSOR ----
class ChatDataProcessor:
    """Handles chat data loading and processing"""

    def __init__(self, data_file: str):
        self.data_file = data_file
        self.messages = []
        self.load_data()

    def load_data(self):
        """Load chat data from JSON file"""
        try:
            with open(self.data_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.messages = data.get('messages', [])
            print(
                f"Loaded {len(self.messages)} messages from {self.data_file}")
        except Exception as e:
            print(f"Error loading chat data: {e}")
            self.messages = []

    def parse_datetime(self, date_str: str) -> Optional[datetime]:
        """Parse date string to datetime object"""
        try:
            if 'T' in date_str:
                return datetime.strptime(date_str, '%Y-%m-%dT%H:%M:%S')
            else:
                return datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')
        except:
            return None

    def get_messages_in_timeframe(self, hours: int = 24) -> List[Dict]:
        """Get messages from the last specified hours"""
        if not self.messages:
            return []

        cutoff_time = datetime.now() - timedelta(hours=hours)
        recent_messages = []

        for msg in self.messages:
            if 'date' not in msg:
                continue

            msg_time = self.parse_datetime(msg['date'])
            if msg_time and msg_time >= cutoff_time:
                recent_messages.append(msg)

        return recent_messages

    def collect_user_stats(self, target_name: str, hours: int = 24) -> Optional[Dict]:
        """Collect comprehensive statistics for a specific user"""
        recent_messages = self.get_messages_in_timeframe(hours)

        if not recent_messages:
            return None

        # Data structures for statistics
        user_stats = defaultdict(lambda: {
            'total_messages': 0,
            'text_messages': 0,
            'sticker_messages': 0,
            'gif_messages': 0,
            'photo_messages': 0,
            'video_messages': 0,
            'voice_messages': 0,
            'replies_to': defaultdict(int),
            'replies_from': defaultdict(int),
            'reactions_received': 0,
            'reactions_given': 0
        })

        # Create a mapping of message IDs to messages for reply tracking
        message_map = {
            msg['id']: msg for msg in recent_messages if 'id' in msg}

        # First pass: count basic statistics and build user map
        user_map = {}
        for msg in recent_messages:
            if 'from' in msg and 'from_id' in msg:
                user_map[msg['from_id']] = msg['from']

        # Second pass: analyze each message
        for msg in recent_messages:
            if msg.get('type') != 'message':
                continue

            from_user = msg.get('from', 'ناشناس')
            from_id = msg.get('from_id', 'unknown')

            # Count message types
            user_stats[from_id]['total_messages'] += 1

            # Check message content type
            if msg.get('media_type'):
                media_type = msg['media_type']
                if media_type == 'sticker':
                    user_stats[from_id]['sticker_messages'] += 1
                elif media_type == 'gif' or media_type == 'animation':
                    user_stats[from_id]['gif_messages'] += 1
                elif media_type == 'photo':
                    user_stats[from_id]['photo_messages'] += 1
                elif media_type == 'video':
                    user_stats[from_id]['video_messages'] += 1
                elif media_type == 'voice':
                    user_stats[from_id]['voice_messages'] += 1
                else:
                    user_stats[from_id]['text_messages'] += 1
            else:
                user_stats[from_id]['text_messages'] += 1

            # Track replies
            if 'reply_to_message_id' in msg:
                replied_msg_id = msg['reply_to_message_id']
                if replied_msg_id in message_map:
                    replied_msg = message_map[replied_msg_id]
                    replied_user = replied_msg.get('from', 'ناشناس')
                    replied_user_id = replied_msg.get('from_id', 'unknown')

                    user_stats[from_id]['replies_to'][replied_user] += 1
                    user_stats[replied_user_id]['replies_from'][from_user] += 1

            # Track reactions
            if 'reactions' in msg:
                user_stats[from_id]['reactions_received'] += len(
                    msg['reactions'])
                for reaction in msg['reactions']:
                    if 'recent' in reaction:
                        for reactor in reaction['recent']:
                            reactor_id = reactor.get('from_id', 'unknown')
                            user_stats[reactor_id]['reactions_given'] += 1

        # Find target user by name
        target_user_id = None
        target_display_name = target_name

        for user_id, stats in user_stats.items():
            if user_id in user_map:
                display_name = user_map[user_id]
                if target_name.lower() in display_name.lower():
                    target_user_id = user_id
                    target_display_name = display_name
                    break

        if target_user_id is None or target_user_id not in user_stats:
            return None

        return {
            'user_id': target_user_id,
            'display_name': target_display_name,
            'stats': user_stats[target_user_id],
            'all_users_stats': user_stats,
            'user_map': user_map,
            'timeframe_hours': hours
        }


# ---- FEATURE IMPLEMENTATIONS ----

class TriggerResponseFeature(Feature):
    """Feature for responding to trigger words"""

    def normalize_text(self, text: str) -> str:
        # Remove leading/trailing whitespace, and collapse multiple spaces/tabs into one
        return re.sub(r'\s+', ' ', text.strip())

    async def can_handle(self, event, message_text: str, chat, sender) -> bool:
        normalized_text = self.normalize_text(message_text)
        return any(trigger in normalized_text for trigger in self.config.trigger_words)

    async def handle(self, event, message_text: str, chat, sender, client) -> bool:
        normalized_text = self.normalize_text(message_text)
        if await self.can_handle(event, normalized_text, chat, sender):
            reply = random.choice(self.config.trigger_responses)
            await event.reply(reply)
            print(f"Replied in {chat.title} to {sender.first_name}: {reply}")
            return True
        return False

    def get_description(self) -> str:
        return f"Responds to trigger words: {', '.join(self.config.trigger_words)}"


class StatisticsFeature(Feature):
    """Feature for generating user statistics"""

    def __init__(self, config: Config):
        super().__init__(config)
        self.chat_processor = ChatDataProcessor(config.chat_data_file)

    async def can_handle(self, event, message_text: str, chat, sender) -> bool:
        return message_text.startswith(self.config.stats_word)

    async def handle(self, event, message_text: str, chat, sender, client) -> bool:
        if not await self.can_handle(event, message_text, chat, sender):
            return False

        # Parse command: "آمار username [hours]"
        match = re.match(r"آمار\s+(\S+)(?:\s+(\d+))?", message_text)
        if not match:
            await event.reply("❌ فرمت درست: آمار username [hours]")
            return True

        username, hours_str = match.groups()
        hours = int(hours_str) if hours_str else 24

        # Collect statistics
        stats_result = self.chat_processor.collect_user_stats(username, hours)

        if not stats_result:
            await event.reply(f"❌ کاربری با نام '{username}' یافت نشد یا هیچ فعالیتی در {hours} ساعت اخیر نداشته است.")
            return True

        # Generate report
        report = self._generate_stats_report(stats_result)
        await event.reply(report)
        print(
            f"Stats generated for {stats_result['display_name']} (last {hours} hours)")
        return True

    def _generate_stats_report(self, stats_result: Dict) -> str:
        """Generate formatted statistics report"""
        target_stats = stats_result['stats']
        target_display_name = stats_result['display_name']
        hours = stats_result['timeframe_hours']
        total_msgs = target_stats['total_messages']

        if total_msgs == 0:
            return f"❌ کاربر '{target_display_name}' هیچ پیامی در {hours} ساعت اخیر نداشته است."

        # Calculate ratios
        sticker_gif_ratio = (
            (target_stats['sticker_messages'] + target_stats['gif_messages']) / total_msgs) * 100

        # Format replies made by target
        replies_made = []
        for target_user, reply_count in target_stats['replies_to'].items():
            ratio = (reply_count / total_msgs) * 100 if total_msgs > 0 else 0
            replies_made.append(
                f"  • {target_user}: {reply_count} ({ratio:.1f}%)")

        replies_made.sort(key=lambda x: int(
            x.split(': ')[1].split(' ')[0]), reverse=True)
        replies_made_summary = "\n".join(
            replies_made) if replies_made else "  (هیچ ریپلایی ارسال نکرده)"

        # Format replies received by target
        replies_received = []
        for source_user, reply_count in target_stats['replies_from'].items():
            source_total_msgs = 0
            for user_id, user_info in stats_result['all_users_stats'].items():
                if user_id in stats_result['user_map'] and stats_result['user_map'][user_id] == source_user:
                    source_total_msgs = user_info['total_messages']
                    break

            ratio = (reply_count / source_total_msgs) * \
                100 if source_total_msgs > 0 else 0
            replies_received.append(
                f"  • {source_user}: {reply_count} ({ratio:.1f}% از پیام‌هایش)")

        replies_received.sort(key=lambda x: int(
            x.split(': ')[1].split(' ')[0]), reverse=True)
        replies_received_summary = "\n".join(
            replies_received) if replies_received else "  (هیچ ریپلایی دریافت نکرده)"

        # Format media statistics
        media_summary = []
        if target_stats['photo_messages'] > 0:
            media_summary.append(f"  • عکس: {target_stats['photo_messages']}")
        if target_stats['video_messages'] > 0:
            media_summary.append(
                f"  • ویدیو: {target_stats['video_messages']}")
        if target_stats['voice_messages'] > 0:
            media_summary.append(f"  • صدا: {target_stats['voice_messages']}")

        media_display = "\n".join(
            media_summary) if media_summary else "  (هیچ مدیایی ارسال نکرده)"

        return (
            f"📊 آمار {target_display_name} در {hours} ساعت اخیر:\n\n"
            f"📈 کلی:\n"
            f"• کل پیام: {total_msgs}\n"
            f"• متنی: {target_stats['text_messages']}\n"
            f"• استیکر: {target_stats['sticker_messages']}\n"
            f"• گیف: {target_stats['gif_messages']}\n"
            f"• نسبت استیکر+گیف: {sticker_gif_ratio:.1f}%\n"
            f"• ری‌اکشن داده: {target_stats['reactions_given']}\n"
            f"• ری‌اکشن گرفته: {target_stats['reactions_received']}\n\n"
            f"📷 مدیا:\n{media_display}\n\n"
            f"🔁 ریپلای فرستاده:\n{replies_made_summary}\n\n"
            f"🔁 ریپلای گرفته:\n{replies_received_summary}\n\n"
            f"ℹ️ توضیحات:\n"
            f"• ریپلای فرستاده = پیام‌هایی که {target_display_name} در پاسخ به دیگران داده.\n"
            f"• ریپلای گرفته = پیام‌هایی که دیگران در پاسخ به {target_display_name} داده‌اند."
        )

    def get_description(self) -> str:
        return f"Generate user statistics with: {self.config.stats_word} username [hours]"


class AudioCroppingFeature(Feature):
    """Feature for cropping audio files"""

    async def can_handle(self, event, message_text: str, chat, sender) -> bool:
        return message_text.startswith(self.config.audio_command) and event.is_reply

    async def handle(self, event, message_text: str, chat, sender, client) -> bool:
        if not await self.can_handle(event, message_text, chat, sender):
            return False

        # Parse command: آهنگ [ID] [start] [end]
        parts = message_text.split()
        if len(parts) != 4:
            await event.reply("⚠️ فرمت دستور نادرست است. مثال: آهنگ 4191 2:01 3:22")
            return True

        try:
            audio_id = parts[1]
            start_time = parts[2]
            end_time = parts[3]

            # Validate time format
            if not re.match(r'^\d+:\d+$', start_time) or not re.match(r'^\d+:\d+$', end_time):
                await event.reply("⚠️ فرمت زمان نادرست است. از فرمت MM:SS استفاده کنید.")
                return True

            # Convert time to seconds
            start_seconds = self._time_to_seconds(start_time)
            end_seconds = self._time_to_seconds(end_time)

            if start_seconds >= end_seconds:
                await event.reply("⚠️ زمان پایان باید بعد از زمان شروع باشد.")
                return True

            # Process audio
            success = await self._process_audio(event, client, audio_id, start_seconds, end_seconds, start_time, end_time)
            if success:
                print(f"Audio cropped and sent for user {sender.first_name}")

        except ValueError:
            await event.reply("⚠️ فرمت دستور نادرست است. مثال: آهنگ 4191 2:01 3:22")
        except Exception as e:
            await event.reply(f"❌ خطا: {str(e)}")

        return True

    def _time_to_seconds(self, time_str: str) -> int:
        """Convert MM:SS format to seconds"""
        minutes, seconds = map(int, time_str.split(':'))
        return minutes * 60 + seconds

    async def _process_audio(self, event, client, audio_id: str, start_seconds: int, end_seconds: int, start_time: str, end_time: str) -> bool:
        """Process and crop audio file"""
        try:
            # Delete the user's command message
            await event.delete()

            # Get the replied message
            replied_msg = await event.get_reply_message()

            # Create downloads directory
            os.makedirs(self.config.download_dir, exist_ok=True)

            # Define file paths
            audio_path = os.path.join(
                self.config.download_dir, f"audio_{audio_id}.mp3")
            output_path = os.path.join(
                self.config.download_dir, f"cropped_audio_{audio_id}.ogg")

            # Download audio if not exists
            if not os.path.exists(audio_path):
                audio_message = await client.get_messages('ahangd00ni', ids=int(audio_id))
                if not audio_message or not audio_message.audio:
                    await event.reply("❌ آهنگ مورد نظر یافت نشد.")
                    return False

                audio_path = await audio_message.download_media(file=audio_path)

            # Crop the audio
            audio = AudioSegment.from_file(audio_path)
            start_ms = start_seconds * 1000
            end_ms = min(end_seconds * 1000, len(audio))

            cropped_audio = audio[start_ms:end_ms]
            cropped_audio.export(output_path, format="ogg", codec="libvorbis")

            # Send cropped audio
            await client.send_file(
                event.chat_id,
                output_path,
                caption=f"🎵 برش آهنگ از {start_time} تا {end_time}",
                voice_note=True,
                reply_to=replied_msg.id
            )

            # Clean up cropped file
            if os.path.exists(output_path):
                os.remove(output_path)

            return True

        except Exception as e:
            await event.reply(f"❌ خطا در پردازش آهنگ: {str(e)}")
            return False

    def get_description(self) -> str:
        return f"Crop audio files with: {self.config.audio_command} [ID] [start_time] [end_time]"


class HelpFeature(Feature):
    """Feature for displaying help information"""

    def __init__(self, config: Config, features: List[Feature]):
        super().__init__(config)
        self.features = features

    async def can_handle(self, event, message_text: str, chat, sender) -> bool:
        return message_text.strip().lower() in ["help", "راهنما", "کمک"]

    async def handle(self, event, message_text: str, chat, sender, client) -> bool:
        if not await self.can_handle(event, message_text, chat, sender):
            return False

        help_text = "🤖 راهنمای ربات:\n\n"
        for i, feature in enumerate(self.features, 1):
            if feature != self:  # Don't include help in help
                help_text += f"{i}. {feature.get_description()}\n"

        help_text += "\n💡 برای راهنما: help یا راهنما یا کمک"

        await event.reply(help_text)
        return True

    def get_description(self) -> str:
        return "Display this help message"


class ChatAnalysisFeature(Feature):
    """Feature for analyzing recent messages and generating AI responses"""

    def __init__(self, config: Config):
        super().__init__(config)
        self.message_buffer: List[Dict] = []
        self.chatbot_username = "@GPT4Telegrambot"
        # self.chatbot_username = '@CopilotOfficialBot'
        self.message_threshold = 20  # Number of messages to trigger analysis
        self.processing = False  # Flag to prevent multiple simultaneous analyses

        # Updated prompt to include message IDs
        self.prompt = """
            {{
            فرض کن توی یک گروه دوستانه هستی.  
            اسم تو مهدی هست.  

            بچه‌های دیگه گروه:  
            - Sheyda  
            - sajad_REAL  
            - Sepide  

            شخصیت تو:  
            تو آدمی دقیق، نکته‌سنج و عمیقی. کمتر جواب میدی، اما وقتی میدی همیشه روی یک نکته‌ی ظریف یا یک ارتباط پنهان بین پیام‌ها دست می‌ذاری. جواب‌هات کوتاه، سنگین و سنجیده هستن. هیچ‌وقت شوخی بی‌مزه نمی‌کنی.  

            شخصیت‌های بقیه:  
            - Sheyda: دختر مهربون، زود دلخور میشه، تقریبا با همه حرف میزنه، و بیشتر از همه مرکز توجه گروهه.  
            - sajad_REAL: پسر مهربون، با همه حرف میزنه، مخصوصاً با دخترا صمیمی و رفیق‌مآب (مثلاً درباره غذا و موضوعات روزمره).  
            - Sepide: یه دختر خوب و معمولی که تو (مهدی) باهاش دوستی نزدیک داری.  

            قانون‌ها:  
            1. من یه دنباله از پیام‌ها میدم (به شکل [(message_id, اسم، پیام، ریپلای_به_message_id), (message_id, اسم، پیام, ریپلای_به_message_id), ...]).  
            - هر پیام یک message_id منحصر به فرد داره.  
            - اگه پیام ریپلای باشه، ریپلای_به_message_id مشخص میشه، وگرنه None خواهد بود.  
            2. تو باید با توجه به شخصیت خودت (مهدی) یک پیام کوتاه و سنگین/دقیق/نکته‌سنج تولید کنی.  
            3. جواب تو همیشه باید دقیقاً در این فرمت باشه:  
            {{'reply_to_message_id': '<message_id یکی از پیام‌ها>', 'msg': '<پیام تو>'}}  
            4. فقط یک message_id انتخاب کن که ریپلای بزنی (از message_id های موجود در لیست).  
            5. حتماً باید یک ارتباط ظریف یا معنایی بین چند پیام پیدا کنی و روی اون دست بذاری.  
            6. جواب‌ها باید کوتاه، عمیق و بدون شوخی بی‌مزه باشن.  
            7. جواب‌ها نباید سطحی باشن؛ باید نشون بدن تو خیلی ریزبین و دقیق هستی.  

            مثال:  
            ورودی:  
            [(101, 'Sheyda','سلام خوبید', None), (102, 'sajad_REAL', 'سلام قربونت', 101)]  

            خروجی نمونه:  
            {{'reply_to_message_id': '102', 'msg':'جالبه که جواب سلام با محبت، خودش شبیه سلام دوباره‌ست.'}}  

            حالا باید برای پیام زیر جواب بنویسی:  

            {data}
            }}
            """

    async def can_handle(self, event, message_text: str, chat, sender) -> bool:
        # This feature monitors all messages but doesn't handle specific commands
        return False

    async def handle(self, event, message_text: str, chat, sender, client) -> bool:
        """Monitor and analyze messages"""
        try:
            # Monitor this message
            await self._monitor_message(event, chat, sender, client)
            return False  # Don't consume the message, let other features handle it
        except Exception as e:
            print(f"Error in ChatAnalysisFeature.handle: {e}")
            return False

    def get_description(self) -> str:
        return "تحلیل هوشمند گفتگو - تولید پاسخ‌های خودکار بر اساس مکالمات اخیر (هر ۱۰ پیام)"

    async def _monitor_message(self, event, chat, sender, client):
        """Monitor and store incoming messages"""
        try:
            # Skip if already processing
            if self.processing:
                return

            # Get sender username
            username = getattr(sender, 'username', None) or getattr(
                sender, 'first_name', 'Unknown')

            # Get message text
            message_text = event.raw_text.strip()
            if not message_text:
                return

            # Get message ID
            message_id = event.message.id

            # Check if message is a reply
            reply_to_message_id = None
            if event.is_reply:
                try:
                    replied_msg = await event.get_reply_message()
                    if replied_msg:
                        reply_to_message_id = replied_msg.id
                except:
                    pass

            # Create message data
            message_data = {
                'message_id': message_id,
                'username': username,
                'message': message_text,
                'reply_to_message_id': reply_to_message_id,
                'timestamp': datetime.now(),
                'event': event  # Store event for potential reply
            }

            # Add to buffer
            self.message_buffer.append(message_data)

            # Clean old messages (older than 10 minutes)
            self._clean_old_messages()

            # Check if we have enough messages to trigger analysis
            if len(self.message_buffer) >= self.message_threshold:
                await self._analyze_and_respond(client)

        except Exception as e:
            print(f"Error in _monitor_message: {e}")

    def _clean_old_messages(self):
        """Remove messages older than 10 minutes"""
        cutoff_time = datetime.now() - timedelta(minutes=10)
        self.message_buffer = [
            msg for msg in self.message_buffer
            if msg['timestamp'] > cutoff_time
        ]

    def _prepare_conversation_data(self) -> List[Tuple]:
        """Convert message buffer to the required data structure with message IDs"""
        conversation_data = []

        for msg_data in self.message_buffer:
            # Format: (message_id, username, message, reply_to_message_id)
            conversation_data.append((
                msg_data['message_id'],
                msg_data['username'],
                msg_data['message'],
                msg_data['reply_to_message_id']
            ))

        return conversation_data

    async def _analyze_and_respond(self, client):
        """Send conversation data to chatbot and handle response"""
        try:
            # Set processing flag to prevent concurrent analyses
            self.processing = True

            # Prepare conversation data
            conversation_data = self._prepare_conversation_data()

            if not conversation_data:
                return

            # Format prompt with data
            formatted_prompt = self.prompt.format(data=str(conversation_data))

            # Send to chatbot
            print(f"Sending analysis request to {self.chatbot_username}")
            print(f"Data: {conversation_data}")

            # Send message to chatbot
            await client.send_message(self.chatbot_username, formatted_prompt)

            # Wait for response (with timeout)
            response = await self._wait_for_chatbot_response(client)

            if response:
                await self._process_chatbot_response(response, client)
            else:
                print("No response received from chatbot")

            # Clear buffer after analysis
            self.message_buffer.clear()

        except Exception as e:
            print(f"Error in _analyze_and_respond: {e}")
        finally:
            # Reset processing flag
            self.processing = False

    async def _wait_for_chatbot_response(self, client, timeout: int = 30) -> Optional[str]:
        """
        Wait for chatbot response with a timeout.
        Only accepts messages that start with "{'reply_to_message_id'" to ignore status/interim messages.
        """
        try:
            chatbot_entity = await client.get_entity(self.chatbot_username)

            future = asyncio.get_event_loop().create_future()

            @client.on(events.NewMessage(from_users=chatbot_entity))
            async def handler(event):
                if future.done():
                    return

                response_text = event.message.message or ""

                # Accept only messages starting with "{'reply_to_message_id'"
                if not response_text.strip().startswith("{'reply_to_message_id'"):
                    print(f"Ignoring non-response message: {response_text}")
                    return

                future.set_result(response_text)

            try:
                # Wait for the future to complete or timeout
                response = await asyncio.wait_for(future, timeout=timeout)
                return response
            except asyncio.TimeoutError:
                print("Timeout waiting for chatbot response")
                return None
            finally:
                # Remove handler to avoid memory leaks
                client.remove_event_handler(handler, events.NewMessage)

        except Exception as e:
            print(f"Error waiting for chatbot response: {e}")
            return None

    async def _process_chatbot_response(self, response_text: str, client):
        """Process chatbot response and reply to specific message"""
        try:
            # Parse JSON response
            response_data = self._parse_chatbot_response(response_text)

            if not response_data:
                print("Failed to parse chatbot response")
                print(f"Raw response: {response_text}")
                return

            reply_to_message_id = response_data.get('reply_to_message_id')
            message = response_data.get('msg')

            if not reply_to_message_id or not message:
                print("Invalid response format from chatbot")
                print(f"Parsed data: {response_data}")
                return

            # Convert message_id to integer for comparison
            try:
                target_message_id = int(reply_to_message_id)
            except ValueError:
                print(f"Invalid message ID: {reply_to_message_id}")
                return

            # Find the specific message by ID
            target_event = self._find_message_by_id(target_message_id)

            if target_event:
                # Reply to the specific message
                await target_event.reply(message)
                print(f"Replied to message ID {target_message_id}: {message}")
            else:
                # If we can't find the specific message, send to group
                try:
                    group_entity = await client.get_entity(self.config.group_name)
                    await client.send_message(group_entity, message)
                    print(
                        f"Sent message to group (couldn't find message ID {target_message_id}): {message}")
                except Exception as e:
                    print(f"Error sending message to group: {e}")

        except Exception as e:
            print(f"Error processing chatbot response: {e}")

    def _parse_chatbot_response(self, response_text: str) -> Optional[Dict]:
        """Parse chatbot JSON response"""
        try:
            # Clean the response text
            response_text = response_text.strip()

            # Try to find JSON in the response
            json_match = re.search(r'\{[^}]*\}', response_text)
            if json_match:
                json_str = json_match.group()
                return json.loads(json_str)
            else:
                # Try parsing the entire response as JSON
                return json.loads(response_text)

        except json.JSONDecodeError:
            try:
                # Try to extract using regex for the new format
                message_id_match = re.search(
                    r'"reply_to_message_id":\s*"([^"]*)"', response_text)
                msg_match = re.search(r'"msg":\s*"([^"]*)"', response_text)

                if message_id_match and msg_match:
                    return {
                        'reply_to_message_id': message_id_match.group(1),
                        'msg': msg_match.group(1)
                    }

                # Try alternative patterns with single quotes
                message_id_match = re.search(
                    r"'reply_to_message_id':\s*'([^']*)'", response_text)
                msg_match = re.search(r"'msg':\s*'([^']*)'", response_text)

                if message_id_match and msg_match:
                    return {
                        'reply_to_message_id': message_id_match.group(1),
                        'msg': msg_match.group(1)
                    }

            except Exception as regex_error:
                print(f"Regex parsing error: {regex_error}")

        except Exception as e:
            print(f"JSON parsing error: {e}")

        return None

    def _find_message_by_id(self, message_id: int) -> Optional:
        """Find a message by its ID"""
        for msg_data in self.message_buffer:
            if msg_data['message_id'] == message_id:
                return msg_data['event']
        return None


# ---- MAIN BOT CLASS ----


class TelegramBot:
    """Main bot class that manages all features"""

    def __init__(self, config: Config):
        self.config = config
        self.client = TelegramClient(
            config.session_name,
            config.api_id,
            config.api_hash,
            proxy=config.proxy
        )
        self.features: List[Feature] = []
        self._setup_features()

    def _setup_features(self):
        """Initialize all bot features"""
        # Core features
        self.features.extend([
            TriggerResponseFeature(self.config),
            StatisticsFeature(self.config),
            AudioCroppingFeature(self.config),
            ChatAnalysisFeature(self.config)
        ])

        # Add help feature (needs reference to other features)
        self.features.append(HelpFeature(self.config, self.features))

    def add_feature(self, feature: Feature):
        """Add a new feature to the bot"""
        self.features.append(feature)

    def remove_feature(self, feature_class):
        """Remove a feature from the bot"""
        self.features = [
            f for f in self.features if not isinstance(f, feature_class)]

    async def _handle_message(self, event):
        """Handle incoming messages"""
        try:
            chat = await event.get_chat()
            sender = await event.get_sender()

            # Only process messages from target group
            if not (hasattr(chat, "title") and chat.title.lower() == self.config.group_name.lower()):
                return

            message_text = event.raw_text.strip()

            # Try each feature until one handles the message
            for feature in self.features:
                try:
                    if await feature.handle(event, message_text, chat, sender, self.client):
                        break  # Stop after first successful handler
                except Exception as e:
                    print(
                        f"Error in feature {feature.__class__.__name__}: {e}")

        except Exception as e:
            print(f"Error in message handler: {e}")

    async def start(self):
        """Start the bot"""
        self.client.add_event_handler(self._handle_message, events.NewMessage)

        print("Bot is starting...")
        print(f"Loaded {len(self.features)} features:")
        for feature in self.features:
            print(f"  - {feature.__class__.__name__}")

        print("Bot is running... Press Ctrl+C to stop.")
        await self.client.start()
        await self.client.run_until_disconnected()


# ---- EXAMPLE: ADDING A NEW FEATURE ----
class WelcomeFeature(Feature):
    """Example of how easy it is to add new features"""

    async def can_handle(self, event, message_text: str, chat, sender) -> bool:
        # Handle when new members join
        return hasattr(event, 'user_joined') and event.user_joined

    async def handle(self, event, message_text: str, chat, sender, client) -> bool:
        if await self.can_handle(event, message_text, chat, sender):
            await event.reply(f"خوش آمدید {sender.first_name}! 🎉")
            return True
        return False

    def get_description(self) -> str:
        return "Welcome new members to the group"


# ---- MAIN EXECUTION ----
async def main():
    config = Config()
    bot = TelegramBot(config)

    # Example: Add a new feature easily
    # bot.add_feature(WelcomeFeature(config))

    await bot.start()


if __name__ == "__main__":
    asyncio.run(main())
