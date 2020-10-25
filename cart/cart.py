from decimal import Decimal
from django.conf import settings
from shop.models import Product


class Cart(object):

    def __init__(self, request):
        """
        Инициализируем корзину, с помощью объекта request
        """
        # Сохраняем текущую сессию, для использования ее другими методами класса Cart
        self.session = request.session
        # Пытаемся получить корзину из текущей сессии
        cart = self.session.get(settings.CART_SESSION_ID)
        if not cart:
            # Если в сессии отсутствует корзина, то мы создадим сессию с пустой корзиной,
            # установив пустой словарь в сессии, по ключу 'cart' из переменной CART_SESSION_ID
            cart = self.session[settings.CART_SESSION_ID] = {}
        # Делаем корзину доступной для остальных методов класса Cart
        self.cart = cart

    def add(self, product, quantity=1, update_quantity=False):
        """
        Добавить продукт в корзину или обновить его количество.

        :param product: экземпляр модели Product для добавления ил обновления в корзине
        :param quantity: Необязательное целое чило для количества продукта.
        :param update_quantity: логическое значение, указывающее требуется обновление кол-ва (True),
               или же добавление нового кол-ва к существующему значению (False)
        """
        # Преобразуем id(pk) продукта в строку, т.к. id используется в качестве ключа в словаре
        # содержимого(JSON) корзины. так как Джанго использует JSON для сериализации данных сессии,
        # а JSON разрешает только имена строк.
        product_id = str(product.pk)
        # Если товара нет в корзине
        if product_id not in self.cart:
            # Присваиваем по id товара, значения кол-ва и цены, цену преобразовываем
            # в строку для сериализации
            self.cart[product_id] = {'quantity': 0,
                                     'price': str(product.price)}
        # Если updated_quantity = True, то обновляем количество товара в корзине
        if update_quantity:
            self.cart[product_id]['quantity'] = quantity
        # Если updated_quantity = Else, то увеличеваем количество товара в корзине на количество quantity
        else:
            self.cart[product_id]['quantity'] += quantity
        # Сохраняем корзину в сессии
        self.save()

    def save(self):
        """
        Метод сохраняет все изменения в корзине в сессии,
        и помечает сессию как modified с помощью session.modified = True

        """
        # Обновление сессии cart
        self.session[settings.CART_SESSION_ID] = self.cart
        # Отметить сеанс как "измененный", чтобы убедиться, что он сохранен
        self.session.modified = True

    def remove(self, product):
        """
        Удаление товара из корзины, метод удаляет заданный товар по ключу(id)
        и сохраняет корзину тем самым обновляя ее

        :param product: экземпляр модели Product для удаления из корзины.
        """
        product_id = str(product.pk)
        if product_id in self.cart:
            del self.cart[product_id]
            self.save()

    def __iter__(self):
        """
        Перебор элементов в корзине и получение продуктов из БД.
        """

        product_ids = self.cart.keys()
        # получение объектов product и добавление их в корзину
        products = Product.objects.filter(id__in=product_ids)
        # Извлекаем экземпляры продукта, присутствующие в корзине,
        # чтобы включить их в номенклатуру корзины
        for product in products:
            self.cart[str(product.pk)]['product'] = product
        # проходим по элементам корзины, преобразуя цену номенклатуры
        # обратно в десятичное число и добавляя атрибут total_price к каждому элементу
        for item in self.cart.values():
            item['price'] = Decimal(item['price'])
            item['total_price'] = item['price'] * item['quantity']
            yield item

    def __len__(self):
        """
        Подсчет всех товаров в корзине.
        """
        return sum(item['quantity'] for item in self.cart.values())

    def get_total_price(self):
        """
        Подсчет стоимости товаров в корзине
        """
        return sum(Decimal(item['price']) * item['quantity'] for item in self.cart.values())

    def clear(self):
        """
        Метод для очистки сеанса корзины
        """
        # удаление корзины из сессии
        del self.session[settings.CART_SESSION_ID]
        self.session.modified = True
