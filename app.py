from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import and_
from datetime import datetime
from file_read import file_read


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:' # lesson_db.db
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JSON_AS_ASCII'] = False


db = SQLAlchemy(app)


class User(db.Model):
    """Класс пользователь"""
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.Text(200))
    last_name = db.Column(db.Text(200))
    age = db.Column(db.Integer)
    email = db.Column(db.Text(200))
    role = db.Column(db.Text(50))
    phone = db.Column(db.Text(50))


class Order(db.Model):
    """Класс заказ"""
    __tablename__ = 'order'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text(200))
    description = db.Column(db.Text(500))
    start_date = db.Column(db.DateTime)
    end_date = db.Column(db.DateTime)
    address = db.Column(db.Text(200))
    price = db.Column(db.Integer)
    customer_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete="CASCADE"))
    executor_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    customer = db.relationship('User', foreign_keys='Order.customer_id')
    executor = db.relationship('User', foreign_keys='Order.executor_id')


class Offer(db.Model):
    """Класс предложение"""
    __tablename__ = 'offer'
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id', ondelete="CASCADE"))
    executor_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete="CASCADE"))
    user = db.relationship('User')
    order = db.relationship('Order')


# создаем все таблицы в БД
db.create_all()

# Имена файлов с данными
file_name_users = 'users.json'
file_name_orders = 'orders.json'
file_name_offers = 'offers.json'

file_names = [file_name_users, file_name_orders, file_name_offers]

# чтение данных из файлов
main_data = file_read(file_names)
users = main_data[0]
orders = main_data[1]
offers = main_data[2]

users_list = []
orders_list = []
offers_list = []

# создаем экземпляры класса Пользователь на основании данных из файла
for user in users:
    temp_user = User(id=user.get('id'),
                     first_name=user.get('first_name'),
                     last_name=user.get('last_name'),
                     age=user.get('age'),
                     email=user.get('email'),
                     role=user.get('role'),
                     phone=user.get('phone'))
    users_list.append(temp_user)

# создаем экземпляры класса Заказ на основании данных из файла
for order in orders:
    start_date_temp = order.get('start_date')
    start_date = datetime.strptime(start_date_temp, '%m/%d/%Y').date()

    end_date_temp = order.get('end_date')
    end_date = datetime.strptime(end_date_temp, '%m/%d/%Y').date()

    temp_order = Order(id=order.get('id'),
                       name=order.get('name'),
                       description=order.get('description'),
                       start_date=start_date,
                       end_date=end_date,
                       address=order.get('address'),
                       price=order.get('price'),
                       customer_id=order.get('customer_id'),
                       executor_id=order.get('executor_id')
                       )
    orders_list.append(temp_order)

# создаем экземпляры класса Предложение на основании данных из файла
for offer in offers:
    temp_offer = Offer(id=offer.get('id'),
                       order_id=offer.get('order_id'),
                       executor_id=offer.get('executor_id'),
                       )
    offers_list.append(temp_offer)

db.session.add_all(users_list)
db.session.add_all(orders_list)
db.session.add_all(offers_list)
db.session.commit()
db.session.close()


@app.route('/users/', methods=['GET', 'POST'])
def users():
    """виды для пользователей - все и добавление нового"""
    if request.method == 'POST':
        data = request.json
        all_users = db.session.query(User).all()
        all_users_id = []
        for user_ in all_users:
            all_users_id.append(user_.id)
        if data.get('id') not in all_users_id:
            new_user = User(id=data.get('id'),
                            first_name=data.get('first_name'),
                            last_name=data.get('last_name'),
                            age=data.get('age'),
                            email=data.get('email'),
                            role=data.get('role'),
                            phone=data.get('phone'))
            db.session.add(new_user)
            db.session.commit()
            db.session.close()
            return f"User {data.get('id')} created"
        else:
            return f"User with id {data.get('id')} already exists"

    elif request.method == 'GET':
        all_users = db.session.query(User).all()
        all_users_list = []
        for user_ in all_users:
            temp_dict = {}
            temp_dict['id'] = user_.id
            temp_dict['age'] = user_.age
            temp_dict['first_name'] = user_.first_name
            temp_dict['last_name'] = user_.last_name
            temp_dict['last_name'] = user_.last_name
            temp_dict['email'] = user_.email
            temp_dict['phone'] = user_.phone
            all_users_list.append(temp_dict)
        return jsonify(all_users_list)
    return 'Unknown type request'


@app.route('/users/<int:uid>/', methods=['GET', 'PUT', 'DELETE'])
def users_id(uid):
    """одиночный пользователь. получение, изменение и удаление"""
    all_users = db.session.query(User).filter(User.id == uid).first()
    if all_users:
        if request.method == 'GET':
            temp_dict = {}
            temp_dict['id'] = all_users.id
            temp_dict['age'] = all_users.age
            temp_dict['first_name'] = all_users.first_name
            temp_dict['last_name'] = all_users.last_name
            temp_dict['last_name'] = all_users.last_name
            temp_dict['email'] = all_users.email
            temp_dict['phone'] = all_users.phone
            return jsonify(temp_dict)

        elif request.method == 'DELETE':
            item_del = User.query.get(uid)
            db.session.delete(item_del)
            db.session.commit()
            db.session.close()
            return f'Item - {uid} removed from DB'
        elif request.method == 'PUT':
            item_put = User.query.get(uid)
            new_data = request.json

            item_put.first_name = new_data.get('first_name')
            item_put.last_name = new_data.get('last_name')
            item_put.age = new_data.get('age')
            item_put.email = new_data.get('email')
            item_put.role = new_data.get('role')
            item_put.phone = new_data.get('phone')

            db.session.add(item_put)
            db.session.commit()
            db.session.close()
            return f'Item {uid} changed'

        return 'Unknown type request'
    return 'Not found'


@app.route('/orders/', methods=['GET', 'POST'])
def orders():
    if request.method == 'POST':
        data = request.json
        all_orders = db.session.query(Order).all()
        all_orders_id = []
        for order_ in all_orders:
            all_orders_id.append(order_.id)
        if data.get('id') not in all_orders_id:
            start_date_temp = data.get('start_date')
            start_date = datetime.strptime(start_date_temp, '%m/%d/%Y').date()
            end_date_temp = data.get('end_date')
            end_date = datetime.strptime(end_date_temp, '%m/%d/%Y').date()

            new_order = Order(id=data.get('id'),
                              name=data.get('name'),
                              description=data.get('description'),
                              start_date=start_date,
                              end_date=end_date,
                              address=data.get('address'),
                              price=data.get('price'),
                              customer_id=data.get('customer_id'),
                              executor_id=data.get('executor_id'))
            db.session.add(new_order)
            db.session.commit()
            db.session.close()
            return f"Order {data.get('id')} created"
        else:
            return f"Order with id {data.get('id')} already exists"
    elif request.method == 'GET':
        all_orders = db.session.query(Order.id, Order.name, Order.address,
                                      Order.price, User.id.label("user_id"), User.first_name, User.last_name).\
            join(User, and_(Order.customer_id == User.id)).all()
        all_orders_list = []
        for order_ in all_orders:
            temp_dict = {}
            temp_dict['id'] = order_.id
            temp_dict['name'] = order_.name
            temp_dict['address'] = order_.address
            temp_dict['price'] = order_.price
            temp_dict['customer_name'] = order_.first_name
            all_orders_list.append(temp_dict)
        return jsonify(all_orders_list)
    return 'Unknown type request'


@app.route('/orders/<int:uid>/', methods=['GET', 'PUT', 'DELETE'])
def orders_id(uid):
    all_orders = db.session.query(Order.id, Order.name, User.id.label("user_id"), User.first_name, User.last_name). \
        filter(Order.id == uid).join(User, and_(Order.customer_id == User.id)).first()
    if all_orders:
        if request.method == 'GET':
            temp_table = {}
            temp_table['Order_id'] = all_orders.id
            temp_table['Order_name'] = all_orders.name
            temp_table['customer_name'] = all_orders.first_name
            temp_table['last_name'] = all_orders.last_name
            temp_table['user_id'] = all_orders.user_id
            return jsonify(temp_table)
        elif request.method == 'DELETE':
            item_del = Order.query.get(uid)
            db.session.delete(item_del)
            db.session.commit()
            db.session.close()
            return f'Item - {uid} removed from DB'
        elif request.method == 'PUT':
            item_put = Order.query.get(uid)
            new_data = request.json

            start_date_temp = new_data.get('start_date')
            start_date = datetime.strptime(start_date_temp, '%m/%d/%Y').date()
            end_date_temp = new_data.get('end_date')
            end_date = datetime.strptime(end_date_temp, '%m/%d/%Y').date()

            item_put.name = new_data.get('name')
            item_put.description = new_data.get('description')
            item_put.start_date = start_date
            item_put.end_date = end_date
            item_put.address = new_data.get('address')
            item_put.price = new_data.get('price')
            item_put.customer_id = new_data.get('customer_id')
            item_put.executor_id = new_data.get('executor_id')

            db.session.add(item_put)
            db.session.commit()
            db.session.close()
            return f'Item {uid} changed'
    return 'Not found'


@app.route('/offers/', methods=['GET', 'POST'])
def offers():
    if request.method == 'POST':
        data = request.json
        all_offers = db.session.query(Offer).all()
        all_offers_id = []
        for order_ in all_offers:
            all_offers_id.append(order_.id)
        if data.get('id') not in all_offers_id:

            new_offer = Offer(id=data.get('id'),
                              order_id=data.get('order_id'),
                              executor_id=data.get('executor_id'))
            db.session.add(new_offer)
            db.session.commit()
            db.session.close()
            return f"Offer {data.get('id')} created"
        else:
            return f"Offer with id {data.get('id')} already exists"
    elif request.method == 'GET':
        all_offers = db.session.query(Offer.id, Offer.order_id, Offer.executor_id,
                                      Order.name).\
            join(Order, and_(Offer.order_id == Order.id)).all()
        all_offers_list = []
        for offer_ in all_offers:
            temp_dict = {}
            temp_dict['id'] = offer_.id
            temp_dict['order_id'] = offer_.order_id
            temp_dict['executor_id'] = offer_.executor_id
            temp_dict['name'] = offer_.name
            all_offers_list.append(temp_dict)
        return jsonify(all_offers_list)
    return 'Unknown type request'


@app.route('/offers/<int:uid>', methods=['GET', 'PUT', 'DELETE'])
def offers_id(uid):
    all_offers = db.session.query(Offer).filter(Offer.id == uid).first()
    if all_offers:
        if request.method == 'GET':
            offer_ = Offer.query.get(uid)
            temp_dict = {}
            temp_dict['id'] = offer_.id
            temp_dict['order_id'] = offer_.order_id
            temp_dict['executor_id'] = offer_.executor_id
            return jsonify(temp_dict)
        elif request.method == 'DELETE':
            offer_ = Offer.query.get(uid)
            db.session.delete(offer_)
            db.session.commit()
            db.session.close()
            return f'Item {uid} removed from DB'
        elif request.method == 'PUT':
            item_put = Offer.query.get(uid)
            new_data = request.json

            item_put.id = new_data.get('id')
            item_put.order_id = new_data.get('order_id')
            item_put.executor_id = new_data.get('executor_id')

            db.session.add(item_put)
            db.session.commit()
            db.session.close()
            return f'Item {uid} changed'
    return 'Not found'


if __name__ == '__main__':
    app.run()
