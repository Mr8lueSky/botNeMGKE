# -*- coding: utf-8 -*-
import os
import json
import vk_api
import sys
import threading
from time import ctime, sleep
from random import randint, choice
from urllib.request import Request, urlopen
import re
import time
import requests
import http.client


class Lock:
    _lock = False

    @staticmethod
    def lock(func, *args):
        if not (Lock._lock):
            _lock = threading.Lock()
        _lock.acquire()
        try:
            func(*args)
        finally:
            _lock.release()


class BotNeMGKE:
    class Commands:
        vk = ''
        basic_buttons = [[{"action": {"type": "text", "payload": "", "label": "звонки"}, "color": "positive"},
                        {"action": {"type": "text", "payload": "", "label": "звонки суббота"}, "color": "negative"}],
                       [{"action": {"type": "text", "payload": "", "label": "инфо"}, "color": "primary"}]]

        if os.path.exists('keyboard.json'):
            with open('keyboard.json', 'r', encoding='utf-8') as file:
                keyboards = json.load(file)
        else:
            with open('keyboard.json', 'w', encoding='utf-8') as file:
                keyboards = {}

        @staticmethod
        def __init__():
            BotNeMGKE.Commands.commands = {
                'инфо': BotNeMGKE.Commands.info,
                'подписаться': BotNeMGKE.Commands.mailing_new_user,
                'отписаться': BotNeMGKE.Commands.mailing_delete_user,
                'подписки': BotNeMGKE.Commands.mailing_get_sub,
                'репорт': BotNeMGKE.Commands.report,
                'дата': BotNeMGKE.Commands.schedule_send_by_day,
                'клавиатура': BotNeMGKE.Commands.keydoard_basic_buttons,
                'очистить': BotNeMGKE.Commands.keyboard_clear,
                'звонки': BotNeMGKE.Commands.time_table,
            }
            BotNeMGKE.Commands.admin_commands = {
                'json#': BotNeMGKE.Commands.json_send,
                'stopall#': BotNeMGKE.Commands.stop_all,
                'restart#': BotNeMGKE.Commands.restart,
                'mailing#': BotNeMGKE.Commands.mailing_all,
                'updatenemgke#': BotNeMGKE.Commands.update_nemgke,
                'updatedebug#': BotNeMGKE.Commands.update_debug,
                'undup#': BotNeMGKE.Commands.undup,
            }

        @staticmethod
        def undup(id, *args, **kwargs):
            with open('spamids.json', 'r', encoding='utf-8') as file:
                spamids = json.load(file)

            for id in spamids:
                spamids[id] = list(set(spamids[id]))

            with open('spamids.json', 'w', encoding='utf-8') as file:
                json.dump(spamids, file, ensure_ascii=False)
            BotNeMGKE.Vk.message_send('А ты не плох))', id)

        @staticmethod
        def update_nemgke(id, *args, **kwargs):
            BotNeMGKE.Vk.message_send('wait...', id)
            with open('update.txt', "wb") as file:
                response = requests.get(BotNeMGKE.Vk.message_get_by_id(
                    kwargs['message_id'])["items"][0]['attachments'][0]['doc']['url'])
                file.write(response.content)
            sys.exit(123)

        @staticmethod
        def update_debug(id, *args, **kwargs):
            BotNeMGKE.Vk.message_send('wait...', id)
            with open('updateDebug.txt', "wb") as file:
                response = requests.get(BotNeMGKE.Vk.message_get_by_id(
                    kwargs['message_id'])["items"][0]['attachments'][0]['doc']['url'])
                file.write(response.content)
            sys.exit(321)

        @staticmethod
        def restart(id, *args, **kwargs):
            BotNeMGKE.Vk.message_send('restart', id)
            sys.exit(0)

        @staticmethod
        def mailing_all(id, *args, **kwargs):
            groups = [group for group in BotNeMGKE.Schedule.schedule]
            BotNeMGKE.Commands.mailing_send_schedule(groups)

        @staticmethod
        def stop_all(id, *args, **kwargs):
            BotNeMGKE.Vk.message_send('TOKIO TOMORE', id)
            sys.exit(1488)

        @staticmethod
        def json_send(id, *args, **kwargs):
            url = BotNeMGKE.Vk.docs_get_upload_server()
            files = {'file': ('spamids.json', open('spamids.json', 'rb'), 'doc')}
            r = requests.post(url["upload_url"], files=files).json()
            ed = BotNeMGKE.Vk.docs_save(r['file'])
            BotNeMGKE.Vk.message_send(ed['doc']['url'], id, attachments=ed['type']+str(ed['doc']['owner_id'])+'_'+str(ed['doc']['id']))

        @staticmethod
        def keyboard_clear(id, *args, **kwargs):
            BotNeMGKE.Commands.keyboards[id][1].clear()
            BotNeMGKE.Vk.message_send('Очищено', id, BotNeMGKE.Commands.keyboard_groups(id))

        @staticmethod
        def keyboard_groups(id, group=None):
            # button_empty = {"action": {"type": "", "payload": "", "label": ""}, "color": ""}
            keyboard = {"one_time": True, "buttons": []}

            if not(id in BotNeMGKE.Commands.keyboards):
                BotNeMGKE.Commands.keyboards.update({id: [False, []]})

            if len(BotNeMGKE.Commands.keyboards[id][1]) == 4:
                BotNeMGKE.Commands.keyboards[id][1].pop(0)

            groups = [button['gr'] for button in BotNeMGKE.Commands.keyboards[id][1]]

            if not(group in groups) and not(group is None):
                BotNeMGKE.Commands.keyboards[id][1].append({'gr': group, 'color': choice(["positive", "negative",
                                                                                          "primary", "default"])})
            if not(group is None):
                keyboard['buttons'].append([])
                keyboard['buttons'][0] = [{"action": {"type": "text", "payload": "", "label": button['gr']},
                                           "color": button['color']} for button in BotNeMGKE.Commands.keyboards[id][1]]

            if BotNeMGKE.Commands.keyboards[id][0] is True:
                for button in BotNeMGKE.Commands.basic_buttons:
                    keyboard['buttons'].append(button)

            with open('keyboard.json', 'w', encoding='utf-8') as file:
                json.dump(BotNeMGKE.Commands.keyboards, file, ensure_ascii=False)

            return keyboard

        @staticmethod
        def keydoard_basic_buttons(id, *args, **kwargs):
            if not(id in BotNeMGKE.Commands.keyboards):
                BotNeMGKE.Commands.keyboards.update({id: [True, []]})
            if BotNeMGKE.Commands.keyboards[id][0] is True:
                BotNeMGKE.Commands.keyboards[id][0] = False
                BotNeMGKE.Vk.message_send('Клавиатура убрана!', id,
                                          {"one_time": True, "buttons": []})
            else:
                BotNeMGKE.Commands.keyboards[id][0] = True
                keyboard = {"one_time": True, "buttons": []}
                keyboard['buttons'].append([])
                keyboard['buttons'][0] = [{"action": {"type": "text", "payload": "", "label": button['gr']},
                                           "color": button['color']} for button in BotNeMGKE.Commands.keyboards[id][1]]
                if not keyboard['buttons'][0]:
                    keyboard['buttons'].pop(0)
                keyboard['buttons'] = [button for button in BotNeMGKE.Commands.basic_buttons]
                BotNeMGKE.Vk.message_send('Клавиатура!', id, keyboard)

            with open('keyboard.json', 'w', encoding='utf-8') as file:
                json.dump(BotNeMGKE.Commands.keyboards, file, ensure_ascii=False)

        @staticmethod
        def command_read(body, id, message_id):
            body_splited = body.lower().split()
            if not(body):
                BotNeMGKE.Commands.no_command(id)
            elif BotNeMGKE.Schedule.is_group_or_teacher(body):
                BotNeMGKE.Commands.schedule_send_day(body, id)
            elif body_splited[0] in BotNeMGKE.Schedule.weeks:
                BotNeMGKE.Commands.schedule_send_week(''.join(body_splited[1:]), id, body_splited[0])
            elif body_splited[0] in BotNeMGKE.Commands.commands:
                BotNeMGKE.Commands.commands[body_splited[0]](id, body_splited[1:], message_id=message_id)
            elif id in BotNeMGKE.Vk.IDs.adminids and body_splited[0] in BotNeMGKE.Commands.admin_commands:
                BotNeMGKE.Commands.admin_commands[body_splited[0]](id, body_splited[1:], message_id=message_id)
            else:
                BotNeMGKE.Commands.no_command(id)

        @staticmethod
        def schedule_send_day(group, id):
            schedule = BotNeMGKE.Schedule.get_schedule_day(group)
            if schedule:
                BotNeMGKE.Vk.message_send(schedule, id, keyboard=BotNeMGKE.Commands.keyboard_groups(id, group))
            else:
                BotNeMGKE.Vk.message_send("Такой группы/учителя нет в расписании или нет такой команды. Для просмотра всех доступных команд используйте 'инфо'", id)

        @staticmethod
        def schedule_send_by_day(id, *args, **kwargs):
            if len(args[0]) >= 2:
                date = args[0][0]
                group = args[0][1]
                if date[0] == '0':
                    date = date[1:]
                if date[date.find('.') + 1] == '0':
                    date = date[:date.find('.') + 1] + date[date.find('.') + 2:]
                date = "cache\\" + date.replace('.', '-') + '.json'
                if os.path.exists(date):
                    with open(date, 'r', encoding='utf-8') as file:
                        schedule = json.load(file)
                        if group in schedule:
                           BotNeMGKE.Vk.message_send(schedule[group], id)
                        else:
                            BotNeMGKE.Vk.message_send(
                                "Такой группы/учителя нет в расписании или вы ввели группу/фамилию неправильно.", id)
                else:
                    BotNeMGKE.Vk.message_send("Вы ввели неправильную дату или такой даты не было в расписании", id)
            else:
                BotNeMGKE.Vk.message_send("Вы не ввели группу или дату, или фамилию учителя, или всё вместе", id)


        @staticmethod
        def schedule_send_week(group, id, day):
            schedule = BotNeMGKE.Schedule.get_schedule_week(group, day)
            if schedule:
                BotNeMGKE.Vk.message_send(schedule, id)
            else:
                BotNeMGKE.Vk.message_send("Такой группы/учителя нет в расписании или нет такой команды. Для просмотра всех доступных команд используйте 'инфо'", id)

        @staticmethod
        def info(id, *args, **kwargs):
            full_information = [
                '№ - просмотр расписания для группы/учителя(вместо № - номер группы или фамилия учителя)',
                'репорт ... - связь с администрацией(вместо ... своё сообщение)',
                'звонки - расписание звонков. Для просмотра звонков на субботу введите дополнительно сб',
                'подписаться № - при подписке на обновление группы/учителя, расписание будет отправляться автоматически, при его обновлении на сайте. Если ввести команду несколько раз с несколькими группами/учителями, то вы будете подписаны на несколько групп/учителей(вместо № указать свою группу или фамилию учителя).',
                'отписаться № - отписывает вас от обновления расписания указанной группы/учителя, если группа/учитель не указан - отписывает от всех групп/учителей(вместо № указать свою группу или фамилию учителя).',
                'подписки - просмотр групп/учителей, на которыe вы подписались.',
                'клавиатура - включить/выключить клавиатуру.',
                'очистить - очистить историю групп/учителей в клавиатуре.',
                'дата ДД.ММ № - просмотр расписания группы/учителя на определённый день(ДД - день, ММ - месяц(число), № - номер группы или фамилия учителя).',
                'ДеньНедели № - просмотр предварительного расписания на определённый день недели (ДеньНедели - день недели, № - номер группы). Пример: суббота 299',
                'инфо - информация о всех командах.',
            ]
            admin_information = [
                'json# - отправка json',
                'stopall# - остановка всиго',
                'restart# - перезагрузка',
                'mailing# - отправка расписания всем',
                'update nemgke# - обновление основного бота',
                'update debug# - обновление дебагера',
                'undup# - удаление повторений групп и уч в спам айди з',
            ]
            full_information = '\n\n'.join([str(num + 1) + '). '+line for num, line in enumerate(full_information)])
            if id in BotNeMGKE.Vk.IDs.adminids:
                full_information += '\n\n' + '\n\n'.join(admin_information)
            BotNeMGKE.Vk.message_send(full_information, id)

        @staticmethod
        def no_command(id):
            text = "Такой группы/учителя нет в расписании или нет такой команды. Для просмотра всех доступных команд используйте 'инфо'"
            BotNeMGKE.Vk.message_send(text, id)

        @staticmethod
        def time_table(id, *args, **kwargs):
            day = ''.join(args[0])
            timetble = [
                'На корпусе Казинца:\n1 пара:\n9.00 - 9.45\n9.55 - 10.40\n2 пара:\n10.50 - 11.35\n11.45 – 12.30\n3 пара:\n13.15 –14.00\n14.10 – 14.55\n4 пара:\n15.05 – 15.50\n16.00 – 16.45\n\nНа корпусе Кнорина:\n1 пара:\n9.00 - 9.45\n9.55 - 10.40\n2 пара:\n11.00 - 11.45\n12.05 - 12.50\n3 пара:\n13.10 - 13.55\n14.05 - 14.50\n4 пара:\n15.00 - 15.45\n15.55 - 16.40',
                'На корпусе Казинца:\n1 пара:\n9.00 - 10.20\n2 пара:\n10.30 –11.15\n11.35 – 12.20\n3 пара:\n12.30- 13.50\n4 пара:\n14.00 – 15.20\n\nНа корпусе Кнорина:\n1 пара:\n9.00 - 10.20\n2 пара:\n10.40 - 11.25\n11.45 - 12.30\n3 пара:\n12.50 - 14.10\n4 пара:\n14.20 -  15.40']
            if 'с' in day.lower():
                BotNeMGKE.Vk.message_send(timetble[1], id)
            else:
                BotNeMGKE.Vk.message_send(timetble[0], id)

        @staticmethod
        def mailing_new_user(*args, **kwargs):
            id = args[0]
            if len(args[1]) < 1:
                BotNeMGKE.Vk.message_send('Вы не ввели группу', id)
                return False
            else:
                group = args[1][0]

            if BotNeMGKE.Schedule.is_group_or_teacher(group):
                with open('spamids.json', 'r', encoding='utf-8') as file:
                    spamids = json.load(file)
                if not(id in spamids):
                    spamids.update({id:[]})
                if group in spamids[id]:
                    BotNeMGKE.Vk.message_send('Вы уже подписаны на эту группу'.format(group), id)
                    return True
                else:
                    spamids[id].append(group)
                with open('spamids.json', 'w', encoding='utf-8') as file:
                    json.dump(spamids, file)

                BotNeMGKE.Vk.message_send('Вы подписались на {0} группу/учителя'.format(group), id)

            else:
                BotNeMGKE.Vk.message_send('Такой группы/учителя нету в расписании', id)
            return True

        @staticmethod
        def mailing_delete_user(*args, **kwargs):
            id = args[0]

            with open('spamids.json', 'r', encoding='utf-8') as file:
                spamids = json.load(file)

            if len(args[1]) < 1:
                spamids.update({id: []})
                BotNeMGKE.Vk.message_send('Вы отписались от всех групп/учителей', id)
            else:
                group = args[1][0]

                if not (id in spamids):
                    spamids.update({id: []})

                if group in spamids[id]:
                    spamids[id].remove(group)
                    with open('spamids.json', 'w', encoding='utf-8') as file:
                        json.dump(spamids, file)

                    BotNeMGKE.Vk.message_send('Вы отписались от {0} группы/учителя'.format(group), id)

                else:
                    BotNeMGKE.Vk.message_send('Вы не подписаны на эту группу/этого учителя', id)

            with open('spamids.json', 'w', encoding='utf-8') as file:
                json.dump(spamids, file)

            return True

        @staticmethod
        def mailing_get_sub(*args, **kwargs):
            id = args[0]
            with open('spamids.json', 'r', encoding='utf-8') as file:
                spamids = json.load(file)
            if not(id in spamids) or len(spamids[id]) == 0:
                BotNeMGKE.Vk.message_send('Вы не подписаны ни на что', id)
            else:
                BotNeMGKE.Vk.message_send('Вы подписаны на {0}'.format(', '.join(spamids[id]) + '.'), id)

        @staticmethod
        def report(id, message_id=None, *args):
            BotNeMGKE.Vk.message_send('', BotNeMGKE.Vk.IDs.adminids[0], forward_message=message_id)
            BotNeMGKE.Vk.message_send('ваш репорт отправлен', id)

        @staticmethod
        def mailing_send_schedule(groups=False):
            if not(groups):
                groups = BotNeMGKE.Schedule.difference()
            print('Рассылка - ', groups)
            BotNeMGKE.Vk.message_send('Рассылка {0}.'.format(', '.join(groups)), BotNeMGKE.Vk.IDs.adminids[0])
            with open('spamids.json', 'r') as file:
                spamids = json.load(file)

            for group in groups:
                for id in spamids:
                    if group in spamids[id]:
                        try:
                            sleep(0.1)
                            BotNeMGKE.Vk.message_send(BotNeMGKE.Schedule.get_schedule_day(group, with_group=True), id)
                        except Exception:
                            None
            BotNeMGKE.Vk.message_send('Завершена', BotNeMGKE.Vk.IDs.adminids[0])

    class Vk:
        vk = ''
        schedules = ''

        @staticmethod
        def Init():
            BotNeMGKE.Commands.vk = BotNeMGKE.Vk
            BotNeMGKE.Vk.vk = vk_api.VkApi(token=BotNeMGKE.Vk.IDs.test_token)
            BotNeMGKE.Vk.vk._auth_token()
            BotNeMGKE.Vk.schedules = BotNeMGKE.Schedule()
            BotNeMGKE.Vk.schedules.daemon = True
            BotNeMGKE.Commands.__init__()
            BotNeMGKE.Vk.schedules.start()
            conn = http.client.HTTPConnection("ifconfig.me")
            conn.request("GET", "/ip")
            BotNeMGKE.Vk.message_send('start NeMGKE ' + conn.getresponse().read().decode('utf-8'),
                                      BotNeMGKE.Vk.IDs.adminids[0])

        @staticmethod
        def message_get_by_id(id):
            response = BotNeMGKE.Vk.vk.method('messages.getById', {'message_ids': id})
            return response

        @staticmethod
        def docs_save(file):
            return BotNeMGKE.Vk.vk.method("docs.save", {"file": file})

        @staticmethod
        class IDs:
            token = "YOUR MAIN TOKEN"
            test_token = "YOUR TEST TOKEN"
            groupid = 176701645
            test_groupid = 175716286
            adminids = ['142747227', '266795811']

        @staticmethod
        def message_send(message=None, user_id=None, keyboard='', forward_message='', attachments=''):
            return BotNeMGKE.Vk.vk.method("messages.send",
                                  {"user_id": user_id, "message": message,
                                   'attachments': attachments,
                                   'forward_messages': forward_message,
                                   "keyboard": json.dumps(keyboard, ensure_ascii=False),
                                   "random_id": randint(0, 2147483647)})

        @staticmethod
        def docs_get_upload_server(type='doc'):
            return BotNeMGKE.Vk.vk.method("docs.getMessagesUploadServer", {"type": type,
                                                                           "peer_id": BotNeMGKE.Vk.IDs.adminids[0]})

        @staticmethod
        def get_conversation():
            response = {}
            messages = BotNeMGKE.Vk.vk.method("messages.getConversations", {"offset": 0, "count": 20,
                                                                            "filter": "unanswered"})
            if messages["count"] >= 1 and messages["items"][0]["last_message"]["from_id"] > 0:
                id = str(messages["items"][0]["last_message"]["from_id"])
                body = messages["items"][0]["last_message"]["text"].lower()
                message_id = messages["items"][0]["last_message"]['id']
                response.update({'id': id, 'body': body, 'message_id': message_id})
                return response
            else:
                return False

        @staticmethod
        def main_loop():
            while True:
                try:
                    sleep(0.5)
                    response = BotNeMGKE.Vk.get_conversation()
                    if response:
                        id = response['id']
                        body = response['body']
                        message_id = response['message_id']
                        Lock.lock(BotNeMGKE.Commands.command_read, body, id, message_id)
                except Exception as err:
                    print(err)

    def run(self):
        if os.path.exists("spamids.json"):
            with open("spamids.json", "r", encoding="utf-8") as file:
                spamids = json.load(file)
        else:
            with open("spamids.json", "w") as file:
                file.write('{}')
            spamids = {}

        if not (os.path.exists("logs")):
            os.makedirs('logs')

        if not (os.path.exists("logs\logsNeMgke.txt")):
            open("logs\logsNeMgke.txt", "w")

        if not (os.path.exists("cache")):
            os.makedirs('cache')
        BotNeMGKE.Vk.Init()
        BotNeMGKE.Vk.main_loop()


    class Schedule(threading.Thread):
        previous_schedule = {}
        schedule = {}
        schedule_week = {}
        weeks = ['понедельник', 'вторник', 'среда', 'четверг', 'пятница', 'суббота']


        @staticmethod
        def run():
            Lock.lock(BotNeMGKE.Schedule.load)
            Lock.lock(BotNeMGKE.Schedule.cache)
            while True:
                sleep(60 * 15)
                BotNeMGKE.Schedule.previous_schedule = BotNeMGKE.Schedule.schedule.copy()
                try:
                    Lock.lock(BotNeMGKE.Schedule.load)
                    Lock.lock(BotNeMGKE.Schedule.cache)
                except Exception:
                    None
                if BotNeMGKE.Schedule.previous_schedule != BotNeMGKE.Schedule.schedule:
                    Lock.lock(BotNeMGKE.Schedule.cache)
                    Lock.lock(BotNeMGKE.Commands.mailing_send_schedule)



        @staticmethod
        def get_schedule_day(group, with_group=False):
            schedule = [" ".join(sch.split()[:group.count(" ")+1]).lower() for sch in BotNeMGKE.Schedule.schedule]
            if group in schedule:
                send = list(BotNeMGKE.Schedule.schedule)[schedule.index(group)]
                if with_group:
                    return group +'\n\n' + BotNeMGKE.Schedule.schedule[send]
                else:
                    return BotNeMGKE.Schedule.schedule[send]
            else:
                return False

        @staticmethod
        def get_schedule_week(group, day):
            if group in BotNeMGKE.Schedule.schedule_week[day]:
                return BotNeMGKE.Schedule.schedule_week[day][group]
            else:
                return False

        @staticmethod
        def load():
            BotNeMGKE.Schedule.schedule = BotNeMGKE.Schedule._load_schedule().copy()
            BotNeMGKE.Schedule.schedule.update(BotNeMGKE.Schedule._load_schedule_teachers().copy())
            BotNeMGKE.Schedule.schedule_week = BotNeMGKE.Schedule._load_schedule_week().copy()
            if " " in BotNeMGKE.Schedule.schedule:
                BotNeMGKE.Schedule.schedule.pop(" ")


        @staticmethod
        def is_group_or_teacher(text):
            if text in [" ".join(group.split()[:len(text.split())]).lower() for group in BotNeMGKE.Schedule.schedule] \
                    and text:
                return True
            else:
                return False

        @staticmethod
        def _load_schedule():
            pages = urlopen(Request("http://mgke.minsk.edu.by/ru/main.aspx?guid=3831",
                                    headers={'User-Agent': 'Mozilla/5.0'})).read().decode("utf-8") + urlopen(
                Request("http://mgke.minsk.edu.by/ru/main.aspx?guid=3841",
                        headers={'User-Agent': 'Mozilla/5.0'})).read().decode("utf8")
            schedule = []
            schedule_dict = {}
            day = ""
            for i in range(pages.count('<table')):
                schedule.append([])
                for o in range(pages[:pages.find('</table>') + 8].count('<tr')):
                    schedule[i].append([])
                    for p in range(pages[:pages.find('</tr>') + 8].count('<td')):
                        schedule[i][o].append(pages[pages.find('<td'):pages.find('</td>')])
                        schedule[i][o][p] = schedule[i][o][p].replace('\r', '').replace('\n', '').replace('&nbsp;', '')
                        for l in range(schedule[i][o][p].count('<')):
                            schedule[i][o][p] = schedule[i][o][p][:schedule[i][o][p].find('<')] + schedule[i][o][p][
                                                                                                  schedule[i][o][
                                                                                                      p].find(
                                                                                                      '>') + 1:]
                        pages = pages[pages.find('</td>') + 5:]
                    pages = pages[pages.find('</tr>') + 5:]
                for num_string in range(1, len(schedule[i][1])):
                    try:
                        pair = 1
                        if schedule[i][0][0][:4] == "День":
                            info = schedule[i][0][0] + "\n\n"
                            day = info
                        else:
                            info = day
                        for string in schedule[i][3:]:
                            if string[num_string * 2 - 1]:
                                if string[0].isnumeric() and string[num_string * 2] != "":
                                    info += string[0] + " - " + string[num_string * 2 - 1] + " " + string[
                                        num_string * 2] + "\n\n"
                                elif string[num_string * 2 + 1] != "":
                                    info += str(pair) + " - " + string[num_string * 2] + " " + string[
                                        num_string * 2 + 1] + "\n\n"
                                    pair += 1
                    except Exception:
                        info += "Произошла ошибка из-за некорректно заполненой таблицы на сайте"
                    if not (schedule[i][1][num_string]): continue
                    if schedule[i][1][num_string] in schedule_dict:
                        schedule_dict[schedule[i][1][num_string]] += info + "\n"
                    else:
                        schedule_dict.update({schedule[i][1][num_string]: info + "\n"})
                pages = pages[pages.find('</table>') + 8:]

            # with open('schedule.json', 'r', encoding='utf-8') as file:
            #     return json.load(file)
            return schedule_dict

        @staticmethod
        def _load_schedule_teachers():
            pages = urlopen(Request("http://mgke.minsk.edu.by/ru/main.aspx?guid=3821",
                                    headers={'User-Agent': 'Mozilla/5.0'})).read().decode("utf-8")
            schedule = []
            schedule_dict = {}
            for i in range(pages.count('<table')):
                schedule.append([])
                for o in range(pages[:pages.find('</table>') + 8].count('<tr')):
                    schedule[i].append([])
                    for p in range(pages[:pages.find('</tr>') + 8].count('<td')):
                        schedule[i][o].append(pages[pages.find('<td'):pages.find('</td>')])
                        schedule[i][o][p] = schedule[i][o][p].replace('\r', '').replace('\n', '').replace('&nbsp;', '')
                        for l in range(schedule[i][o][p].count('<')):
                            schedule[i][o][p] = schedule[i][o][p][:schedule[i][o][p].find('<')] + schedule[i][o][p][
                                                                                                  schedule[i][o][
                                                                                                      p].find(
                                                                                                      '>') + 1:]
                        pages = pages[pages.find('</td>') + 5:]
                    pages = pages[pages.find('</tr>') + 5:]
                pages = pages[pages.find('</table>') + 8:]
            for table in schedule:
                for line in table[3:]:
                    line.pop(0)
                    info = line[0] + "\n\n" + table[0][2] + "\n\n"
                    for pair in range(1, 7):
                        if line[pair * 2 - 1]: info += str(pair) + " - " + line[pair * 2 - 1] + " " + line[
                            pair * 2] + "\n\n"
                    if not (line[0] in schedule_dict):
                        schedule_dict.update({line[0]: info})
                    else:
                        schedule_dict[line[0]] += info

            return schedule_dict

        @staticmethod
        def _load_schedule_week():
            html = urlopen(Request("http://mgke.minsk.edu.by/main.aspx?guid=3781",
                                   headers={'User-Agent': 'Mozilla/5.0'})).read().decode("utf-8") + urlopen(
                Request("http://mgke.minsk.edu.by/ru/main.aspx?guid=3791",
                        headers={'User-Agent': 'Mozilla/5.0'})).read().decode("utf8") + urlopen(
                Request("http://mgke.minsk.edu.by/ru/main.aspx?guid=3811",
                        headers={'User-Agent': 'Mozilla/5.0'})).read().decode("utf8")

            html = html[html.find('<div class="content">'):html.rfind('<div style="clear: both;"></div>')]

            schedule_week = {week: {} for week in BotNeMGKE.Schedule.weeks}

            for _ in range(html.count('<h2>')):
                group = html[html.find('<h2>') + 4:html.find('</h2>')]
                if 'Преподаватель' in group:
                    group = group.split(' - ')[1]
                else:
                    group = group.split()[-1]
                table = html[html.find('<tbody>') + 7:html.find('</tbody>')]
                lines = table.split('</tr>')
                first_line = [BotNeMGKE.Schedule.clean_html(cell) for cell in lines[0].split('</td>')][1:]
                schedule = [first_line[:-1]]
                for line in lines[2:]:
                    cells = [' '.join(BotNeMGKE.Schedule.clean_html(cell).split()) for cell in line.split('</td>')]
                    cells.pop(-1)
                    if cells:
                        schedule.append(cells)
                for count, day in enumerate(schedule[0]):
                    current_day = day.split(',')[0]
                    schedule_day = day + '\n\n'
                    for ind in range(len(schedule[1:])):
                        if schedule[ind + 1][count * 2 + 1]:
                            schedule_day += schedule[ind + 1][0] + " - " + schedule[ind + 1][count * 2 + 1] + \
                                            schedule[ind + 1][
                                                (count + 1) * 2] + '\n\n'
                    schedule_week[current_day.lower()].update({group: schedule_day})
                html = html[html.find('</table') + 7:]
            return schedule_week

        @staticmethod
        def load_from_file():
            with open('schedule.json', 'r', encoding='utf-8') as file:
                BotNeMGKE.Schedule.schedule = json.load(file)

        @staticmethod
        def clean_html(raw_html):
            cleanr = re.compile('<.*?>')
            cleantext = re.sub(cleanr, '', raw_html)
            return cleantext.replace('\r', '').replace('\n', '').replace('&nbsp;', '')

        @staticmethod
        def difference():
            groups = []
            for group in BotNeMGKE.Schedule.schedule:
                if not(group in BotNeMGKE.Schedule.previous_schedule) or \
                    (group in BotNeMGKE.Schedule.previous_schedule and \
                     BotNeMGKE.Schedule.previous_schedule[group] != BotNeMGKE.Schedule.schedule[group]):
                    groups.append(group)
            return groups

        @staticmethod
        def cache():
            with open('schedule.json', 'w', encoding='utf-8') as file:
                json.dump(BotNeMGKE.Schedule.schedule, file, ensure_ascii=False)
            week = ['Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница', 'Суббота', 'Воскресенье']
            now = time.localtime()
            last_date = str(now.tm_mday) + '-' + str(now.tm_mon)
            files = {}
            schedule_for_cache = BotNeMGKE.Schedule.schedule.copy()
            with open('schedule.json', 'r', encoding='utf-8') as file:
                schedule_for_cache = json.load(file)
            for group in schedule_for_cache:
                if not (group.isnumeric() or group[:-1].isnumeric()):
                    schedule_for_cache[group] = schedule_for_cache[group].replace(group + '\n\n', '')
                for line in schedule_for_cache[group].split('\n\n'):
                    for day in week:
                        if day in line:
                            last_date = '-'.join(line.split(', ')[-1].split('.')[:2])
                            if last_date[0] == '0': last_date = last_date[1:]
                            if last_date[last_date.find('-') + 1] == '0':
                                last_date = last_date[:last_date.find('-') + 1] + last_date[last_date.find('-') + 2:]
                    if not (last_date in files):
                        files.update({last_date: {}})
                    if not (group in files[last_date]):
                        files[last_date].update({group: ''})
                    files[last_date][group] += line + '\n\n'
            for file_name in files:
                with open('cache\\' + file_name + '.json', 'w', encoding='utf-8') as file:
                    json.dump(files[file_name], file, ensure_ascii=False)


def main():
    bot = BotNeMGKE()
    bot.run()


if __name__ == '__main__':
    main()