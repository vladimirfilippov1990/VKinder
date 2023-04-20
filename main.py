from random import randrange

import vk_api
import cfg
from vk_api.longpoll import VkLongPoll, VkEventType

import vk_bot

import threading

vk = vk_api.VkApi(login=cfg.login, password=cfg.password, token=cfg.token)

longpoll = VkLongPoll(vk)

def write_msg(user_id, message):
    vk.method('messages.send', {'user_id': user_id, 'message': message, 'random_id': randrange(10 ** 7),})

for event in longpoll.listen():
    if event.type == VkEventType.MESSAGE_NEW:
        if event.to_me:
            request = event.text
            threading.Thread(target=vk_bot.processing_message, args=(vk, event.user_id, request)).start()
            
