import datetime
import sys
from sqlalchemy import create_engine, Table, Column, Integer, String, MetaData, ForeignKey, DateTime, Text
from sqlalchemy.orm import mapper, sessionmaker


class BusParkStorage:
    """Класс для работы с базой данных"""

    class AllBuses:
        """Класс, создающий модель всего транспорта предприятия"""

        def __init__(self, bus_number, name_driver, surname_driver, route_number):
            self.bus_number = bus_number
            self.name_driver = name_driver
            self.surname_driver = surname_driver
            self.route_number = route_number

        def __repr__(self):
            return f'({self.bus_number}, {self.name_driver}, {self.surname_driver}, {self.route_number})'

    class BusesLine:
        """Класс, создающий модель таблицы для транспорта, находящегося на маршруте"""

        def __init__(self, auto_id, event_time):
            self.id = None
            self.auto = auto_id
            self.event_time = event_time

    class BusesPark:
        """Класс, создающий модель таблицы для транспорта, находящегося в парке (не на линии)"""

        def __init__(self, auto_id, event_time):
            self.id = None
            self.auto = auto_id
            self.event_time = event_time

    class BusesService:
        """Класс, создающий модель таблицы для транспорта, находящегося на ТО"""

        def __init__(self, auto_id, event_time):
            self.id = None
            self.auto = auto_id
            self.event_time = event_time

    def __init__(self, path):
        """Создаём движок базы данных"""
        self.database_engine = create_engine(f'sqlite:///{path}', echo=False, pool_recycle=7200)

        """Создаём объект MetaData"""
        self.metadata = MetaData()

        """Создаем таблицу всего транспорта на балансе в парке"""
        all_buses_table = Table('All_buses', self.metadata,
                                Column('id', Integer, primary_key=True),
                                Column('bus_number', Integer, unique=True),
                                Column('name_driver', String),
                                Column('surname_driver', String),
                                Column('route_number', Integer)
                                )

        """Создаём таблицу транспорта на линии"""
        buses_line_table = Table('Buses_line', self.metadata,
                                 Column('id', Integer, primary_key=True),
                                 Column('auto', ForeignKey('All_buses.id'), unique=True),
                                 Column('event_time', DateTime)
                                 )

        """Создаём таблицу транспорта на парке"""
        buses_park_table = Table('Buses_park', self.metadata,
                                 Column('id', Integer, primary_key=True),
                                 Column('auto', ForeignKey('All_buses.id'), unique=True),
                                 Column('event_time', DateTime)
                                 )

        """Создаём таблицу транспорта на ТО"""
        buses_service_table = Table('Buses_service', self.metadata,
                                    Column('id', Integer, primary_key=True),
                                    Column('auto', ForeignKey('All_buses.id'), unique=True),
                                    Column('event_time', DateTime)
                                    )

        """Создаём таблицы"""
        self.metadata.create_all(self.database_engine)

        """Создаём отображения"""
        mapper(self.AllBuses, all_buses_table)
        mapper(self.BusesLine, buses_line_table)
        mapper(self.BusesPark, buses_park_table)
        mapper(self.BusesService, buses_service_table)

        """Создаём сессию"""
        conn = sessionmaker(bind=self.database_engine)
        self.session = conn()
        self.session.commit()

    def add_bus(self, bus_number, name_driver, surname_driver, route_number):
        """Метод регистрации маршрута, добавления транспорта на баланс предприятия"""

        if self.session.query(self.AllBuses).filter_by(bus_number=bus_number).count():
            print(f'аккаунт с номером АМ - {bus_number} уже существует')
        else:
            bus_row = self.AllBuses(bus_number, name_driver, surname_driver, route_number)
            self.session.add(bus_row)
            self.session.commit()
            print('Запись добавлена в БД предприятия')

    def buses_all_list(self):
        """Метод, возвращающий список всего траспорта, находящегося на балансе"""

        # Запрос строк таблицы AllBuses на балансе в парке.
        query = self.session.query(
            self.AllBuses.bus_number,
            self.AllBuses.name_driver,
            self.AllBuses.surname_driver,
            self.AllBuses.route_number
        )
        # Возвращаем список кортежей строк с нужными полями
        return query.all()

    def buses_line_list(self):
        """Метод, возвращающий список всех автобусов, находящихся на маршруте"""
        query = self.session.query(
            self.AllBuses.bus_number,
            self.AllBuses.route_number,
            self.AllBuses.name_driver,
            self.AllBuses.surname_driver,
            self.BusesLine.event_time
        ).join(self.AllBuses)
        return query.all()

    def buses_park_list(self):
        """Метод, возвращающий список всех автобусов, находящихся в парке  (не на линии)"""
        query = self.session.query(
            self.AllBuses.bus_number,
            self.AllBuses.route_number,
            self.AllBuses.name_driver,
            self.AllBuses.surname_driver,
            self.BusesPark.event_time
        ).join(self.AllBuses)
        return query.all()

    def buses_servise_list(self):
        """Метод, возвращающий список всех автобусов, находящихся на сервисном обслуживании в парке"""
        query = self.session.query(
            self.AllBuses.bus_number,
            self.AllBuses.route_number,
            self.AllBuses.name_driver,
            self.AllBuses.surname_driver,
            self.BusesService.event_time
        ).join(self.AllBuses)
        return query.all()

    def search_bus(self, bus_number):
        """Метод, проверяющий существование транспорта в БД предприятия (на балансе), в каком цикле находится"""

        if self.session.query(self.AllBuses).filter_by(bus_number=bus_number).count():
            # забираем все данные по строке bus_number из таблицы AllBuses
            auto = self.session.query(self.AllBuses).filter_by(bus_number=bus_number).first()
            if self.session.query(self.BusesLine).filter_by(auto=auto.id).count():
                return f'{auto} находится на линии'

            if self.session.query(self.BusesPark).filter_by(auto=auto.id).count():
                return f'{auto} находится в парке'

            if self.session.query(self.BusesService).filter_by(auto=auto.id).count():
                return f'{auto} находится на ТО'

            return f'{auto} числится на балансе, но не задействовано в эксплуатации'
        else:

            return f' {bus_number} не числится на балансе предприятия'

    def bus_line(self, bus_number):
        """Метод добавляет аккаунт автобуса в таблицу "На линии" Buses_line"""

        self.delete_bus_list_category(bus_number)
        auto = self.session.query(self.AllBuses).filter_by(bus_number=bus_number).first()
        new_bus_line = self.BusesLine(auto.id, datetime.datetime.now())
        self.session.add(new_bus_line)
        self.session.commit()

    def bus_park(self, bus_number):
        """Метод добавляет аккаунт автобуса в таблицу "В парке" Buses_park"""

        self.delete_bus_list_category(bus_number)
        auto = self.session.query(self.AllBuses).filter_by(bus_number=bus_number).first()
        new_bus_park = self.BusesPark(auto.id, datetime.datetime.now())
        self.session.add(new_bus_park)
        self.session.commit()

    def bus_service(self, bus_number):
        """Метод добавляет аккаунт автобуса в таблицу "На ТО" Buses_service"""

        self.delete_bus_list_category(bus_number)
        auto = self.session.query(self.AllBuses).filter_by(bus_number=bus_number).first()
        new_bus_line = self.BusesService(auto.id, datetime.datetime.now())
        self.session.add(new_bus_line)
        self.session.commit()

    def delete_bus_list_category(self, bus_number):
        """Метод удаляет аккаунт автобуса из всех категорий (очистка). Предотвращает дублирование данных"""
        auto = self.session.query(self.AllBuses).filter_by(bus_number=bus_number).first()
        self.session.query(self.BusesLine).filter_by(auto=auto.id).delete()
        self.session.query(self.BusesPark).filter_by(auto=auto.id).delete()
        self.session.query(self.BusesService).filter_by(auto=auto.id).delete()
        self.session.commit()

    def delete_bus(self, bus_number):
        """Метод удаления транспорта из БД"""
        if self.session.query(self.AllBuses).filter_by(bus_number=bus_number).count():
            # забираем все данные по строке bus_number из таблицы AllBuses
            auto = self.session.query(self.AllBuses).filter_by(bus_number=bus_number).first()
            self.session.query(self.BusesLine).filter_by(auto=auto.id).delete()
            self.session.query(self.BusesPark).filter_by(auto=auto.id).delete()
            self.session.query(self.BusesService).filter_by(auto=auto.id).delete()
            self.session.query(self.AllBuses).filter_by(bus_number=bus_number).delete()
            self.session.commit()
            return f'{bus_number} удален из БД предприяти'

        else:
            return f' {bus_number} не числится на балансе предприятия'

    def start_menu(self):
        """Метод МЕНЮ КОМАНД и логика для консольной версии приложения"""

        action = input(f'введите код действия или число 11 для выхода: \n '
                       f'1 - поиск ТС по госномеру в базе данных (сведения) \n '
                       f'2 - добавление ТС в базу данных \n '
                       f'3 - удаление ТС из БД \n '
                       f'4- открыть полный список ТС (на балансе предприятия) \n '
                       f'5 - открыть список ТС, находящихся НА ЛИНИИ \n '
                       f'6 - открыть список ТС, находящихся В ОЖИДАНИИ РАБОТЫ в парке  \n '
                       f'7 - открыть список ТС, находящихся НА СЕРВИСНОМ ОБСЛУЖИВАНИИ \n '
                       f'8 - добавть ТС в цикл "НА ЛИНИИ" \n '
                       f'9 - добавить ТС в цикл "ЗАХОД В ПАРК (ОЖИДАНИЕ РАБОТЫ)" \n '
                       f'10 - добавить ТС в цикл "ЗАХОД НА ТО" \n '
                       f'11 - ВЫХОД ИЗ ПРОГРАММЫ \n ')
        try:
            act_int = int(action)
            if act_int == 11:
                print('Пользователем осуществлен выход из программы')
                sys.exit(0)
            if act_int in range(1, 11):
                if act_int == 1:
                    bus = int(input('Введите цифры госномера искомого ТС - '))
                    auto_search = self.search_bus(bus)
                    print(auto_search)
                    self.start_menu()

                elif act_int == 2:
                    self.add_bus(bus_number=input('Введите цифры госномера ТС - '),
                                 name_driver=input('Введите имя водителя ТС - '),
                                 surname_driver=input('Введите фимилию водителя ТС - '),
                                 route_number=input('Введите номер маршрута - '))

                    req = input(f'Для продолжения ввода данных введите - 1 \n'
                                f'Для выхода из операции ввода нажмите любую клавишу \n')
                    req_int = int(req)
                    if req_int == 1:
                        self.add_bus(bus_number=input('Введите цифры госномера ТС - '),
                                     name_driver=input('Введите имя водителя ТС - '),
                                     surname_driver=input('Введите фимилию водителя ТС - '),
                                     route_number=input('Введите номер маршрута - '))
                    else:
                        self.start_menu()

                elif act_int == 3:
                    bus_del = int(input('Введите цифры госномера ТС для удаления из БД - '))
                    self.delete_bus(bus_del)
                    print(f'ТС с госномером - {bus_del} удален из БД предприятия')
                    self.start_menu()

                elif act_int == 4:
                    list_all = self.buses_all_list()
                    print(f'Весь транспорт на балансе предприятия {list_all}')
                    self.start_menu()

                elif act_int == 5:
                    list_line = self.buses_line_list()
                    if len(list_line) == 0:
                        print('НА ЛИНИИ не числится машин')
                    else:
                        print(f'На ЛИНИИ  {list_line}')
                    self.start_menu()

                elif act_int == 6:
                    list_park = self.buses_park_list()
                    if len(list_park) == 0:
                        print('В ОЖИДАНИИ РАБОТЫ в парке не числится машин')
                    else:
                        print(f'В ОЖИДАНИИ РАБОТЫ в парке  {list_park}')
                    self.start_menu()

                elif act_int == 7:
                    list_serv = self.buses_servise_list()
                    if len(list_serv) == 0:
                        print('НА СЕРВИСНОМ ОБСЛУЖИВАНИИ машин не числится')
                    else:
                        print(f'На СЕРВИСНОМ ОБСЛЕЖИВАНИИ {list_serv}')
                    self.start_menu()

                elif act_int == 8:
                    bus_line = int(input('Введите цифры госномера ТС для выпуска НА ЛИНИЮ - '))
                    self.delete_bus_list_category(bus_line)
                    self.bus_line(bus_line)
                    print(f'ТС с госномером - {bus_line} выведен НА ЛИНИЮ')
                    self.start_menu()

                elif act_int == 9:
                    bus_park = int(input('Введите цифры госномера ТС для захода в парк В ОЖИДАНИИ РАБОТЫ - '))
                    self.delete_bus_list_category(bus_park)
                    self.bus_park(bus_park)
                    print(f'ТС с госномером - {bus_park} добавлено в парк В ОЖИДАНИИ РАБОТЫ')
                    self.start_menu()

                elif act_int == 10:
                    bus_serv = int(input('Введите цифры номера ТС для добавления в цикл НА СЕРВИСНОМ ОБСЛУЖИВАНИИ - '))
                    self.delete_bus_list_category(bus_serv)
                    self.bus_service(bus_serv)
                    print(f'ТС с госномером - {bus_serv} отправлено НА СЕРВИСНОЕ ОБСЛУЖИВАНИЕ')
                    self.start_menu()
            else:
                return print('Введен ошибочный код, ведите числовой код команды из меню или число 11 для выхода'), \
                       self.start_menu()
        except ValueError:
            return print('Введен ошибочный код, ведите числовой код команды из меню или число 11 для выхода'), \
                   self.start_menu()


if __name__ == '__main__':
    conn = BusParkStorage('test_db_1')  # Подключение к БД. Если не создана - создается.
    conn.start_menu()  # Запуск метода для консольной версии

