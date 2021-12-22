import json
from channels.generic.websocket import AsyncWebsocketConsumer
from django.utils import timezone

class ChatConsumer(AsyncWebsocketConsumer):
    '''Basic WebSocket Consumer.'''
    async def connect(self):
        '''Called when a new connection is received.'''
        # retrieve user info
        self.user = self.scope['user']
        # retrieve course id
        self.id = self.scope['url_route']['kwargs']['course_id']
        # build the group name
        self.room_group_name = 'chat_%s' % self.id
        # join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        # accept connection
        await self.accept()
    
    async def disconnect(self, close_code):
        '''Called when the socket closed.'''
        # leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        '''Returns the received message to the WebSocket client.

        Arguments include text_data, which expects either text or binary
        (json) data. The json data is deserialized into a 
        dictionary through json.loads. The message key is accessed from 
        the dictionary, serialized to json, and then returned/sent.
        '''
        # receive messages from websocket
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        now = timezone.now()
        # send message to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message':message,
                'user': self.user.username,
                'datetime': now.isoformat(),
            }
        )
    
    async def chat_message(self, event):
        '''Receive messages from the group.'''
        # Send message to WebSocket
        await self.send(text_data=json.dumps(event))