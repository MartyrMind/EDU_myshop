from decimal import Decimal

from coupons.models import Coupon
from myshop import settings
from shop.models import Product


class Cart:
    def __init__(self, request):
        # инициализируем корзину
        self.session = request.session  # сохранили текущий сеанс
        cart = self.session.get(settings.CART_SESSION_ID)  # получили корзину
        if not cart:
            # создаем пустую корзину в сеансе
            cart = self.session[settings.CART_SESSION_ID] = {}
        self.cart = cart
        # сохраним текущий примененный купон
        self.coupon_id = self.session.get('coupon_id')

    def add(self, product, quantity=1, override_quantity=False):
        # конвертируем в строку, потому что JSON допускает только строковые имена кключей
        product_id = str(product.id)
        if product_id not in self.cart:
            self.cart[product_id] = {'quantity': 0, 'price': str(product.price)}
        if override_quantity:
            self.cart[product_id]['quantity'] = quantity
        else:
            self.cart[product_id]['quantity'] += quantity
        self.save()

    def save(self):
        # помечаем сеанс как измененный, чтобы он сохранился
        self.session.modified = True

    def remove(self, product):
        product_id = str(product.id)
        if product_id in self.cart:
            del self.cart[product_id]
            self.save()

    def __iter__(self):
        product_ids = self.cart.keys()
        products = Product.objects.filter(id__in=product_ids)
        cart = self.cart.copy()  # скопировали существующую корзину
        for product in products:
            # добавим в копию экземпляры класса Product
            cart[str(product.id)]['product'] = product
        for item in cart.values():  # добавим новые данные
            # сконвертировали цену в тип Decimal
            item['price'] = Decimal(item['price'])
            # посчитали итоговую стоимость
            item['total_price'] = item['price'] * item['quantity']
            # корзина выглядит так:
            # {
            #   'quantity': int
            #   'price': Decimal
            #   'product': Product
            #   'total_price': Decimal
            # }
            yield item

    def __len__(self):
        # считаем общее число товаров в корзине
        return sum(item['quantity'] for item in self.cart.values())

    def get_total_price(self):
        return sum(Decimal(item['price']) * item['quantity'] for item in self.cart.values())

    def clear(self):
        del self.session[settings.CART_SESSION_ID]
        self.save()

    @property
    def coupon(self):
        if self.coupon_id:
            try:
                return Coupon.objects.get(id=self.coupon_id)
            except Coupon.DoesNotExist:
                pass
        return None

    def get_discount(self):
        if self.coupon:
            return (self.coupon.discount / Decimal(100)) * self.get_total_price()
        return Decimal(0)

    def get_total_price_after_discount(self):
        return self.get_total_price() - self.get_discount()
