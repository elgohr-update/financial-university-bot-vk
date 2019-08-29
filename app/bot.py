import threading
import json

from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from app.models import User


def vk_bot_main(bot):
    """
    Запускает лонгпул и передает event в отдельном потоке

    :param bot:
    :return:
    """
    for event in bot.longpoll.listen():
        if event.type == VkBotEventType.MESSAGE_NEW:
            if event.from_user:
                flow = threading.Thread(target=vk_bot_from_user, args=(bot, event,))
                flow.start()
            elif event.from_chat:
                flow = threading.Thread(target=vk_bot_from_chat, args=(bot, event,))
                flow.start()
            else:
                print(event)


def vk_bot_from_user(bot, event):
    """
    Обработывает сообщения пользователей

    :param bot:
    :param event:
    :return:
    """

    user = User.search_user(event.obj.peer_id)
    payload = json.loads(getattr(event.obj, 'payload', '{}')) if 'payload' in event.obj else {}
    message = event.obj.text
    message_lower = message.lower()

    if message_lower == ("начать" or "start" or "сброс"):
        bot.send_main_menu(user)

    elif "menu" in payload:
        menu = payload["menu"]
        if menu == "main":
            bot.send_main_menu(user)
        elif menu == "schedule":
            bot.send_schedule_menu(user)
        elif menu == "schedule_today":
            bot.send_schedule(user, days=1)
        elif menu == "schedule_tomorrow":
            bot.send_schedule(user, start_day=1, days=1)
        elif menu == "schedule_today_and_tomorrow":
            bot.send_schedule(user, days=2)
        elif menu == "schedule_this_week":
            bot.send_schedule(user, days=7)
        elif menu == "schedule_next_week":
            bot.send_schedule(user, start_day=7, days=7)
        elif menu == "search_teacher":
            bot.send_search_teacher(user)
        elif menu == "teachers":
            bot.send_teacher(user, payload)
        elif menu == "teacher_schedule_today":
            bot.send_teacher_schedule(user, days=1)
        elif menu == "teacher_schedule_tomorrow":
            bot.send_teacher_schedule(user, start_day=1, days=1)
        elif menu == "teacher_schedule_today_and_tomorrow":
            bot.send_teacher_schedule(user, days=2)
        elif menu == "teacher_schedule_this_week":
            bot.send_teacher_schedule(user, days=7)
        elif menu == "teacher_schedule_next_week":
            bot.send_teacher_schedule(user, start_day=7, days=7)
        elif menu == "settings":
            bot.send_settings_menu(user)
        elif menu == "change_group":
            bot.send_choice_group(user)
        elif menu == "subscribe_to_newsletter":
            bot.subscribe_schedule(user)
        elif menu == "unsubscribe_to_newsletter":
            bot.unsubscribe_schedule(user)
        elif menu in ("subscribe_to_newsletter_today", "subscribe_to_newsletter_tomorrow",
                      "subscribe_to_newsletter_today_and_tomorrow", "subscribe_to_newsletter_this_week",
                      "subscribe_to_newsletter_next_week"):
            bot.update_subscribe_day(user, menu)

    elif "menu" not in payload:
        if user.group_name == "CHANGES":
            bot.send_check_group(user, message_lower)
        if user.found_teacher_name == "CHANGES" and user.found_teacher_id == "CHANGES":
            bot.search_teacher_schedule(user, message_lower)
        if user.subscription_days == "CHANGES":
            bot.update_subscribe_time(user, message_lower)


def vk_bot_from_chat(bot, event):
    """
    Обработка сообщений в беседах

    :param bot:
    :param event:
    :return:
    """

    print(f"Сообщение в беседе {event.chat_id}")
    # TODO Дописать функцианал для бесед
