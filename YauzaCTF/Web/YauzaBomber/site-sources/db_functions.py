import datetime

from flask_sqlalchemy import SQLAlchemy

from app import app
import time

from random import randint

db = SQLAlchemy(app)


class Database:

    def __init__(self):
        pass

    #######################################
    #                Tables               #
    #######################################

    class User(db.Model):
        __tablename__ = 'users'

        id = db.Column(db.Integer, db.Sequence('id'), primary_key=True, autoincrement=True, nullable=False)
        login = db.Column('login', db.Text, unique=True)
        password = db.Column('password', db.Text)
        phone = db.Column('phone', db.Text)
        money = db.Column('money', db.Float, default=15)
        __table_args__ = (db.UniqueConstraint('id'),)

        def __init__(self, login='', password=''):
            self.login = login
            self.password = password

        def get_user_by_creds(self, login, password):
            return self.query.filter_by(login=login, password=password).first()

        def get_user_by_phone(self, phone):
            return self.query.filter_by(phone=phone).first()

        def get_user_by_id(self, id):
            return self.query.filter_by(id=id).first()

        def get_user_by_login(self, login):
            return self.query.filter_by(login=login).first()

        def users_top(self):
            return self.query.order_by(Database.User.money.desc()).limit(10).all()

        def create_user(self, login, password):
            if self.get_user_by_login(login=login):
                return None
            try:
                user_obj = Database.User(login=login, password=password)
                db.session.add(user_obj)
                db.session.commit()
                db.session.refresh(user_obj)
                user_obj.phone = '+1337-({:03d})-{:06d}'.format(int(user_obj.id), randint(0, 999999))
                db.session.commit()
                return user_obj
            except ValueError:
                print('Error!')

        def update_password(self, login, old_password, new_password):
            user_obj = self.get_user_by_creds(login, old_password)
            if user_obj:
                user_obj.password = new_password
                db.session.commit()
                db.session.refresh(user_obj)
                return user_obj

        def add_money_to_login(self, login, money):
            user_obj = self.get_user_by_login(login)
            if user_obj:
                user_obj.money += money
                db.session.commit()
                db.session.refresh(user_obj)

        def delete_login(self, login):
            user_obj = self.get_user_by_login(login)
            if user_obj:
                self.query.filter_by(login=login).delete()
                db.session.commit()

    class Message(db.Model):
        __tablename__ = 'messages'

        id = db.Column(db.Integer, primary_key=True, autoincrement=True)
        sender_id = db.Column('sender_id', db.Integer)
        sender_phone = db.Column('sender_phone', db.Text)  # if empty - its chat message
        text = db.Column('text', db.Text)
        time = db.Column('time', db.DateTime)
        receiver_phone = db.Column('receiver_phone', db.Text, default='')
        receiver_id = db.Column('receiver_id', db.Integer, default=0)

        def __init__(self, sender_id=0, sender_phone='', text='', time=0, receiver_phone='', receiver_id=0):
            self.sender_id = sender_id
            self.text = text
            self.sender_phone = sender_phone
            if not time:
                self.time = datetime.datetime.now()
            elif type(time) == int:
                self.time = datetime.datetime.utcfromtimestamp(time)
            elif type(time) == datetime.datetime:
                self.time = time
            self.receiver_phone = receiver_phone
            self.receiver_id = receiver_id

        def get_last_chat(self, amount=10):
            return self.query.order_by(Database.Message.id.desc()).limit(amount).all()[::-1]

        def sent_chat(self, user_obj, message):
            msg_obj = Database.Message(sender_id=user_obj.id,
                                       sender_phone=user_obj.phone,
                                       text=message)
            db.session.add(msg_obj)
            db.session.commit()
            return msg_obj

        def send_sms(self, user_obj, phone, message):
            msg_obj = Database.Message(sender_id=user_obj.id,
                                       sender_phone=user_obj.phone,
                                       text=message,
                                       receiver_phone=phone)
            db.session.add(msg_obj)
            db.session.commit()
            return msg_obj

        def send_private(self, user_obj, phone, message):
            recv_obj = Database.User().get_user_by_phone(phone)
            if not recv_obj:
                return None
            msg_obj = Database.Message(sender_id=user_obj.id,
                                       sender_phone=user_obj.phone,
                                       text=message,
                                       receiver_phone=phone,
                                       receiver_id=recv_obj.id)
            db.session.add(msg_obj)
            db.session.commit()
            return msg_obj

        def list_sms(self, user_obj):
            messages = self.query.filter_by(Database.Message.sender_id == user_obj.id and
                                            Database.Message.receiver_id == 0).all()
            return messages

        def list_private(self, user_obj):
            messages = self.query.filter_by(Database.Message.sender_id == user_obj.id and
                                            Database.Message.receiver_id != 0).all()
            return messages

        def list_sms_recv(self, user_obj):
            sms_recvs = db.session.query(Database.Message) \
                .distinct(Database.Message.receiver_phone) \
                .filter((Database.Message.sender_id == user_obj.id),
                        Database.Message.receiver_id == 0).all()
            return sms_recvs

        def list_private_recv(self, user_obj):
            private_recvs = db.session.query(Database.Message.receiver_phone, Database.Message.receiver_id) \
                .distinct(Database.Message.receiver_phone) \
                .filter(Database.Message.receiver_id == user_obj.id,
                        Database.Message.receiver_id != 0).all()

            private_send = db.session.query(Database.Message.sender_phone, Database.Message.sender_id) \
                .filter(Database.Message.sender_id == user_obj.id,
                        Database.Message.receiver_id != 0).all()

            result = private_recvs + private_send

            return list(set(result))

        def get_sms_by_msg(self, user_obj, msg_obj):
            sms_recvs = db.session.query(Database.Message) \
                .filter((Database.Message.sender_id == user_obj.id) | (Database.Message.receiver_id == user_obj.id),
                        Database.Message.receiver_id == 0,
                        Database.Message.receiver_phone == msg_obj.receiver_phone).all()
            return sms_recvs

        def get_private_by_msg(self, user_obj, phone):
            private_recvs = db.session.query(Database.Message) \
                .filter((Database.Message.sender_id == user_obj.id) | (Database.Message.receiver_id == user_obj.id),
                        (Database.Message.sender_phone == phone) | (Database.Message.receiver_phone == phone),
                        Database.Message.receiver_id != 0).all()
            return private_recvs

    class ShopItem(db.Model):
        __tablename__ = 'shop'

        id = db.Column(db.Integer, primary_key=True, autoincrement=True)
        phone = db.Column('phone', db.Text)
        description = db.Column('description', db.Text)
        price = db.Column('price', db.Float, default=15)
        count = db.Column('count', db.Integer, default=1)

        def __init__(self, phone='', description='', price=15, count=1):
            self.phone = phone
            self.description = description
            self.price = price
            self.count = count

        def list_items(self, min_count=1):
            return self.query.filter(Database.ShopItem.count >= min_count)

        def get_item_by_id(self, id):
            return self.query.filter_by(id=id).first()

        def buy_item(self, item_id, user_id):
            user_obj = Database.User().get_user_by_id(user_id)
            item_obj = self.get_item_by_id(item_id)
            if item_obj.count < 1:
                return (None, None)
            if item_obj.price > user_obj.money:
                return (None, None)
            if item_obj.phone == '+7777-(777)-777777':
                return (user_obj, item_obj)
            user_obj.phone = item_obj.phone
            item_obj.count -= 1
            user_obj.money -= item_obj.price
            db.session.commit()
            db.session.refresh(user_obj)
            return (user_obj, item_obj)

        def add_random_number(self, amount=1, price=15):

            phone = '+1337-({:03d})-{:06d}'.format(randint(0, 999), randint(0, 999999))
            item_obj = Database.ShopItem(phone=phone,
                                         description='VIP numper for your phone!',
                                         price=randint(1, 15), count=1)
            db.session.add(item_obj)
            db.session.commit()
            return

        def add_number(self, number='', amount=1, price=15):

            item_obj = Database.ShopItem(phone=number,
                                         description='VIP numper for your phone!',
                                         price=price, count=amount)
            db.session.add(item_obj)
            db.session.commit()
            return

        def update_shop(self):
            shop_items = self.query.filter(Database.ShopItem.count > 0).all()
            if len(shop_items) < 10:
                for x in range(10 - len(shop_items)):
                    self.add_random_number()


db.create_all()
