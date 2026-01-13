from channels.generic.websocket import AsyncWebsocketConsumer
import json

class RobotConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        self.robo_id = self.scope['url_route']['kwargs']['robo_id']
        self.group_name = f"robot_{self.robo_id}"

        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )

        await self.accept()

        await self.send(text_data=json.dumps({
            "status": "connected",
            "robo_id": self.robo_id
        }))

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        data = json.loads(text_data)

        # Broadcast only to this robot group
        await self.channel_layer.group_send(
            self.group_name,
            {
                "type": "robot.message",
                "message": data
            }
        )

    async def robot_message(self, event):
        await self.send(text_data=json.dumps(event["message"]))
