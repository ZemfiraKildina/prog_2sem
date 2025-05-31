from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, Table
from sqlalchemy.orm import DeclarativeBase, relationship, Session

# Подключение к SQLite (или поменяйте на нужную вам БД)
engine = create_engine('sqlite:///restaurant.db')

class Base(DeclarativeBase):
    pass

# Промежуточная таблица многие-ко-многим
order_dish = Table(
    'order_dish',
    Base.metadata,
    Column('order_id', ForeignKey('orders.id'), primary_key=True),
    Column('dish_id', ForeignKey('dishes.id'), primary_key=True)
)

class TableInRestaurant(Base):
    __tablename__ = "tables"
    id = Column(Integer, primary_key=True)
    number = Column(Integer, unique=True, nullable=False)

    orders = relationship("Order", back_populates="table")

class Order(Base):
    __tablename__ = "orders"
    id = Column(Integer, primary_key=True)
    table_id = Column(Integer, ForeignKey("tables.id"))

    table = relationship("TableInRestaurant", back_populates="orders")
    dishes = relationship("Dish", secondary=order_dish, back_populates="orders")

class Dish(Base):
    __tablename__ = "dishes"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    price = Column(Integer, nullable=False)

    orders = relationship("Order", secondary=order_dish, back_populates="dishes")

# Создаём таблицы
Base.metadata.create_all(bind=engine)