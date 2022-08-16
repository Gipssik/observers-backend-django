import json

from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
from django.contrib.auth.models import AnonymousUser


class ChatConsumer(WebsocketConsumer):
    """Websocket chat consumer."""

    DEFAULT_GROUP = "chat"

    def connect(self):
        """Executes on websocket connection.

        :return: None.
        """
        current_user = self.scope.get("user")
        if not current_user or isinstance(current_user, AnonymousUser):
            self.close()
            return
        self.accept()
        async_to_sync(self.channel_layer.group_add)(
            self.DEFAULT_GROUP,
            self.channel_name,
        )

        response = {
            "user": current_user.username,
            "message": "connected to the chat",
            "connection": True,
        }
        message_data = {
            "type": "chat.message",
            "message": response,
        }
        async_to_sync(self.channel_layer.group_send)(
            self.DEFAULT_GROUP,
            message_data,
        )

    def receive(self, text_data: str | None = None, bytes_data: bytes | None = None):
        """Executes on message receive.

        :param text_data: Text data from message.
        :param bytes_data: Bytes data from message.
        :return:
        """
        data = text_data or bytes_data.decode("utf-8")
        data = json.loads(data)
        message_data = {
            "type": "chat.message",
            "message": data,
        }
        async_to_sync(self.channel_layer.group_send)(self.DEFAULT_GROUP, message_data)

    def chat_message(self, event: dict):
        """Executes on event type 'chat.message'.

        :param event: Websocket message. Contains event type and message.
        :return: None.
        """
        message = json.dumps(event.get("message"))
        self.send(message)

    def disconnect(self, code: int):
        """Executes on websocket disconnect.

        :param code: Status code.
        :return: None
        """
        current_user = self.scope.get("user")
        response = {
            "user": current_user.username,
            "message": "left the chat",
            "connection": True,
        }
        message_data = {
            "type": "chat.message",
            "message": response,
        }
        async_to_sync(self.channel_layer.group_send)(self.DEFAULT_GROUP, message_data)
        async_to_sync(self.channel_layer.group_discard)(
            self.DEFAULT_GROUP,
            self.channel_name,
        )
