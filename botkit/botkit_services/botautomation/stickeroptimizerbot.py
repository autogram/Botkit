# class StickerOptimizerBot(BotAutomationBase):
#     __username__ = '@NewStickerOptimizerBot'
#
#     @dataclass
#     class State(object):
#         optimized_sticker: Message = None
#
#     state: State = State()
#
#     async def convert_image(self, message: Message):
#         photo = photo_from_message(message, raise_=True)
#
#         wait_event = self.conversation.wait_event(
#             NewMessage(incoming=True, chats=[self.__username__]),
#         )
#         await self.conversation.send_file(photo)
#
#         response: NewMessage.Event = await wait_event
#
#         if not is_media_event(response):
#             raise UnexpectedBehaviorException(f"Unexpected error: No media returned by {self.username}.")
#
#         self.state.optimized_sticker = response.message
