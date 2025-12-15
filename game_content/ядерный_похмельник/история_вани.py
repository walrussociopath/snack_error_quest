
from tg_quest import Attrs, Condition, Node, Reaction, Story


cond = Condition.all_reactions_used(
    next="#13",
    else_="#12",
)


Story(
    code="ваня",
    start_node=Node(
        content=
    )
    nods=(

    )
)
_NODES = (
    Node(
        code="#1",
        content="Вы начали игру за Вано. Доступные способности:\n*«Гвозди»*\n*«Металлическая стружка»*",
        wait=2,
        next="#2"
    ),
    Node(
        code="#2",
        content="Новый год на дворе, и вы продолжаете делать всевозможные салаты. "
                 "На этот раз вам нужно натереть сыр",
        reactions=(
            Reaction(
                title="«Гвозди»",
                next="#3"
            ),
            Reaction(
                title="«Металлическая стружка»",
                next="#4"
            ),
        )
    ),
    Node(
        code="#3",
        content="Какие гвозди? Давай стружку!",
        reactions=(
            Reaction(title="«Металлическая стружка»", next="#4"),
        )
    ),
    Node(
        code="#4",
        content="Ты достаёшь майонез из холодильника."
                 " Но вдруг появляется камень, который мешает продолжению этого сюжета",
        reactions=(
            Reaction(
                title="Причинить боль",
                next="#5"
            ),
            Reaction(
                title="«Гвозди»",
                next="#6"
            ),
        )
    ),
    Node(
        code="#5",
        content="Камень не может болеть! Попытка не удалась. Try again!",
        reactions=(
            Reaction(
                title="«Гвозди»",
                next="#6"
            ),
        )
    ),
    Node(
        code="#6",
        content="Гвозди уверенно входят в камень. Под натиском рубилова камень раскалывается пополам",
        wait=2,
        next="#7"
    ),
    Node(
        code="#7",
        content="Окей. Все салатики успешно замайонежены, но хочется большего. Хочется сахара, хочется энергии. "
                 "Хочется шоколадки!",
        wait=2,
        next="#8"
    ),
    Node(
        code="#8",
        content="Ты доходишь до ближайшего магазина, где есть вендинговый аппарат. Выбираешь нужную шоколадку...\n"
                 "Но вдруг засада! Шоколадка застряла...",
        reactions=(
            Reaction(
                title="Сдаться",
                next="#9"
            ),
            Reaction(
                title="ДАЙ МНЕ ШОКОЛАДКУ!",
                next="#10"
            ),
        )
    ),
    Node(
        code="#9",
        content="Ты уже готов уйти, но какое-то новогоднее чудо заставляет снек упасть. "
                 "Ты берёшь его и с удовольствием съедаешь",
        wait=2,
        next="#11"
    ),
    Node(
        code="#10",
        content="Аппарат трепещет перед величайшими строками современности. Шоколадка падает, и ты её съедаешь",
        wait=2,
        next="#11"
    ),
    Node(
        code="#11",
        content="Ты возвращаешься домой, ведь нужно настроиться на заряженную атмосферу перед концертом",
        wait=2,
        next="#12"
    ),
    Node(
        code="#12",
        content="Квартира находится в предновогоднем настроении",
        reactions=(
            Reaction.once(title="Зажечь гирлянды", next=cond),
            Reaction.once(title="Зажечь ёлочку", next=cond),
            Reaction.once(title="Подготовить фейерверки", next=cond),
            Reaction.once(title="Повесить мишуру и шары", next=cond),
        ),
    ),
    Node(
        code="#13",
        content="Всё готово! А самое главное ты теперь заряжен на самый мощный концерт в истории планеты",
        wait=2,
        next="#14"
    ),
    Node(
        code="#14",
        content="На этом история Вани заканчивается.",
        is_terminal=True,
    ),
)


ИСТОРИЯ_ВАНИ = Story(start_node=_NODES[0], nodes=_NODES)
