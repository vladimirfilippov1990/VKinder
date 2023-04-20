import vk_api
from vk_api.utils import get_random_id

import Vkinder_db
import datetime


def send_message(vk, id_user, message_text):
    """
    Отправка сообщения пользователю
    Входные параметры:
    vk - Объект подключения к VkApi
    id_user - id пользователя
    message_text - текст отправляемого сообщения
    """
    vk.method('messages.send', 
                {'user_id': id_user, 
                 'message': message_text, 
                 'random_id': get_random_id()})


def send_message_with_photos(vk, id_user, message_text, attachments):
    """
    Отправка сообщения c фотографиями пользователю 
    Входные параметры:
    vk - Объект подключения к VkApi
    id_user - id пользователя
    message_text - текст отправляемого сообщения
    attachments - массив приложений
    """
    attachments = ",".join(attachments)
    vk.method('messages.send', 
                {'user_id': id_user, 
                 'message': message_text, 
                 'random_id': get_random_id(),
                 'attachment': attachments})



def find_city(vk, input_city):
    cities = vk.method('database.getCities', {'q': input_city})
    output = ''
    if cities['count'] != 0:
        cities = cities['items']
        for city in cities:
            cid = city.get('id')
            title = city.get('title')
            area = city.get('area')
            region = city.get('region')
            country = city.get('country')
            title = "" if title == None else title
            area = "" if area == None else area
            region = "" if region == None else region
            country = "" if country == None else country
            output += f"{cid} {title} {area} {region} {country}\n"
        return output
    else:
        return None

def get_city_by_id(vk, cid):
    cities = vk.method('database.getCitiesById', {'city_ids': cid})
    cities = cities[0]
    return cities.get('title')

def set_city(vk, id_user, message: str):
    if message.isdigit():
        city = get_city_by_id(vk, message)
        if city:
            Vkinder_db.update_user_city(id_user, message)
            Vkinder_db.update_user_position(id_user, 2)
            send_message(vk, 
                id_user, 
                f"Для поиска установлен город {city}.\nВведите возраст для поиска.")
        else:
            send_message(vk, 
                id_user, 
                "Нет города с таким id.")
    else:
        cities = find_city(vk, message)
        if cities:
            send_message(vk, 
                id_user, 
                f"Введите id города из списка:\n{cities}.") 
        else:
            send_message(vk, 
                id_user, 
                f"Ничего не найдено по запросу {message}.\nВведите название города") 


def set_age(vk, id_user, message_text:str):
    if message_text.isdigit():
        Vkinder_db.update_user_age(id_user, message_text)
        Vkinder_db.update_user_position(id_user, 3)
        send_message(vk, 
            id_user, 
            f"Для поиска установлен возраст {message_text}.\nУкажите пол: [М]ужской или [Ж]енский.")
    else:
        send_message(vk, 
            id_user, 
            f"Вы ввели не число. Введите целое число лет.")


def set_gender(vk, id_user, message_text:str):
    gender = message_text[0].upper()
    if gender in ['Ж', 'F']:
        gender = 1    
    elif gender in ['М', 'M']:
        gender = 2
    else:
        send_message(vk, 
            id_user, 
            f"Укажите пол: [М]ужской или [Ж]енский.")
        return -1 
    Vkinder_db.update_user_gender(id_user, gender)
    Vkinder_db.update_user_position(id_user, 4)
    send_message(vk, 
        id_user, 
        f"""Для поиска установлен возраст {message_text}.
        Введите семейное положение:
        [1] Не женат (не замужем)
        [2] Встречается
        [3] Помолвлен(-а)
        [4] Женат (замужем)
        [5] Все сложно
        [6] В активном поиске
        [7] Влюблен(-а)
        [8] В гражданском браке""")    


def set_family(vk, id_user, message_text:str):
    if len(message_text) == 1 and '1' <= message_text <= '8':
        Vkinder_db.update_user_family(id_user, message_text)
        Vkinder_db.update_user_position(id_user, 5)
        send_message(vk, 
            id_user, 
            "Для поиска введите [П]оиск") 
    else:
        send_message(vk, 
            id_user, 
            """Введите семейное положение:
            [1] Не женат (не замужем)
            [2] Встречается
            [3] Помолвлен(-а)
            [4] Женат (замужем)
            [5] Все сложно
            [6] В активном поиске
            [7] Влюблен(-а)
            [8] В гражданском браке""") 


def create_partners_list(vk, id_user):
    city, gender, age, family = Vkinder_db.get_user_settings(id_user)
    age_from = age - 2 if age > 20 else 18
    age_to = age + 2
    partners = vk.method('users.search', 
                            {'count': 1000, 
                             'city_id': city, 
                             'sex': gender,
                             'status': family,
                             'age_from': age_from,
                             'age_to': age_to})
    partners = partners ['items']
    for partner in partners:
        uid = partner['id']
        firstname = partner['first_name']
        lastname = partner['last_name']
        closed = partner['is_closed']
        if not closed:
            Vkinder_db.insert_partners([id_user, uid, firstname, lastname])
    Vkinder_db.update_user_position(id_user, 6)
    get_new_partner(vk, id_user)


def get_top_photos(vk, user_id):
    photos = vk.method('photos.getAll', 
                            {'owner_id': user_id, 
                             'extended': True})
    photos = photos['items']
    photos_list = []
    for photo in photos:
        photo_id = f"photo{user_id}_{photo['id']}"
        likes = photo['likes']['count']
        photos_list.append([photo_id, likes])
    photos_list = sorted(photos_list, key=lambda x: x[1], reverse=True)
    if len(photos_list)  <= 3:
        return photos_list
    return photos_list[:3]


def get_new_partner(vk, id_user):
    partner = Vkinder_db.get_user_from_db(id_user)
    if partner:
        id_partner, firstname, lastname = partner
        Vkinder_db.delete_candidate(id_user, id_partner)
        message = f"""{firstname} {lastname}
        vk.com/id{id_partner}
        Чтобы изменить настройки поиска введите [И]зменить
        Чтобы найти нового человека введите любое сообщение"""
        photos = get_top_photos(vk, id_partner)
        photos = [i[0] for i in photos]
        send_message_with_photos(vk, id_user, message, photos)


def processing_message(vk, id_user, message_text):
    number_position = Vkinder_db.take_position(id_user)
    
    if number_position == 1:
        set_city(vk, id_user, message_text)
    elif number_position == 2:
        set_age(vk, id_user, message_text)
    elif number_position == 3:
        set_gender(vk, id_user, message_text)
    elif number_position == 4:
        set_family(vk, id_user, message_text)
    elif number_position == 5:
        create_partners_list(vk, id_user)
    elif number_position == 6:
        if message_text[0].upper() == "И":
            Vkinder_db.update_user_position(id_user, 1)
            Vkinder_db.delete_candidates(id_user)
            set_city(vk, id_user, message_text)
        else:
            get_new_partner(vk, id_user)
