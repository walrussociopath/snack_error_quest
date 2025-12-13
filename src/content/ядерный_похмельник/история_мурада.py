
from core.models import Item
from src.core.models import Directions, Node, Story, Reaction, ItemApplication


# TAPE_ITEM = Item('Кассета')
# ROD_ITEM = Item('Удочка')
# AXE_ITEM = Item('Топор')
# STETHOSCOPE_ITEM = Item('Стетоскоп')


_NODES = (
    Node(
        code='#1',
        content='Ты начал игру за Мурада. Тебе доступны способности:\n*«Пиво»*',
        wait=2,
        next='#2',
        is_start_node=True,
    ),
    Node(
        code='#2',
        content='Ты просыпаешься, открываешь глаза, но ничего не видишь',
        reactions=(
            Reaction('Зажечь синюю свечу', '#3'),
            Reaction('Зажечь красную свечу', '#4'),
            Reaction('Зажечь свечу из комнаты страха', '#5'),
        ),
    ),
    Node(
        code='#3',
        content='Ты просыпаешься в своей постели и веришь, что всё это был сон. '
                 'Никаких ошибок в твоей жизни не было. Шоколадки всегда выпадали из вендинговых аппаратов. '
                 'Ты не знаешь, что было пиво. Ты не знаешь, что это пиво нужно было куда-то носить',
        wait=2,
        next='#6'        
    ),
    Node(
        code='#6',
        content='*You lose*',
        reactions=(
            Reaction('Начать заново', '#1'),
        )
    ),
    Node(
        code='#4',
        content='Тихой сапой ты окунаешься в страну чудес.'
                 ' В этом мире ты можешь быть кем угодно. Но твой выбор это ходить за пивом в группе Ошибка Снека.'
                 ' Сегодня ты точно узнаешь глубока ли кроличья нора',
        wait=4,
        next='#7'
    ),
    Node(
        code='#5',
        content='Ты зажигаешь свечу и видишь перед собой грузина, сидящего на корточках. Он спрашивает тебя:',
        wait=1.5,
        next='#8'
    ),
    Node(
        code='#8',
        content='Попу мыл?',
        reactions=(
            Reaction('Мыл', '#9'),
        )
    ),
    Node(
        code='#9',
        content='Грузин молча тушит свечу...',
        wait=2,
        next='#10',
    ),
    Node(
        code='#10',
        content='Ты проиграл',
        reactions=(
            Reaction('Начать заново', '#1'),
        ),
    ),
    Node(
        code='#7',
        content='Ты осматриваешь помещение, в котором находишься',
        wait=1,
        next='#11',
    ),
    Node(
        code='#11',
        content='Ты находишься в подвале. Здесь почти пусто, есть только несколько вещей',
        reactions=(
            Reaction('Осмотреть аквариум', '#12'),
            Reaction('Осмотреть магнитофон', '#13'),
            Reaction('Осмотреть шкаф', '#14'),
            Reaction('Осмотреть дверь', '#15'),
        )
    ),
    Node(
        code='#12',
        content='В аквариуме кружатся пираньи. На дне лежит стетоскоп',
        ask_using_item=True,
        items_transition={
            # ROD_ITEM: ItemApplication(
            #     content='Вы вытаскиваете стетоскоп',
            #     next=Directions.BACK, 
            #     add_items=STETHOSCOPE_ITEM
            # )
        },
        can_go_back=True
    ),
    # Node(
    #     code='#16',

    # ),
    Node(
        code='#13',
        content='Обычный магнитофон. Внутри нет кассеты',
        can_go_back=True
    )
)

ИСТОРИЯ_МУРАДА = Story.from_nodes(_NODES, code='murad_story')
