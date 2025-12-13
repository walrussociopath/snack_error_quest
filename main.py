from dataclasses import dataclass
from time import sleep

from telebot import TeleBot
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup


API_TOKEN = '8416137790:AAHV1KcRZhc-z5Vew6_s1KTY_BeRHC3soBw'

bot = TeleBot(API_TOKEN)

IS_PROD = False


@dataclass
class UserStorage:
    # Kolyan and Lexa Story
    kolyan_and_lexa_progress: str = 'unstarted'
    kolyan_and_lexa_last_callback: str = ''
    pudge_picked: bool = False
    techies_picked: bool = False
    first_dota_play_pick: bool = True
    mask_off: bool = False
    dress_off: bool = False
    # Sanya Story
    sanya_progress: str = 'unstarted'
    sanya_last_callback: str = ''
    sanya_conday: bool = True
    sanya_dogs: bool = True
    sanya_hungry: bool = True
    # Vano Story
    vano_progress: str = 'unstarted'
    vano_last_callback: str = ''
    vano_lights = False
    vano_pine = False
    vano_fire = False
    vano_balls = False
    # Den Story
    den_progress: str = 'unstarted'
    den_last_callback: str = ''
    den_available: bool = False
    den_gym_up: bool = False
    den_gym_bass: bool = False
    den_voice_available: bool = False
    # Murad Story
    murad_progress: str = 'unstarted'
    murad_last_callback: str = ''
    murad_locker: bool = False
    murad_axe: bool = False
    murad_tape: bool = False
    murad_stet: bool = False
    murad_rod: bool = False
    murad_seif: bool = False
    murad_aqua: bool = False
    murad_player: bool = False
    # Together Story
    together_progress: str = 'unstarted'
    together_callback: str = ''
    together_available: bool = False
    ending_spells_car: bool = True
    ending_spells_nails: bool = True
    ending_spells_metal: bool = True
    ending_spells_scream: bool = True
    ending_spells_rap: bool = True
    ending_spells_bass: bool = True
    ending_spells_beer: bool = True
    ending_spells_drums: bool = True

    def reset(self, branch):
        if branch == 'kolyan_and_lexa':
            self.kolyan_and_lexa_progress = 'unstarted'
            self.kolyan_and_lexa_last_callback = ''
            self.pudge_picked = False
            self.techies_picked = False
            self.first_dota_play_pick = True
            self.mask_off = False
            self.dress_off = False
        if branch == 'sanya':
            self.sanya_progress: str = 'unstarted'
            self.sanya_last_callback: str = ''
            self.sanya_conday: bool = True
            self.sanya_dogs: bool = True
            self.sanya_hungry: bool = True
        if branch == 'vano':
            self.vano_progress: str = 'unstarted'
            self.vano_last_callback: str = ''
            self.vano_lights = False
            self.vano_pine = False
            self.vano_fire = False
            self.vano_balls = False
        if branch == 'murad':
            self.murad_progress: str = 'unstarted'
            self.murad_last_callback: str = ''
            self.murad_locker: bool = False
            self.murad_axe: bool = False
            self.murad_tape: bool = False
            self.murad_stet: bool = False
            self.murad_rod: bool = False
            self.murad_seif: bool = False
            self.murad_aqua: bool = False
            self.murad_player: bool = False
        if branch == 'den':
            self.den_progress: str = 'unstarted'
            self.den_last_callback: str = ''
            self.den_gym_up: bool = False
            self.den_gym_bass: bool = False
            self.den_voice_available: bool = False
        if branch == 'together':
            self.together_progress: str = 'unstarted'
            self.together_callback: str = ''
            self.together_available: bool = False
            self.ending_spells_car: bool = True
            self.ending_spells_nails: bool = True
            self.ending_spells_metal: bool = True
            self.ending_spells_scream: bool = True
            self.ending_spells_rap: bool = True
            self.ending_spells_bass: bool = True
            self.ending_spells_beer: bool = True
            self.ending_spells_drums: bool = True

    def reset_all(self):
        for branch in ['kolyan_and_lexa', 'sanya', 'murad', 'den', 'vano', 'together']:
            self.reset(branch)
        self.den_available = False

    def is_together_available(self):
        self.together_available = all(
            map(
                lambda story: story == 'finished',
                [self.kolyan_and_lexa_progress, self.sanya_progress, self.murad_progress, self.den_progress,
                 self.vano_progress]
            )
        )
        return self.together_available


storage = {}


def save_last_callback_and_step(branch, callback, step):
    if branch == 'kolyan_and_lexa':
        storage[callback.message.chat.id].kolyan_and_lexa_last_callback = callback
        storage[callback.message.chat.id].kolyan_and_lexa_last_progress = step
    if branch == 'sanya':
        storage[callback.message.chat.id].sanya_last_callback = callback
        storage[callback.message.chat.id].sanya_last_progress = step
    if branch == 'vano':
        storage[callback.message.chat.id].vano_last_callback = callback
        storage[callback.message.chat.id].vano_last_progress = step
    if branch == 'den':
        storage[callback.message.chat.id].den_last_callback = callback
        storage[callback.message.chat.id].den_last_progress = step
    if branch == 'murad':
        storage[callback.message.chat.id].murad_last_callback = callback
        storage[callback.message.chat.id].murad_last_progress = step
    if branch == 'together':
        storage[callback.message.chat.id].together_last_callback = callback
        storage[callback.message.chat.id].together_last_progress = step


def progress(story, step):
    def _save_progress(f):
        def inner(callback):
            if story not in ['kolyan_and_lexa', 'sanya', 'vano', 'den', 'murad', 'together']:
                bot.send_message(
                    chat_id=callback.message.chat.id,
                    text='ERROR story not in STORY_LIST'
                )
            all_steps = kolyan_and_lexa_steps | sanya_steps | vano_steps | den_steps | murad_steps | together_steps
            if step not in all_steps:
                bot.send_message(
                    chat_id=callback.message.chat.id,
                    text='ERROR step not in '
                )
            save_last_callback_and_step(story, callback, step)
            f(callback)

        return inner

    return _save_progress


def get_stories_list(message, handel):
    if message.chat.id not in storage:
        storage[message.chat.id] = UserStorage()
    stories_list = ['vano', 'murad', 'kolyan_and_lexa', 'sanya']
    name_list = ['Вано', 'Мурад', 'Колян и Лёха', 'Саня']
    if storage[message.chat.id].den_available:
        stories_list.append('den')
        name_list.append('Денчик')
    if storage[message.chat.id].together_available:
        stories_list.append('together')
        name_list.append('Ошибка Снека')
    text = ''
    for story, name in zip(stories_list, name_list):
        text += f'/{handel}_{story} — {name}\n'
    return text


@bot.message_handler(commands=['start'])
def start(message):
    plays_text = get_stories_list(message, 'play')
    text = ('Ошибка Снека готовится к концерту 3-го января. Помоги парням подготовиться и огненно выступить!\n'
            'Начни проходить историю за одного из участников группы Ошибка Снека:\n')
    bot.send_message(
        chat_id=message.chat.id,
        text=text + plays_text + 'Больше информации: /help'
    )


@bot.message_handler(commands=['help'])
def help(message):
    plays_text = get_stories_list(message, 'play')
    reset_stories = get_stories_list(message, 'reset')
    text_stories = 'Начни или продолжи прохождение сюжетных веток:\n'
    text_reset = 'Или сбрось прогресс историй и начни заново:\n'
    bot.send_message(
        chat_id=message.chat.id,
        text=text_stories + plays_text + text_reset + reset_stories + '/reset_all — Сбросить всё\n'
                                                                      'Если нашли баг, пишите @walrussociopath'
    )


@bot.message_handler(commands=['reset_all'])
def reset_all(message):
    storage[message.chat.id].reset_all()
    bot.send_message(
        chat_id=message.chat.id,
        text='Весь игровой прогресс удалён'
    )


@bot.message_handler(commands=['reset_kolyan_and_lexa'])
def reset_kolyan_and_lexa(message):
    storage[message.chat.id].reset('kolyan_and_lexa')
    bot.send_message(
        chat_id=message.chat.id,
        text='Игровой прогресс ветки Колян и Лёха удалён'
    )


@bot.message_handler(commands=['reset_sanya'])
def reset_sanya(message):
    storage[message.chat.id].reset('sanya')
    bot.send_message(
        chat_id=message.chat.id,
        text='Игровой прогресс ветки Саня удалён'
    )


@bot.message_handler(commands=['reset_vano'])
def reset_vano(message):
    storage[message.chat.id].reset('vano')
    bot.send_message(
        chat_id=message.chat.id,
        text='Игровой прогресс ветки Вано удалён'
    )


@bot.message_handler(commands=['reset_murad'])
def reset_murad(message):
    storage[message.chat.id].reset('murad')
    bot.send_message(
        chat_id=message.chat.id,
        text='Игровой прогресс ветки Мурад удалён'
    )


@bot.message_handler(commands=['reset_den'])
def reset_den(message):
    storage[message.chat.id].reset('den')
    bot.send_message(
        chat_id=message.chat.id,
        text='Игровой прогресс ветки Ден удалён'
    )


@bot.message_handler(commands=['reset_together'])
def reset_together(message):
    storage[message.chat.id].reset('together')
    bot.send_message(
        chat_id=message.chat.id,
        text='Игровой прогресс ветки Ошибка Снека удалён'
    )


@bot.message_handler(commands=['play_kolyan_and_lexa'])
def play_kolyan_and_lexa(message):
    local_storage = storage[message.chat.id]

    # Restore progress
    if local_storage.kolyan_and_lexa_progress != 'unstarted':
        kolyan_and_lexa_steps[local_storage.kolyan_and_lexa_progress](
            local_storage.kolyan_and_lexa_last_callback
        )

    # Or start new game
    else:
        bot.send_message(
            chat_id=message.chat.id,
            text='Вы начали игру за Коляна и Лёху\nВам доступны способности:\n*«Крик»*\n*«Навалить репчика»*',
            parse_mode='Markdown'
        )
        if IS_PROD:
            sleep(3)
        keyboard = InlineKeyboardMarkup()
        keyboard.row(InlineKeyboardButton(text='Поиграть в Доту', callback_data='yes_play_dota'))
        keyboard.row(InlineKeyboardButton(text='Порепетировать перед концертом', callback_data='no_play_dota'))
        bot.send_message(
            chat_id=message.chat.id,
            text='Скоро концерт и фронтмены уже собраны. Но выезжать ещё рано.'
                 ' Есть ещё время, как раз хватит на катку в Доту',
            reply_markup=keyboard,
            parse_mode='Markdown'
        )


@bot.message_handler(commands=['play_vano'])
def play_vano(message):
    local_storage = storage[message.chat.id]

    # Restore progress
    if local_storage.vano_progress != 'unstarted':
        vano_steps[local_storage.vano_progress](
            local_storage.vano_last_callback
        )

    # Or start new game
    else:
        bot.send_message(
            chat_id=message.chat.id,
            text='Вы начали игру за Вано. Доступные способенности:\n*«Гвозди»*\n*«Металлическая стружка»*',
            parse_mode='Markdown'
        )
        if IS_PROD:
            sleep(3)
        keyboard = InlineKeyboardMarkup()
        keyboard.row(InlineKeyboardButton(text='«Гвозди»', callback_data='nails_salad'))
        keyboard.row(InlineKeyboardButton(text='«Металлическая стружка»', callback_data='metal_salad'))
        bot.send_message(
            chat_id=message.chat.id,
            text='Новый год на дворе и вы продолжаете делать всевозможные салаты. '
                 'На этот раз вам нужно натереть сыр',
            reply_markup=keyboard,
            parse_mode='Markdown'
        )


@bot.callback_query_handler(func=lambda call: call.data.endswith('_salad'))
@progress(story='vano', step='salad')
def salad(callback):
    if callback.data.startswith('nails'):
        keyboard = InlineKeyboardMarkup()
        keyboard.add(InlineKeyboardButton(text='«Металлическая стружка»', callback_data='metal_salad'))
        bot.send_message(
            chat_id=callback.message.chat.id,
            text="Какие гвозди? Давай стружку!",
            reply_markup=keyboard,
            parse_mode='Markdown'
        )
    if callback.data.startswith('metal'):
        bot.send_message(
            chat_id=callback.message.chat.id,
            text='Круто! Сделали салатик!'
        )
        keyboard = InlineKeyboardMarkup()
        keyboard.row(InlineKeyboardButton(text='Причинить боль', callback_data='pain_stone'))
        keyboard.row(InlineKeyboardButton(text='«Гвозди»', callback_data='nails_stone'))
        bot.send_message(
            chat_id=callback.message.chat.id,
            text='Ты достаёшь майонез из холодильника.'
                 ' Но вдруг появляется камень, который мешает продолжению этого сюжета',
            reply_markup=keyboard,
            parse_mode='Markdown'
        )


@bot.callback_query_handler(func=lambda call: call.data.endswith('_stone'))
@progress(story='vano', step='stone')
def stone(callback):
    if callback.data.startswith('pain'):
        keyboard = InlineKeyboardMarkup()
        keyboard.add(InlineKeyboardButton(text='«Гвозди»', callback_data='nails_stone'))
        bot.send_message(
            chat_id=callback.message.chat.id,
            text='Камень не может болеть! Попытка не удалась. Try again!',
            reply_markup=keyboard,
            parse_mode='Markdown'
        )
    if callback.data.startswith('nails'):
        bot.send_message(
            chat_id=callback.message.chat.id,
            text='Гвозди уверенно входят в камень. Под натиском рубилова камень раскалывается пополам'
        )
        if IS_PROD:
            sleep(5)
        bot.send_message(
            chat_id=callback.message.chat.id,
            text='Окей. Все салатики успешно замайонежены, но хочется большего. Хочется сахара, хочется энергии. '
                 'Хочется шоколадки!'
        )
        if IS_PROD:
            sleep(2)
        keyboard = InlineKeyboardMarkup()
        keyboard.row(InlineKeyboardButton(text='Сдаться', callback_data='no_snack'))
        keyboard.row(InlineKeyboardButton(text='ДАЙ МНЕ ШОКОЛАДКУ!', callback_data='yes_snack'))
        bot.send_message(
            chat_id=callback.message.chat.id,
            text='Ты доходишь до ближайшего магазина, где есть вендинговый аппарат. Выбираешь нужную шоколадку...\n'
                 'Но вдруг засада! Шоколадка застряла...',
            reply_markup=keyboard,
            parse_mode='Markdown'
        )


@bot.callback_query_handler(func=lambda call: call.data.endswith('_snack'))
@progress(story='vano', step='snack')
def snack(callback):
    if callback.data.startswith('yes'):
        bot.send_message(
            chat_id=callback.message.chat.id,
            text='Аппарат трепещет перед величайшими строками современности. Шоколадка падает, и ты её съедаешь'
        )
    if callback.data.startswith('no'):
        bot.send_message(
            chat_id=callback.message.chat.id,
            text='Ты уже готов уйти, но какое-то новогоднее чудо заставляет снек упасть. '
                 'Ты берёшь его и с удовольствием съедаешь'
        )
    if IS_PROD:
        sleep(3)
    bot.send_message(
        chat_id=callback.message.chat.id,
        text='Ты возвращаешься домой, ведь нужно настроиться на заряженную атмосферу перед концертом'
    )
    callback.data = 'start_new_year'
    new_year(callback)


@bot.callback_query_handler(func=lambda call: call.data.endswith('_new_year'))
@progress(story='vano', step='new_year')
def new_year(callback):
    local_storage = storage[callback.message.chat.id]
    text = 'Что-то пошло не так'
    if callback.data.startswith('lights'):
        text = ('Горят гирлянды, мы будем танцевать\n'
                'С ночи до утра, мы будет танцевать\n'
                'Горят гирлянды, мы будем не одни\n'
                'Прошедшего года непотухщие огни')
        local_storage.vano_lights = True
    if callback.data.startswith('pine'):
        text = ('Зажжётся ёлочка, мороз щекочет нос\n'
                'С весёлыми глазами, весёлый Дед мороз\n'
                'Зажжётся ёлочка веселые огни\n'
                'Сегодня ночью мы будем не одни\n')
        local_storage.vano_pine = True
    if callback.data.startswith('fire'):
        text = ('А в зимнем небе цветастый фейерверк\n'
                'И запах мандарина, бумажки на столе\n'
                'А в зимнем небе кружит волшебный снег\n'
                'Пройдёт немного, мы станем горячей')
        local_storage.vano_fire = True
    if callback.data.startswith('balls'):
        text = ('Наступит утро, мы будем не одни\n'
                'На стенке мишура, на ёлочке шары\n'
                'Наступит утро, наступит новый год\n'
                'Мы будем с друзьями, нам будет хорошо')
        local_storage.vano_balls = True
    if not callback.data.startswith('start'):
        bot.send_message(
            chat_id=callback.message.chat.id,
            text=text
        )
    if not (local_storage.vano_lights and local_storage.vano_pine and local_storage.vano_fire and
            local_storage.vano_balls):
        keyboard = InlineKeyboardMarkup()
        if not local_storage.vano_lights:
            keyboard.row(InlineKeyboardButton(text='Зажечь гирлянды', callback_data='lights_new_year'))
        if not local_storage.vano_pine:
            keyboard.row(InlineKeyboardButton(text='Зажечь ёлочку', callback_data='pine_new_year'))
        if not local_storage.vano_fire:
            keyboard.row(InlineKeyboardButton(text='Подготовить фейерверки', callback_data='fire_new_year'))
        if not local_storage.vano_balls:
            keyboard.row(InlineKeyboardButton(text='Повесить мишуру и шары', callback_data='balls_new_year'))
        bot.send_message(
            chat_id=callback.message.chat.id,
            text='Квартира находится в предновогоднем настроении',
            reply_markup=keyboard,
            parse_mode='Markdown'
        )
    else:
        bot.send_message(
            chat_id=callback.message.chat.id,
            text='Всё готово! А самое главное ты теперь заряжен на самый мощный концерт в истории планеты'
        )
        if IS_PROD:
            sleep(3)
        bot.send_message(
            chat_id=callback.message.chat.id,
            text='На этом история Вани заканчивается. Ты можешь пройти другие истории: /help'
        )
        local_storage.vano_progress = 'finished'
        print_greetings_for_last_story(callback)


@bot.message_handler(commands=['play_murad'])
def play_murad(message):
    local_storage = storage[message.chat.id]

    # Restore progress
    if local_storage.murad_progress != 'unstarted':
        vano_steps[local_storage.murad_progress](
            local_storage.murad_last_callback
        )

    # Or start new game
    else:
        bot.send_message(
            chat_id=message.chat.id,
            text='Ты начал игру за Мурада. Тебе доступны способности:\n*«Пиво»*',
            parse_mode='Markdown'
        )
        if IS_PROD:
            sleep(2)
        keyboard = InlineKeyboardMarkup()
        keyboard.row(InlineKeyboardButton(text='Зажечь синюю свечу', callback_data='blue_candle'))
        keyboard.row(InlineKeyboardButton(text='Зажечь красную свечу', callback_data='red_candle'))
        keyboard.row(InlineKeyboardButton(text='Зажечь свечу из комнаты страха', callback_data='scary_candle'))
        bot.send_message(
            chat_id=message.chat.id,
            text='Ты просыпаешься, открываешь глаза, но ничего не видишь',
            reply_markup=keyboard,
            parse_mode='Markdown'
        )


@bot.callback_query_handler(func=lambda call: call.data.endswith('candle'))
@progress('murad', 'candle')
def candle(callback):
    if callback.data.startswith('red'):
        bot.send_message(
            chat_id=callback.message.chat.id,
            text='Тихой сапой ты окунаешься в страну чудес.'
                 ' В этом мире ты можешь быть кем угодно. Но твой выбор это ходить за пивом в группе Ошибка Снека.'
                 ' Сегодня ты точно узнаешь глубока ли кроличья нора'
        )
        if IS_PROD:
            sleep(4)
        bot.send_message(
            chat_id=callback.message.chat.id,
            text='Ты осматриваешь помещение в котором находишься'
        )
        if IS_PROD:
            sleep(1)
        callback.data = 'look_quest'
        quest(callback)

    if callback.data.startswith('blue'):
        bot.send_message(
            chat_id=callback.message.chat.id,
            text='Ты просыпаешься в своей постели и веришь, что всё это был сон. '
                 'Никаких ошибок в твоей жизни не было. Шоколадки всегда выпадали из вендинговых аппаратов. '
                 'Ты не знаешь, что было пиво. Ты не знаешь, что это пиво нужно было куда-то носить'
        )
        if IS_PROD:
            sleep(3)
        bot.send_message(
            chat_id=callback.message.chat.id,
            text='*You lose*. Начать заново: /play_murad',
            parse_mode='Markdown'
        )
    if callback.data.startswith('scary'):
        bot.send_message(
            chat_id=callback.message.chat.id,
            text='Ты зажигаешь свечу и видишь перед собой грузина, сидящего на корточках. Он спрашивает тебя:'
        )
        if IS_PROD:
            sleep(2)
        keyboard = InlineKeyboardMarkup()
        keyboard.row(InlineKeyboardButton(text='Мыл', callback_data='washed_candle'))
        bot.send_message(
            chat_id=callback.message.chat.id,
            text='Попу мыл?',
            reply_markup=keyboard,
            parse_mode='Markdown'
        )
    if callback.data.startswith('washed'):
        bot.send_message(
            chat_id=callback.message.chat.id,
            text='Грузин молча тушит свечу...'
        )
        if IS_PROD:
            sleep(3)
        bot.send_message(
            chat_id=callback.message.chat.id,
            text='*Ты проиграл*. Начать заново: /play_murad',
            parse_mode='Markdown'
        )


def form_use_list(local_storage, keyboard, endpoint, first_word='Использовать', endpoint_suffix='quest'):
    if local_storage.murad_axe:
        keyboard.row(InlineKeyboardButton(text=f'{first_word} топор',
                                          callback_data=f'{endpoint}_axe_{endpoint_suffix}'))
    if local_storage.murad_stet:
        keyboard.row(InlineKeyboardButton(text=f'{first_word} стетоскоп',
                                          callback_data=f'{endpoint}_stet_{endpoint_suffix}'))
    if local_storage.murad_tape:
        keyboard.row(InlineKeyboardButton(text=f'{first_word} кассету',
                                          callback_data=f'{endpoint}_tape_{endpoint_suffix}'))
    if local_storage.murad_rod:
        keyboard.row(InlineKeyboardButton(text=f'{first_word} удочку',
                                          callback_data=f'{endpoint}_rod_{endpoint_suffix}'))
    if endpoint_suffix == 'quest':
        keyboard.row(InlineKeyboardButton(text='Назад', callback_data='look_quest'))


def item_does_not_affect(callback):
    default_back_keyboard = InlineKeyboardMarkup()
    default_back_keyboard.add(InlineKeyboardButton(text='Назад', callback_data='look_quest'))
    bot.send_message(
        chat_id=callback.message.chat.id,
        text='Предмет не подходит',
        reply_markup=default_back_keyboard,
        parse_mode='Markdown'
    )


@bot.callback_query_handler(func=lambda call: call.data.endswith('_quest'))
@progress(story='murad', step='quest')
def quest(callback):
    local_storage = storage[callback.message.chat.id]

    if callback.data.startswith('look'):
        keyboard = InlineKeyboardMarkup()
        keyboard.row(InlineKeyboardButton(text='Осмотреть аквариум', callback_data='aqua_l_quest'))
        keyboard.row(InlineKeyboardButton(text='Осмотреть магнитофон', callback_data='player_l_quest'))
        keyboard.row(InlineKeyboardButton(text='Осмотреть шкаф', callback_data='locker_l_quest'))
        keyboard.row(InlineKeyboardButton(text='Осмотреть дверь', callback_data='door_l_quest'))
        if local_storage.murad_seif:
            keyboard.row(InlineKeyboardButton(text='Осмотреть сейф', callback_data='seif_l_quest'))
        bot.send_message(
            chat_id=callback.message.chat.id,
            text='Ты находишься в подвале. Здесь почти пусто, есть только несколько вещей',
            reply_markup=keyboard,
            parse_mode='Markdown'
        )
    if callback.data.startswith('locker'):
        if local_storage.murad_locker:
            keyboard = InlineKeyboardMarkup()
            keyboard.add(InlineKeyboardButton(text='Назад', callback_data='look_quest'))
            bot.send_message(
                chat_id=callback.message.chat.id,
                text='Вы уже взяли здесь всё, что можно',
                reply_markup=keyboard,
                parse_mode='Markdown'
            )
        else:
            bot.send_message(
                chat_id=callback.message.chat.id,
                text='Вы открываете шкаф. Здесь кассета и удочка.'
            )
            keyboard = InlineKeyboardMarkup()
            keyboard.row(InlineKeyboardButton(text='Назад', callback_data='look_quest'))
            bot.send_message(
                chat_id=callback.message.chat.id,
                text='Кассета добавлена в инвентарь\n'
                     'Удочка добавлена в инвентарь',
                reply_markup=keyboard,
                parse_mode='Markdown'
            )
            local_storage.murad_tape = True
            local_storage.murad_rod = True
            local_storage.murad_locker = True
    if callback.data.startswith('door'):
        if callback.data.startswith('door_l'):
            keyboard = InlineKeyboardMarkup()
            form_use_list(local_storage, keyboard, 'door')
            bot.send_message(
                chat_id=callback.message.chat.id,
                text='Дверь выглядит крепко. Нужно найти ключ...',
                reply_markup=keyboard,
                parse_mode='Markdown'
            )
        elif callback.data.startswith('door_axe'):
            bot.send_message(
                chat_id=callback.message.chat.id,
                text='Ты разносишь дверь в щепки. Путь свободен'
            )
            callback.data = 'start_charon'
            charon(callback)
        else:
            item_does_not_affect(callback)
    if callback.data.startswith('aqua'):
        if callback.data.startswith('aqua_l'):
            keyboard = InlineKeyboardMarkup()
            form_use_list(local_storage, keyboard, 'aqua')
            bot.send_message(
                chat_id=callback.message.chat.id,
                text='В аквариуме кружатся пираньи. На дне лежит стетоскоп',
                reply_markup=keyboard,
                parse_mode='Markdown'
            )
        elif local_storage.murad_aqua:
            keyboard = InlineKeyboardMarkup()
            keyboard.row(InlineKeyboardButton(text='Назад', callback_data='look_quest'))
            bot.send_message(
                chat_id=callback.message.chat.id,
                text='Ты уже выудил стетоскоп',
                reply_markup=keyboard,
                parse_mode='Markdown'
            )
        elif callback.data.startswith('aqua_rod'):
            bot.send_message(
                chat_id=callback.message.chat.id,
                text='Ты успешно выуживаешь стетоскоп из аквариума'
            )
            keyboard = InlineKeyboardMarkup()
            keyboard.row(InlineKeyboardButton(text='Назад', callback_data='look_quest'))
            bot.send_message(
                chat_id=callback.message.chat.id,
                text='Стетоскоп добавлен в инвентарь',
                reply_markup=keyboard,
                parse_mode='Markdown'
            )
            local_storage.murad_stet = True
            local_storage.murad_aqua = True
        else:
            item_does_not_affect(callback)
    if callback.data.startswith('player'):
        if callback.data.startswith('player_l'):
            keyboard = InlineKeyboardMarkup()
            form_use_list(local_storage, keyboard, 'player')
            bot.send_message(
                chat_id=callback.message.chat.id,
                text='Обычный магнитофон. Внутри нет кассеты',
                reply_markup=keyboard,
                parse_mode='Markdown'
            )
        elif local_storage.murad_player:
            keyboard = InlineKeyboardMarkup()
            keyboard.row(InlineKeyboardButton(text='Назад', callback_data='look_quest'))
            bot.send_message(
                chat_id=callback.message.chat.id,
                text='Ты уже использовал кассету',
                reply_markup=keyboard,
                parse_mode='Markdown'
            )
        elif callback.data.startswith('player_tape'):
            keyboard = InlineKeyboardMarkup()
            keyboard.add(InlineKeyboardButton(text='Назад', callback_data='look_quest'))
            bot.send_message(
                chat_id=callback.message.chat.id,
                text='Вы вставляете кассету в магнитофон. Играет песня Ошибка Снека — Всё что есть.'
                     ' Вдруг задняя стенка шкафа открывается. За ним оказывается сейф',
                reply_markup=keyboard,
                parse_mode='Markdown'
            )
            local_storage.murad_player = True
            local_storage.murad_seif = True
        else:
            item_does_not_affect(callback)
    if callback.data.startswith('seif'):
        if callback.data.startswith('seif_l'):
            keyboard = InlineKeyboardMarkup()
            form_use_list(local_storage, keyboard, 'seif')
            bot.send_message(
                chat_id=callback.message.chat.id,
                text='Сейф с прокручивающимся круговым циферблатом',
                reply_markup=keyboard,
                parse_mode='Markdown'
            )
        elif local_storage.murad_axe:
            keyboard = InlineKeyboardMarkup()
            keyboard.row(InlineKeyboardButton(text='Назад', callback_data='look_quest'))
            bot.send_message(
                chat_id=callback.message.chat.id,
                text='Ты уже открыл сейф',
                reply_markup=keyboard,
                parse_mode='Markdown'
            )
        elif callback.data.startswith('seif_stet'):
            keyboard = InlineKeyboardMarkup()
            keyboard.add(InlineKeyboardButton(text='Назад', callback_data='look_quest'))
            bot.send_message(
                chat_id=callback.message.chat.id,
                text='Ты прослушиваешь сейф и успешно его открываешь. Внутри оказывается топор'
            )
            bot.send_message(
                chat_id=callback.message.chat.id,
                text='Топор добавлен в инвентарь',
                reply_markup=keyboard,
                parse_mode='Markdown'
            )
            local_storage.murad_axe = True
        else:
            item_does_not_affect(callback)


@bot.callback_query_handler(func=lambda call: call.data.endswith('_charon'))
@progress(story='murad', step='charon')
def charon(callback):
    local_storage = storage[callback.message.chat.id]
    keyboard = InlineKeyboardMarkup()
    text = 'Что-то пошло не так'
    # bot.send_message()
    if callback.data.startswith('start'):
        text = 'За первой дверью оказывается вторая. Её охраняет Харон, так просто он тебя не пропустит'
    if callback.data.startswith('give'):
        text = 'Этого мало'
        if callback.data.startswith('give_axe'):
            local_storage.murad_axe = False
        if callback.data.startswith('give_stet'):
            local_storage.murad_stet = False
        if callback.data.startswith('give_tape'):
            local_storage.murad_tape = False
        if callback.data.startswith('give_rod'):
            local_storage.murad_rod = False
    # RETURN
    if not (local_storage.murad_axe or local_storage.murad_stet or local_storage.murad_rod or
            local_storage.murad_tape):
        bot.send_message(
            chat_id=callback.message.chat.id,
            text='Ты отдал Харону ВСЁ ЧТО ЕСТЬ'
        )
        keyboard = InlineKeyboardMarkup()
        keyboard.add(InlineKeyboardButton(text='«Пиво»', callback_data='murad_ending'))
        bot.send_message(
            chat_id=callback.message.chat.id,
            text='Осталось сделать две вещи перед концертом: сходить за пивом и порепетировать с Денчиком в качалке',
            reply_markup=keyboard,
            parse_mode='Markdown'
        )
        return

    form_use_list(local_storage, keyboard, endpoint='give', first_word='Отдать', endpoint_suffix='charon')
    bot.send_message(
        chat_id=callback.message.chat.id,
        text=text,
        reply_markup=keyboard,
        parse_mode='Markdown'
    )


@bot.callback_query_handler(func=lambda call: call.data.endswith('murad_ending'))
@progress(story='murad', step='murad_ending')
def murad_ending(callback):
    bot.send_message(
        chat_id=callback.message.chat.id,
        text='Пиво куплено. И ты отправляешься в качалку, где тебя ждёт Ден'
    )
    bot.send_message(
        chat_id=callback.message.chat.id,
        text='На этом заканчивается линия Мурада. Пройти остальные истории: /help'
    )
    bot.send_message(
        chat_id=callback.message.chat.id,
        text='Разблокирован персонаж: Ден'
    )
    storage[callback.message.chat.id].den_available = True
    storage[callback.message.chat.id].murad_progress = 'finished'
    print_greetings_for_last_story(callback)


@bot.message_handler(commands=['play_sanya'])
def play_sanya(message):
    local_storage = storage[message.chat.id]

    # Restore progress
    if local_storage.sanya_progress != 'unstarted':
        sanya_steps[local_storage.sanya_progress](
            local_storage.sanya_last_callback
        )

    # START NEW GAME
    else:
        text = 'Ты играешь за Саню. Тебе доступны способности:\n*«Тыщ-тыщ-тыщ»*'
        bot.send_message(
            chat_id=message.chat.id,
            text=text,
            parse_mode='Markdown'
        )
        if IS_PROD:
            sleep(3)
        keyboard = InlineKeyboardMarkup()
        keyboard.row(InlineKeyboardButton(text='Узнать подробнее', callback_data='list_irritants'))
        bot.send_message(
            chat_id=message.chat.id,
            text='Перед концертом ты хочешь поиграть в Майнкрафт, но тебе мешают некоторые раздражители',
            reply_markup=keyboard,
            parse_mode='Markdown'
        )


@bot.callback_query_handler(func=lambda call: call.data.endswith('irritants'))
@progress(story='sanya', step='irritants')
def irritants(callback):
    local_storage = storage[callback.message.chat.id]
    keyboard = InlineKeyboardMarkup()
    if not (local_storage.sanya_conday or local_storage.sanya_hungry or local_storage.sanya_dogs):
        bot.send_message(
            chat_id=callback.message.chat.id,
            text='Ты решил все вопросики и теперь можешь спокойно поиграть в Майнкрафт'
        )
        bot.send_message(
            chat_id=callback.message.chat.id,
            text='А дальше у меня уже не хватает времени. Поэтому эта линия закончена (сори)'
        )
        bot.send_message(
            chat_id=callback.message.chat.id,
            text='Ты прошёл линию Сани. Остальные линии: /help'
        )
        local_storage.sanya_progress = 'finished'
        print_greetings_for_last_story(callback)
        return
    if local_storage.sanya_conday:
        keyboard.row(InlineKeyboardButton(text='Жарко пизда ваще', callback_data='start_conday'))
    if local_storage.sanya_dogs:
        keyboard.row(InlineKeyboardButton(text='Собаки орут', callback_data='start_dogs'))
    if local_storage.sanya_hungry:
        keyboard.row(InlineKeyboardButton(text='Хочу есть', callback_data='start_hungry'))
    bot.send_message(
        chat_id=callback.message.chat.id,
        text='Реши проблемы, чтобы спокойно поиграть в майнкрафт',
        reply_markup=keyboard,
        parse_mode='Markdown'
    )


def irritant_base(callback, text, keyboard, done_message):
    if callback.data.startswith('done'):
        bot.send_message(
            chat_id=callback.message.chat.id,
            text=done_message
        )
        callback.data = 'irritants'
        irritants(callback)
        return
    bot.send_message(
        chat_id=callback.message.chat.id,
        text=text,
        reply_markup=keyboard,
        parse_mode='Markdown'
    )
    if IS_PROD:
        sleep(3)


@bot.callback_query_handler(func=lambda call: call.data.endswith('_dogs'))
@progress(story='sanya', step='dogs')
def dogs(callback):
    keyboard = InlineKeyboardMarkup()
    keyboard.row(InlineKeyboardButton(text='«Тыщ-тыщ-тыщ»', callback_data='done_dogs'))
    text = 'Что-то пошло не так'
    if callback.data.startswith('start'):
        keyboard.row(InlineKeyboardButton(text='Попросить успокоиться', callback_data='continue_dogs'))
        text = 'Собаки лают так, что у тебя начинает болеть голова'
    if callback.data.startswith('continue'):
        text = 'Собаки игнорируют все твои просьбы'
    if callback.data.startswith('done'):
        storage[callback.message.chat.id].sanya_dogs = False
    irritant_base(callback, text, keyboard, done_message='Проблема успешно решена')


@bot.callback_query_handler(func=lambda call: call.data.endswith('conday'))
@progress(story='sanya', step='conday')
def conday(callback):
    keyboard = InlineKeyboardMarkup()
    keyboard.row(InlineKeyboardButton(text='«Тыщ-тыщ-тыщ»', callback_data='done_conday'))
    text = 'Что-то пошло не так'
    if callback.data.startswith('start'):
        keyboard.row(InlineKeyboardButton(text='Воспользоваться пультом', callback_data='continue_conday'))
        text = 'Жарко... Наверно стоит включить кондей'
    if callback.data.startswith('continue'):
        text = 'Кондей никак не реагирует на пульт'
    if callback.data.startswith('done'):
        storage[callback.message.chat.id].sanya_conday = False
    irritant_base(callback, text, keyboard, done_message='Кондей начинает работать после трёх ударов')


@bot.callback_query_handler(func=lambda call: call.data.endswith('hungry'))
@progress(story='sanya', step='hungry')
def hungry(callback):
    keyboard = InlineKeyboardMarkup()
    keyboard.row(InlineKeyboardButton(text='«Тыщ-тыщ-тыщ»', callback_data='done_hungry'))
    text = 'Что-то пошло не так'
    if callback.data.startswith('start'):
        keyboard.row(InlineKeyboardButton(text='Посмотреть в холодильнике', callback_data='continue_hungry'))
        text = 'Нужно поискать еду'
    if callback.data.startswith('continue'):
        text = 'В холодильнике еды нет (у нас вымышленная вселенная)'
    if callback.data.startswith('done'):
        storage[callback.message.chat.id].sanya_hungry = False
    irritant_base(
        callback, text, keyboard,
        done_message='Ты стучишь по холодильнику, и из него как из пиньяты вылетает еда')


@bot.message_handler(commands=['play_den'])
def play_den(message):
    local_storage = storage[message.chat.id]

    # Restore progress
    if local_storage.den_progress != 'unstarted':
        den_steps[local_storage.den_progress](
            local_storage.den_last_callback
        )
    # Start new game
    elif storage[message.chat.id].den_available:
        bot.send_message(
            chat_id=message.chat.id,
            text='Теперь ты играешь за Дена. Вам доступны способности:\n*«Тачка Дена»*\n*«Бас соло»*',
            parse_mode='Markdown'
        )
        if IS_PROD:
            sleep(3)
        keyboard = InlineKeyboardMarkup()
        keyboard.row(InlineKeyboardButton(text='BONES — HDMI', callback_data='bones_car_music'))
        keyboard.row(InlineKeyboardButton(text='Ошибка Снека — Кости', callback_data='snack_car_music'))
        bot.send_message(
            chat_id=message.chat.id,
            text='Ты уже едешь в качалочку к Мураду. Ехать в тишине скучно. Поэтому ты включаешь музыку',
            reply_markup=keyboard,
            parse_mode='Markdown'
        )
    else:
        bot.message_handler(
            chat_id=message.chat.id,
            text='Игра за Денчика пока не доступна'
        )


@bot.callback_query_handler(func=lambda call: call.data.endswith('_car_music'))
@progress(story='den', step='car_music')
def car_music(callback):
    if callback.data.startswith('snack'):
        bot.send_message(
            chat_id=callback.message.chat.id,
            text='Вот это хорошая музыка! Весёлая!'
        )
        if IS_PROD:
            sleep(2)
        keyboard = InlineKeyboardMarkup()
        keyboard.row(InlineKeyboardButton(text='Позвать Мурада', callback_data='murad_gym'))
        keyboard.row(InlineKeyboardButton(text='Подкинуть в воздух', callback_data='up_gym'))
        keyboard.row(InlineKeyboardButton(text='«Бас соло»', callback_data='bass_gym'))
        bot.send_message(
            chat_id=callback.message.chat.id,
            text='Ты сделал правильный выбор и успешно добрался до качалочки. Вы с Мурадом жмёте от груди. '
                 '500кг, 1000кг, 2000кг. Тут у железа вырастают руки, и оно начинает тебя душить',
            reply_markup=keyboard,
            parse_mode='Markdown'
        )
    if callback.data.startswith('bones'):
        bot.send_message(
            chat_id=callback.message.chat.id,
            text='Бензин кончился короче. Ну плохо в общем. Не то ты выбрал.'
        )
        bot.send_message(
            chat_id=callback.message.chat.id,
            text='*Ты проиграл*. Начать заново: /play_den',
            parse_mode='Markdown'
        )


@bot.callback_query_handler(func=lambda call: call.data.endswith('_gym'))
@progress(story='den', step='gym')
def gym(callback):
    keyboard = InlineKeyboardMarkup()
    keyboard.row(InlineKeyboardButton(text='Позвать Мурада', callback_data='murad_gym'))
    if callback.data.startswith('up'):
        storage[callback.message.chat.id].den_gym_up = True
        if not storage[callback.message.chat.id].den_gym_bass:
            keyboard.row(InlineKeyboardButton(text='«Бас соло»', callback_data='bass_gym'))
        bot.send_message(
            chat_id=callback.message.chat.id,
            text='Железо не может летать, поэтому оно снова приземляется тебе на грудь',
            reply_markup=keyboard,
            parse_mode='Markdown'
        )
    if callback.data.startswith('bass'):
        storage[callback.message.chat.id].den_gym_bass = True
        if not storage[callback.message.chat.id].den_gym_up:
            keyboard.row(InlineKeyboardButton(text='Подкинуть в воздух', callback_data='up_gym'))
        bot.send_message(
            chat_id=callback.message.chat.id,
            text='Ты тянешься к басу, но не можешь достать до него',
            reply_markup=keyboard,
            parse_mode='Markdown'
        )
    if callback.data.startswith('murad'):
        bot.send_message(
            chat_id=callback.message.chat.id,
            text='Мурад флоссом перерезает вес пополам'
        )
        if IS_PROD:
            sleep(2)
        keyboard = InlineKeyboardMarkup()
        keyboard.row(InlineKeyboardButton(text='Сделать подножку', callback_data='yes_sugar'))
        keyboard.row(InlineKeyboardButton(text='«Бас соло»', callback_data='bass_sugar'))
        bot.send_message(
            chat_id=callback.message.chat.id,
            text='Железо было повержено. Однако, неожиданно в gym появляется враждебно настроенный сахар',
            reply_markup=keyboard,
            parse_mode='Markdown'
        )


@bot.callback_query_handler(func=lambda call: call.data.endswith('_play_dota'))
@progress(story='kolyan_and_lexa', step='play_dota')
def play_dota(callback):
    if callback.data.startswith('yes'):
        keyboard = InlineKeyboardMarkup()
        if not storage[callback.message.chat.id].pudge_picked:
            keyboard.row(InlineKeyboardButton('Pudge', callback_data='pudge_play_dota_pick'))
        if not storage[callback.message.chat.id].techies_picked:
            keyboard.row(InlineKeyboardButton('Techies', callback_data='techies_play_dota_pick'))
        keyboard.row(InlineKeyboardButton('Ogre Magi', callback_data='ogre_magi_play_dota_pick'))
        text = 'Кого пикаем?'
        if storage[callback.message.chat.id].first_dota_play_pick:
            text = 'Вы находите игру. Кого пикаем?'
        bot.send_message(
            chat_id=callback.message.chat.id,
            text=text,
            reply_markup=keyboard,
            parse_mode='Markdown'
        )
        storage[callback.message.chat.id].first_dota_play_pick = False
    if callback.data.startswith('no'):
        bot.send_message(
            chat_id=callback.message.chat.id,
            text='Вы начинаете распеваться перед концертом. Тут из пустоты материализуется Бонес.'
                 ' Он смотрит на вас с презрением, и вы начинаете батлиться.'
        )
        if IS_PROD:
            sleep(3)
        bot.send_message(
            chat_id=callback.message.chat.id,
            text=("I'm swerving off, my eyes closed\n"
                  "Graveyard's where I call home\n"
                  "Razor blade on my fuckin' bones\n"
                  "Touch me and I'ma cut you off")
        )
        if IS_PROD:
            sleep(3)
        keyboard = InlineKeyboardMarkup()
        keyboard.row(InlineKeyboardButton(text='Пук, среньк', callback_data='no_bones_fight'))
        keyboard.row(InlineKeyboardButton(text='«Навалить репчика»', callback_data='yes_bones_fight'))
        bot.send_message(
            chat_id=callback.message.chat.id,
            text='Вы отвечаете:',
            reply_markup=keyboard,
            parse_mode='Markdown'
        )


@bot.callback_query_handler(func=lambda call: call.data.endswith('_sugar'))
@progress(story='den', step='sugar')
def sugar(callback):
    if callback.data.startswith('yes'):
        keyboard = InlineKeyboardMarkup()
        keyboard.add(InlineKeyboardButton(text='Сделать подножку (ЕЩЁ РАЗ)', callback_data='again_sugar'))
        bot.send_message(
            chat_id=callback.message.chat.id,
            text='Сахар упал. Сахар упал',
            reply_markup=keyboard,
            parse_mode='Markdown'
        )
    if callback.data.startswith('bass'):
        keyboard = InlineKeyboardMarkup()
        keyboard.add(InlineKeyboardButton(text='Сделать подножку', callback_data='yes_sugar'))
        bot.send_message(
            chat_id=callback.message.chat.id,
            text='У сахара нет ушей. Поэтому сахару бас не слышно',
            reply_markup=keyboard,
            parse_mode='Markdown'
        )
    if callback.data.startswith('again'):
        keyboard = InlineKeyboardMarkup()
        keyboard.add(InlineKeyboardButton(
            text='ВСЕ ВМЕСТЕ',
            callback_data='together_sugar'
        ))
        bot.send_message(
            chat_id=callback.message.chat.id,
            text='Сахар упал. Сахар упал',
            reply_markup=keyboard,
            parse_mode='Markdown'
        )
    if callback.data.startswith('together'):
        bot.send_message(
            chat_id=callback.message.chat.id,
            text='Сахар упал. Сахар упал. Не слышу'
        )
        if IS_PROD:
            sleep(3)
        bot.send_message(
            chat_id=callback.message.chat.id,
            text='Подсказка! Используйте голосовое сообщение'
        )
        storage[callback.message.chat.id].den_voice_available = True


@bot.message_handler(content_types=['voice'])
def sugar_voice(message):
    if storage[message.chat.id].den_voice_available:
        bot.send_message(
            chat_id=message.chat.id,
            text='Сахар упал! Сахар упал! Быстрее!'
        )
        for i in range(4):
            if True:
                sleep(1)
            bot.send_message(
                chat_id=message.chat.id,
                text='САХАР УПАЛ! САХАР УПАЛ!'
            )
        storage[message.chat.id].den_voice_available = False
        bot.send_message(
            chat_id=message.chat.id,
            text='Сахар упал, и вы с Мурадом уже готовы к концерту.'
                 ' Осталось только подкрепиться, и вы отправляетесь в Мак'
        )
        if IS_PROD:
            sleep(3)
        keyboard = InlineKeyboardMarkup()
        keyboard.row(InlineKeyboardButton(text='Чизбургер', callback_data='cheese_mac'))
        keyboard.row(InlineKeyboardButton(text='Гамбургер', callback_data='beef_mac'))
        bot.send_message(
            chat_id=message.chat.id,
            text='Надо выбрать, что ты сегодня будешь есть',
            reply_markup=keyboard,
            parse_mode='Markdown'
        )


@bot.callback_query_handler(func=lambda call: call.data.endswith('_bones_fight'))
@progress(story='kolyan_and_lexa', step='bones_fight')
def bones_fight(callback):
    if callback.data.startswith('no'):
        keyboard = InlineKeyboardMarkup()
        keyboard.add(InlineKeyboardButton(text='«Навалить репчика»',
                                          callback_data='yes_bones_fight'))
        bot.send_message(
            chat_id=callback.message.chat.id,
            text='Пук, среньк какой-то. Не получилось. Попробуем ещё раз?',
            reply_markup=keyboard,
            parse_mode='Markdown'
        )
    if callback.data.startswith('yes'):
        bot.send_message(
            chat_id=callback.message.chat.id,
            text=("Ви вор десишн апир дизаливилинг\n"
                  "Накин э ро зе диарма инишетив\n"
                  "Вилин асил ю йор харма салитилин\n"
                  "Викин аволен септемба ар баталин")
        )
        if IS_PROD:
            sleep(3)
        keyboard = InlineKeyboardMarkup()
        keyboard.add(InlineKeyboardButton(text='«Крик»', callback_data='fatality_bones_fight'))
        bot.send_message(
            chat_id=callback.message.chat.id,
            text='Бонес испытывает стыд за свои слова. Над его головой появляется надпись "Fatality"',
            reply_markup=keyboard,
            parse_mode='Markdown'
        )
    if callback.data.startswith('fatality'):
        bot.send_message(
            chat_id=callback.message.chat.id,
            text='По квартире проносится ультимативный крик. Лопаются лампочки, бокалы и вазы. '
                 'Бонес развалился на маленькие осколкию.'
        )
        if IS_PROD:
            sleep(3)
        callback.data = 'start_boots'
        boots(callback)


@bot.callback_query_handler(func=lambda call: call.data.endswith('_boots'))
@progress(story='kolyan_and_lexa', step='boots')
def boots(callback):
    if callback.data.startswith('start'):
        keyboard = InlineKeyboardMarkup()
        keyboard.row(InlineKeyboardButton(text='Простить', callback_data='mercy_boots'))
        keyboard.row(InlineKeyboardButton(text='Наказать', callback_data='punish_boots'))
        bot.send_message(
            chat_id=callback.message.chat.id,
            text='Вроде бы уже и пора двигаться в сторону концертной точки, но тут две ваши головы обнаруживают,'
                 ' что кто-то сделал сигну Ошибки Снека на фоне унитаза',
            reply_markup=keyboard,
            parse_mode='Markdown'
        )
    if callback.data.startswith('mercy'):
        bot.send_message(
            chat_id=callback.message.chat.id,
            text='На этом история Коляна и Лёхи заканчивается. Ты можешь пройти другие истории: /help'
        )
        storage[callback.message.chat.id].kolyan_and_lexa_progress = 'finished'
        print_greetings_for_last_story(callback)
    if callback.data.startswith('punish'):
        bot.send_message(
            chat_id=callback.message.chat.id,
            text='История этой ветки остаётся за кадром. Можем только намекнуть'
        )
        STICKER_ID = 'CAACAgIAAxkBAAIFPWOwF-RocZq0Wyvey-ug8G9JClb6AAIbIgACoM4QSZ8fBFnQzApeLQQ'
        if IS_PROD:
            sleep(3)
        bot.send_sticker(
            chat_id=callback.message.chat.id,
            sticker=STICKER_ID
        )
        if IS_PROD:
            sleep(2)
        callback.data = 'mercy_boots'
        boots(callback)


@bot.callback_query_handler(func=lambda call: call.data.endswith('_mac'))
@progress(story='den', step='mac')
def mac(callback):
    if callback.data.startswith('cheese') or callback.data.startswith('beef'):
        keyboard = InlineKeyboardMarkup()
        keyboard.row(InlineKeyboardButton(text='Цезарь ролл', callback_data='cesar_mac'))
        keyboard.row(InlineKeyboardButton(text='Биг Тейсти', callback_data='taste_mac'))
        bot.send_message(
            chat_id=callback.message.chat.id,
            text='Что-то ещё?',
            reply_markup=keyboard,
            parse_mode='Markdown'
        )
    if callback.data.startswith('cesar') or callback.data.startswith('taste'):
        keyboard = InlineKeyboardMarkup()
        keyboard.row(InlineKeyboardButton(text='Сегодня буду КЛУБНИЧНЫЙ МИЛКШЕЙК', callback_data='straw_mac'))
        keyboard.row(InlineKeyboardButton(text='Сегодня буду ОБЫЧНЫЙ МИЛКШЕЙК', callback_data='common_mac'))
        bot.send_message(
            chat_id=callback.message.chat.id,
            text='Мурад берёт Макфлури. Ты тоже хочешь что-то на десерт',
            reply_markup=keyboard,
            parse_mode='Markdown'
        )
    if callback.data.startswith('straw') or callback.data.startswith('common'):
        bot.send_message(
            chat_id=callback.message.chat.id,
            text='В подарок вам дают СНЕК БОКС. Его ты возьмёшь с собой, чтобы угостить пацанов'
        )
        if IS_PROD:
            sleep(3)
        bot.send_message(
            chat_id=callback.message.chat.id,
            text='На этом история Денчика закончилась. Ты можешь пройти или перепройти другие истории. '
                 'Кликай /help для просмотра твоих возможностей'
        )
        if IS_PROD:
            sleep(3)
        storage[callback.message.chat.id].den_progress = 'finished'
        print_greetings_for_last_story(callback)


def print_greetings_for_last_story(callback):
    if IS_PROD:
        sleep(5)
    if storage[callback.message.chat.id].is_together_available():
        bot.send_message(
            chat_id=callback.message.chat.id,
            text='Ты прошёл все истории участников Ошибки Снека и теперь готов пройти последнюю. '
                 'Нажимай /play_together чтобы начать'
        )


@bot.callback_query_handler(func=lambda call: call.data.endswith('_play_dota_pick'))
@progress(story='kolyan_and_lexa', step='play_dota_pick')
def play_dota_pick(callback):
    if callback.data.startswith('ogre_magi'):
        with open('ogre_magi.jpg', 'rb') as ogre_magi_img:
            bot.send_photo(
                chat_id=callback.message.chat.id,
                photo=ogre_magi_img
            )
        bot.send_message(
            chat_id=callback.message.chat.id,
            text='Вы идёте на линию. Только первые крипы столкнулись, '
                 'как вражеский Бейн кидает сон на одну из ваших голов (на голову Коляна)'
        )
        if IS_PROD:
            sleep(5)
        keyboard = InlineKeyboardMarkup()
        keyboard.row(InlineKeyboardButton(text='Я тут (18+)', callback_data='yes_dream_call'))
        keyboard.row(InlineKeyboardButton(text='Не здесь', callback_data='no_dream_call'))
        bot.send_message(
            chat_id=callback.message.chat.id,
            text='Ты не понимаешь, что происходит. Какой-то далёкий голос зовёт тебя и спрашивает: "Ты где?"',
            reply_markup=keyboard,
            parse_mode='Markdown'
        )
    else:
        if callback.data.startswith('pudge'):
            storage[callback.message.chat.id].pudge_picked = True
            bot.send_message(
                chat_id=callback.message.chat.id,
                text="Пуджа пикнули обе стороны. Герой забанен"
            )
        if callback.data.startswith('techies'):
            storage[callback.message.chat.id].techies_picked = True
            bot.send_message(
                chat_id=callback.message.chat.id,
                text="Течиса пикнули обе стороны. Герой забанен"
            )
        callback.data = 'yes_play_dota'
        play_dota(callback)


@bot.callback_query_handler(func=lambda call: call.data.endswith('_dream_call'))
@progress(story='kolyan_and_lexa', step='dream_call')
def dream_call(callback):
    if callback.data.startswith('yes'):
        with open('undress_mask_and_dress.jpg', 'rb') as girl_img:
            bot.send_photo(
                chat_id=callback.message.chat.id,
                photo=girl_img
            )
        keyboard = InlineKeyboardMarkup()
        keyboard.row(InlineKeyboardButton(text='Снять маску', callback_data='mask_undress'))
        keyboard.row(InlineKeyboardButton(text='Снять одежду', callback_data='dress_undress'))
        bot.send_message(
            chat_id=callback.message.chat.id,
            text='Всё как в тумане... Сквозь дымку фантасмагории ты видишь её☝🏼',
            reply_markup=keyboard,
            parse_mode='Markdown'
        )
    if callback.data.startswith('no'):
        callback.data = 'next_undress'
        undress(callback)


@bot.callback_query_handler(func=lambda call: call.data.endswith('_undress'))
@progress(story='kolyan_and_lexa', step='undress')
def undress(callback):
    # START NEW STEP
    if callback.data.startswith('next'):
        bot.send_message(
            chat_id=callback.message.chat.id,
            text='Пока ты спал вражеская Медуза нафармила 9 слотов, и ваш трон упал.'
        )
        if IS_PROD:
            sleep(2)
        callback.data = 'start_boots'
        boots(callback)
        return
    # UPDATE BOOLS
    if callback.data.startswith('mask'):
        storage[callback.message.chat.id].mask_off = True
    if callback.data.startswith('dress'):
        storage[callback.message.chat.id].dress_off = True
    # PRINT PHOTO
    if storage[callback.message.chat.id].mask_off and storage[callback.message.chat.id].dress_off:
        with open('undress_face_and_nude.jpg', 'rb') as girl_img:
            bot.send_photo(
                chat_id=callback.message.chat.id,
                photo=girl_img
            )
        if IS_PROD:
            sleep(3)
        bot.send_message(
            chat_id=callback.message.chat.id,
            text='За то, что ты дрочил на Лёху к тебе в двери уже ломится ОМОН. Вот тебе мем, раз ты всё равно сядешь:'
        )
        if IS_PROD:
            sleep(1)
        with open('mem.jpg', 'rb') as mem_img:
            bot.send_photo(
                chat_id=callback.message.chat.id,
                photo=mem_img
            )
        if IS_PROD:
            sleep(3)
        storage[callback.message.chat.id].reset('kolyan_and_lexa')
        bot.send_message(
            chat_id=callback.message.chat.id,
            text='*Ты проиграл*. Начать заново: /play_kolyan_and_lexa',
            parse_mode='Markdown'
        )
    elif storage[callback.message.chat.id].mask_off:
        keyboard = InlineKeyboardMarkup()
        keyboard.row(InlineKeyboardButton(text='«Крик»', callback_data='next_undress'))
        keyboard.row(InlineKeyboardButton(text='Снять одежду😳', callback_data='dress_undress'))
        with open('undress_face_and_dress.jpg', 'rb') as girl_img:
            bot.send_photo(
                chat_id=callback.message.chat.id,
                photo=girl_img,
                reply_markup=keyboard,
                parse_mode='Markdown'
            )
    else:
        keyboard = InlineKeyboardMarkup()
        keyboard.row(InlineKeyboardButton(text='Снять маску', callback_data='mask_undress'))
        with open('undress_mask_and_nude.jpg', 'rb') as girl_img:
            bot.send_photo(
                chat_id=callback.message.chat.id,
                photo=girl_img,
                reply_markup=keyboard,
                parse_mode='Markdown'
            )


@bot.message_handler(commands=['play_together'])
def play_together(message):
    if storage[message.chat.id].together_available:
        bot.send_message(
            chat_id=message.chat.id,
            text='Вы играете за Ошибку Снека. Доступны все способности участников группы'
        )
        keyboard = InlineKeyboardMarkup()
        keyboard.row(InlineKeyboardButton(text='Маршрутка', callback_data='taxi_drive'))
        keyboard.row(InlineKeyboardButton(text='«Тачка Дена»', callback_data='car_drive'))
        bot.send_message(
            chat_id=message.chat.id,
            text='Самое время ехать на концерт. Чем воспользуемся?',
            reply_markup=keyboard,
            parse_mode='Markdown'
        )
    else:
        bot.send_message(
            chat_id=message.chat.id,
            text='Игра за Ошибку Снека пока не доступна'
        )


def get_performance_keyboard(car, drums, nails, metal, beer, screem, rap, bass):
    keyboard = InlineKeyboardMarkup()
    if car:
        keyboard.row(InlineKeyboardButton(text='«Тачка Дена»', callback_data='car_performance'))
    if drums:
        keyboard.row(InlineKeyboardButton(text='«Тыщ-тыщ-тыщ»', callback_data='drums_performance'))
    if nails:
        keyboard.row(InlineKeyboardButton(text='«Гвозди»', callback_data='nails_performance'))
    if metal:
        keyboard.row(InlineKeyboardButton(text='«Металлическая стружка»', callback_data='metal_performance'))
    if beer:
        keyboard.row(InlineKeyboardButton(text='«Пиво»', callback_data='beer_performance'))
    if screem:
        keyboard.row(InlineKeyboardButton(text='«Крик»', callback_data='scream_performance'))
    if rap:
        keyboard.row(InlineKeyboardButton(text='«Навалить репчика»', callback_data='rap_performance'))
    if bass:
        keyboard.row(InlineKeyboardButton(text='«Бас соло»', callback_data='bass_performance'))
    return keyboard


@bot.callback_query_handler(func=lambda call: call.data.endswith('_drive'))
@progress(story='together', step='drive')
def drive(callback):
    if callback.data.startswith('taxi'):
        bot.send_message(
            chat_id=callback.message.chat.id,
            text='Так как до Диеза едет только тройка все участники группы опоздали на концерт.'
        )
        bot.send_message(
            chat_id=callback.message.chat.id,
            text='*Ты проиграл*. Начать заново: /play_together',
            parse_mode='Markdown'
        )

    if callback.data.startswith('car'):
        local_storage = storage[callback.message.chat.id]
        keyboard = get_performance_keyboard(
            car=local_storage.ending_spells_car,
            drums=local_storage.ending_spells_drums,
            nails=local_storage.ending_spells_nails,
            metal=local_storage.ending_spells_metal,
            beer=local_storage.ending_spells_beer,
            screem=local_storage.ending_spells_scream,
            rap=local_storage.ending_spells_rap,
            bass=local_storage.ending_spells_bass
        )
        bot.send_message(
            chat_id=callback.message.chat.id,
            text='Вся группа Ошибка Снека в сборе. '
                 'В тачку Дена поместятся все кто нужно, и останется ещё одно свободное место. '
                 'Ошибка Снека уже в Диезе. '
                 'Темно, лишь на беке прогресс бар. '
                 'И вот звенят Кости. Вся группа поднимается на сцену. ',
            reply_markup=keyboard,
            parse_mode='Markdown'
        )


@bot.callback_query_handler(func=lambda call: call.data.endswith('_performance'))
@progress(story='together', step='performance')
def performance(callback):
    local_storage = storage[callback.message.chat.id]
    text = ''
    if callback.data.startswith('car'):
        local_storage.ending_spells_car = False
        text = ('Тачка Дена\n'
                'Строчка для песни\n'
                'Все девчонки в фанзоне поют эти строчки')
    if callback.data.startswith('drums'):
        local_storage.ending_spells_drums = False
        text = ('Гудит всепронзающее Нитро\n'
                'Публика ликует')
    if callback.data.startswith('nails'):
        local_storage.ending_spells_nails = False
        text = 'Гвозди летят со сцены и пронзают насквозь несколько сердец'
    if callback.data.startswith('metal'):
        local_storage.ending_spells_metal = False
        text = ('Никто не ожидал настолько суровой металлической стружки. '
                'Под каждый пэлмьют фанаты качают головой так,'
                ' что орбита земли изменяет своё направление на пару градусов')
    if callback.data.startswith('beer'):
        local_storage.ending_spells_beer = False
        text = ('Мурад достаёт пиво и обливает им первые ряды. '
                'Души фанатов начинают гореть. Девчонки в первом ряду снимают свои тишки "Ошибка Снека" '
            )
    if callback.data.startswith('scream'):
        local_storage.ending_spells_scream = False
        text = 'Вопль пронзает всю площадку. Публика ощущает свою причастность к великому'
    if callback.data.startswith('rap'):
        local_storage.ending_spells_rap = False
        text = ('Начинается лютая читка. '
                'Ни у кого нет сомнения, что это лучший флоу в мире, наполненный глубоким смыслом')
    if callback.data.startswith('bass'):
        local_storage.ending_spells_bass = False
        text = ('Бас проходит сквозь стены. Птицы вторят музыке Ошибки Снека. '
                'Перелётные стаи возвращаются домой')
    keyboard = get_performance_keyboard(
        car=local_storage.ending_spells_car,
        drums=local_storage.ending_spells_drums,
        nails=local_storage.ending_spells_nails,
        metal=local_storage.ending_spells_metal,
        beer=local_storage.ending_spells_beer,
        screem=local_storage.ending_spells_scream,
        rap=local_storage.ending_spells_rap,
        bass=local_storage.ending_spells_bass
    )
    bot.send_message(
        chat_id=callback.message.chat.id,
        text=text,
        reply_markup=keyboard,
        parse_mode='Markdown'
    )
    if not (local_storage.ending_spells_car or local_storage.ending_spells_drums or
            local_storage.ending_spells_nails or local_storage.ending_spells_metal or
            local_storage.ending_spells_beer or local_storage.ending_spells_scream or
            local_storage.ending_spells_rap or local_storage.ending_spells_bass):
        bot.send_message(
            chat_id=callback.message.chat.id,
            text=('Открывается портал в рай. '
                  'Все находящиеся в комнате испытывают оргазм, и умирают в самый счастливый день своей жизни')
        )
        if IS_PROD:
            sleep(5)
        bot.send_message(
            chat_id=callback.message.chat.id,
            text=('Вот и всё, что мы хотели вам сказать. '
                  'Приходите 3-го января в 17:00 в Диез на наш концерт')
        )
        if IS_PROD:
            sleep(4)
        bot.send_message(
            chat_id=callback.message.chat.id,
            text='/reset_all — Начать заново'
        )


kolyan_and_lexa_steps = {
    'play_dota': play_dota,
    'play_dota_pick': play_dota_pick,
    'undress': undress,
    'bones_fight': bones_fight,
    'dream_call': dream_call,
    'boots': boots
}
sanya_steps = {
    'irritants': irritants,
    'dogs': dogs,
    'conday': conday,
    'hungry': hungry
}
vano_steps = {
    'salad': salad,
    'stone': stone,
    'snack': snack,
    'new_year': new_year
}
murad_steps = {
    'candle': candle,
    'quest': quest,
    'charon': charon,
    'murad_ending': murad_ending
}
den_steps = {
    'car_music': car_music,
    'gym': gym,
    'sugar': sugar,
    'mac': mac
}
together_steps = {
    'drive': drive,
    'performance': performance
}


if __name__ == '__main__':
    bot.infinity_polling()
