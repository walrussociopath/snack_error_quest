from content.ядерный_похмельник.история_мурада import ИСТОРИЯ_МУРАДА
from content.ядерный_похмельник.история_вани import ИСТОРИЯ_ВАНИ
from src.core.models import SubstoryRoute, StoryRouter


ЯДЕРНЫЙ_ПОХМЕЛЬНИК = StoryRouter.from_stories(
    code='nuclear_concert',
    content=(
        'Ошибка Снека готовится к концерту 3-го января. Помоги парням подготовиться и огненно выступить!\n'
        'Начни проходить историю за одного из участников группы Ошибка Снека'
    ),
    routes=(
        SubstoryRoute(
            title='Играть за Ваню',
            story=ИСТОРИЯ_ВАНИ
        ),
        SubstoryRoute(
            title='Играть за Мурада',
            story=ИСТОРИЯ_МУРАДА
        ),
    ),
)
