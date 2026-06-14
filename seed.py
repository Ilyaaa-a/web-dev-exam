# Создание таблиц и заполнение данными (роли, жанры, пользователи, книги).

from app import app
from extensions import db
from models import (
    ROLE_ADMIN, ROLE_MODERATOR, ROLE_USER, Book, Genre, Role, User,
)

ROLES = [
    (ROLE_ADMIN, 'Суперпользователь, полный доступ к системе, '
                 'в том числе создание и удаление книг'),
    (ROLE_MODERATOR, 'Может редактировать данные книг и '
                     'производить модерацию рецензий'),
    (ROLE_USER, 'Может оставлять рецензии'),
]

GENRES = [
    'Роман', 'Фантастика', 'Детектив', 'Фэнтези', 'Поэзия',
    'Научная литература', 'Историческая проза', 'Приключения',
    'Драма', 'Ужасы',
]

# (логин, пароль, фамилия, имя, отчество, роль)
USERS = [
    ('admin', 'admin', 'Иванов', 'Иван', 'Иванович', ROLE_ADMIN),
    ('moder', 'moder', 'Петров', 'Пётр', 'Петрович', ROLE_MODERATOR),
    ('user', 'user', 'Сидоров', 'Сидор', 'Сидорович', ROLE_USER),
]

# 20 книг
BOOKS = [
    {
        'title': 'Война и мир', 'author': 'Лев Толстой',
        'publisher': 'Художественная литература', 'year': 1869, 'pages': 1300,
        'genres': ['Роман', 'Историческая проза'],
        'description': 'Роман-эпопея о русском обществе в эпоху войн против '
                       'Наполеона. Переплетение **судеб** героев на фоне '
                       'грандиозных исторических событий.',
    },
    {
        'title': 'Преступление и наказание', 'author': 'Фёдор Достоевский',
        'publisher': 'Эксмо', 'year': 1866, 'pages': 672,
        'genres': ['Роман', 'Драма'],
        'description': 'История бедного студента Раскольникова, решившегося на '
                       '*убийство*, и его мучительного пути к раскаянию.',
    },
    {
        'title': 'Анна Каренина', 'author': 'Лев Толстой',
        'publisher': 'АСТ', 'year': 1877, 'pages': 864,
        'genres': ['Роман', 'Драма'],
        'description': 'Трагическая история любви замужней женщины и её '
                       'столкновение с лицемерием высшего света.',
    },
    {
        'title': 'Мастер и Маргарита', 'author': 'Михаил Булгаков',
        'publisher': 'Азбука', 'year': 1967, 'pages': 480,
        'genres': ['Роман', 'Фэнтези'],
        'description': 'Дьявол посещает Москву 1930-х годов. Сатира, мистика и '
                       'вечная история **любви и творчества**.',
    },
    {
        'title': 'Евгений Онегин', 'author': 'Александр Пушкин',
        'publisher': 'Художественная литература', 'year': 1833, 'pages': 384,
        'genres': ['Поэзия', 'Роман'],
        'description': 'Роман в стихах — «энциклопедия русской жизни» и история '
                       'несостоявшейся любви Онегина и Татьяны.',
    },
    {
        'title': 'Мёртвые души', 'author': 'Николай Гоголь',
        'publisher': 'Эксмо', 'year': 1842, 'pages': 352,
        'genres': ['Роман', 'Драма'],
        'description': 'Похождения Чичикова, скупающего «мёртвые души» — '
                       'сатирическая поэма о пороках России.',
    },
    {
        'title': 'Отцы и дети', 'author': 'Иван Тургенев',
        'publisher': 'АСТ', 'year': 1862, 'pages': 320,
        'genres': ['Роман', 'Драма'],
        'description': 'Конфликт поколений и идей: нигилист Базаров против '
                       'устоев дворянского общества.',
    },
    {
        'title': 'Идиот', 'author': 'Фёдор Достоевский',
        'publisher': 'Азбука', 'year': 1869, 'pages': 640,
        'genres': ['Роман', 'Драма'],
        'description': 'Князь Мышкин, человек чистой души, оказывается среди '
                       'страстей и интриг петербургского общества.',
    },
    {
        'title': 'Братья Карамазовы', 'author': 'Фёдор Достоевский',
        'publisher': 'Эксмо', 'year': 1880, 'pages': 992,
        'genres': ['Роман', 'Драма'],
        'description': 'Философский роман о вере, свободе и отцеубийстве в '
                       'семье Карамазовых.',
    },
    {
        'title': 'Герой нашего времени', 'author': 'Михаил Лермонтов',
        'publisher': 'АСТ', 'year': 1840, 'pages': 224,
        'genres': ['Роман', 'Драма'],
        'description': 'Психологический портрет Печорина — «лишнего человека» '
                       'своей эпохи.',
    },
    {
        'title': 'Обломов', 'author': 'Иван Гончаров',
        'publisher': 'Художественная литература', 'year': 1859, 'pages': 528,
        'genres': ['Роман'],
        'description': 'История апатичного помещика Обломова и понятия '
                       '«обломовщины» как явления.',
    },
    {
        'title': 'Вишнёвый сад', 'author': 'Антон Чехов',
        'publisher': 'Азбука', 'year': 1904, 'pages': 96,
        'genres': ['Драма'],
        'description': 'Пьеса об уходящей эпохе дворянства и продаже родового '
                       'имения с вишнёвым садом.',
    },
    {
        'title': 'Капитанская дочка', 'author': 'Александр Пушкин',
        'publisher': 'Эксмо', 'year': 1836, 'pages': 256,
        'genres': ['Историческая проза', 'Роман'],
        'description': 'Повесть о любви и чести на фоне Пугачёвского восстания.',
    },
    {
        'title': 'Тихий Дон', 'author': 'Михаил Шолохов',
        'publisher': 'АСТ', 'year': 1940, 'pages': 1500,
        'genres': ['Роман', 'Историческая проза'],
        'description': 'Роман-эпопея о судьбе донского казачества в годы войны '
                       'и революции.',
    },
    {
        'title': 'Доктор Живаго', 'author': 'Борис Пастернак',
        'publisher': 'Азбука', 'year': 1957, 'pages': 592,
        'genres': ['Роман', 'Драма'],
        'description': 'Судьба врача и поэта Юрия Живаго на фоне революционных '
                       'потрясений начала XX века.',
    },
    {
        'title': 'Двенадцать стульев', 'author': 'Илья Ильф, Евгений Петров',
        'publisher': 'Эксмо', 'year': 1928, 'pages': 416,
        'genres': ['Роман', 'Приключения'],
        'description': 'Сатирический роман о поисках сокровищ, спрятанных в '
                       'одном из двенадцати стульев. Остап Бендер в деле!',
    },
    {
        'title': 'Горе от ума', 'author': 'Александр Грибоедов',
        'publisher': 'Художественная литература', 'year': 1825, 'pages': 160,
        'genres': ['Драма', 'Поэзия'],
        'description': 'Комедия в стихах о столкновении Чацкого с косным '
                       'московским обществом.',
    },
    {
        'title': 'Ревизор', 'author': 'Николай Гоголь',
        'publisher': 'АСТ', 'year': 1836, 'pages': 144,
        'genres': ['Драма'],
        'description': 'Комедия о том, как мелкого чиновника приняли за '
                       'грозного ревизора в уездном городе.',
    },
    {
        'title': 'Стихотворения', 'author': 'Сергей Есенин',
        'publisher': 'Азбука', 'year': 1925, 'pages': 320,
        'genres': ['Поэзия'],
        'description': 'Сборник лирики о русской деревне, природе и любви.',
    },
    {
        'title': 'Котлован', 'author': 'Андрей Платонов',
        'publisher': 'Эксмо', 'year': 1930, 'pages': 176,
        'genres': ['Роман', 'Драма'],
        'description': 'Антиутопическая повесть о строительстве «общепролетар'
                       'ского дома» и абсурде эпохи.',
    },
]


def seed():
    with app.app_context():
        db.create_all()

        roles = {}
        for name, description in ROLES:
            role = db.session.scalar(db.select(Role).filter_by(name=name))
            if role is None:
                role = Role(name=name, description=description)
                db.session.add(role)
            roles[name] = role

        for name in GENRES:
            if not db.session.scalar(db.select(Genre).filter_by(name=name)):
                db.session.add(Genre(name=name))

        for login, password, last, first, middle, role_name in USERS:
            if not db.session.scalar(db.select(User).filter_by(login=login)):
                user = User(
                    login=login, last_name=last, first_name=first,
                    middle_name=middle, role=roles[role_name],
                )
                user.set_password(password)
                db.session.add(user)

        db.session.flush()

        # Карта жанров по названию для назначения книгам
        genre_map = {
            g.name: g for g in db.session.scalars(db.select(Genre)).all()
        }

        created = 0
        for item in BOOKS:
            if db.session.scalar(db.select(Book).filter_by(title=item['title'])):
                continue
            book = Book(
                title=item['title'],
                description=item['description'],
                year=item['year'],
                publisher=item['publisher'],
                author=item['author'],
                pages=item['pages'],
            )
            book.genres = [genre_map[name] for name in item['genres']]
            db.session.add(book)
            created += 1

        db.session.commit()

        print('Готово.')
        print('  Роли, жанры и тестовые пользователи созданы:')
        print('    admin / admin  (администратор)')
        print('    moder / moder  (модератор)')
        print('    user  / user   (пользователь)')
        print(f'  Добавлено книг: {created} (всего в базе: '
              f'{db.session.scalar(db.select(db.func.count(Book.id)))})')
        print('  Обложки не заданы — загрузите их через '
              'редактирование книги.')


if __name__ == '__main__':
    seed()
