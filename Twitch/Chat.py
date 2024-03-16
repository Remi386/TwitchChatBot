
from twitchAPI.helper import first
from twitchAPI.twitch import Twitch
from twitchAPI.oauth import UserAuthenticator
from twitchAPI.type import AuthScope, ChatEvent
from twitchAPI.chat import Chat, EventData, ChatMessage, ChatCommand, NoticeEvent


class ChatBot:
    USER_SCOPE = [AuthScope.CHAT_READ, AuthScope.CHAT_EDIT, AuthScope.CLIPS_EDIT, AuthScope.WHISPERS_READ]

    def __init__(self):
        self.superuser_id: int = -1
        self.target_channels = []
        self.twitch: Twitch = None
        self.chat: Chat = None

    async def aconnect_dict(self, settings: dict):
        try:
            app_id = settings["app_id"]
            app_secret = settings["app_secret"]
            target_channels = settings["target_channels"]
            superuser = settings["superuser"]
        except KeyError as ex:
            print("Missing twitch setting: " + str(ex))
        else:
            await self.aconnect(app_id=app_id, app_secret=app_secret, target_channels=target_channels,
                                superuser=superuser)

    async def aconnect(self, app_id: str, app_secret: str, target_channels: list[str], superuser: str):
        self.twitch = await Twitch(app_id, app_secret)
        auth = UserAuthenticator(self.twitch, self.USER_SCOPE)
        token, refresh_token = await auth.authenticate()
        await self.twitch.set_user_authentication(token, self.USER_SCOPE, refresh_token)
        self.target_channels = target_channels
        self.chat = await Chat(self.twitch)

        superuser = await first(self.twitch.get_users(logins=superuser))
        self.superuser_id = superuser.id

        # listen to when the bot is done starting up and ready to join channels
        self.chat.register_event(ChatEvent.READY, self.on_ready)
        # listen to chat messages
        self.chat.register_event(ChatEvent.MESSAGE, self.on_message)

        self.chat.register_event(ChatEvent.MESSAGE_DELETE, self.on_message_deleted)
        # listen to channel subscriptions
        # self.chat.register_event(ChatEvent.SUB, self.onSub)
        # self.chat.register_event(ChatEvent.WHISPER, self.onWhisper)

        self.chat.register_event(ChatEvent.NOTICE, self.on_notice)
        # Directly registered commands
        # self.chat.register_command('makeClip', self.onMakeClip)
        self.chat.register_command('isbotalive', self.on_check_alive)

        # self.chat.register_command('chatgpt', self.onMessageToChatGPT)
        # self.chat.register_command('lastseen', self.onGetLastSeen)

    async def run(self, settings: dict):
        await self.aconnect_dict(settings)
        self.chat.start()
        try:
            input('press ENTER to stop\n')
        finally:
            # now we can close the chatbot and the twitch api client
            self.chat.stop()
            await self.twitch.close()

    async def on_ready(self, ready_event: EventData):
        print("Bot is ready for work, joining channels")

        await ready_event.chat.join_room(self.target_channels)

    async def on_message(self, message_event: ChatMessage):
        print(f"Got message in {message_event.room.name} room : {message_event.text}")

    async def on_notice(self, notice_event: NoticeEvent):
        print(f"Got notice event: {notice_event.message} in {notice_event.room.name} room")

    async def on_check_alive(self, command: ChatCommand):
        print(f"Got check command from {command.user.name}")
        # if(command.user.id in self.superusers)
        await command.reply("Да живой я, живой")

    async def on_message_deleted(self):
        pass
