from models import engine, TableInRestaurant, Order, Dish, Session

with Session(engine) as session:
    # Создаём столики
    t1 = TableInRestaurant(number=1)
    t2 = TableInRestaurant(number=2)
    # Создаём блюда
    d1 = Dish(name="Борщ", price=300)
    d2 = Dish(name="Пельмени", price=400)
    d3 = Dish(name="Салат", price=200)
    # Создаём заказы
    o1 = Order(table=t1, dishes=[d1, d2])
    o2 = Order(table=t1, dishes=[d2, d3])
    o3 = Order(table=t2, dishes=[d1, d3])
    session.add_all([t1, t2, d1, d2, d3, o1, o2, o3])
    session.commit()

# Все заказы для каждого столика

with Session(engine) as session:
    tables = session.query(TableInRestaurant).all()
    for table in tables:
        print(f"Столик {table.number}:")
        for order in table.orders:
            print(f"  Заказ {order.id}: {[dish.name for dish in order.dishes]}")

# Все блюда, которые были заказаны хотя бы раз

with Session(engine) as session:
    dishes = session.query(Dish).filter(Dish.orders.any()).all()
    for d in dishes:
        print(f"{d.name} — заказов: {len(d.orders)}")

# Анализ: общее количество заказов, сумма всех заказов по столикам

with Session(engine) as session:
    for table in session.query(TableInRestaurant):
        total = 0
        for order in table.orders:
            total += sum(dish.price for dish in order.dishes)
        print(f"Столик {table.number}: сумма заказов = {total}")