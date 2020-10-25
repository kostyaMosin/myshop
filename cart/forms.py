from django import forms

# Генерируем список кортежей - [(1, '1'), (2, '2'), (3, '3'), ...., (20, '20')]
PRODUCT_QUANTITY_CHOICES = [(i, str(i)) for i in range(1, 21)]


class CartAddProductForm(forms.Form):
    # quantity позволяет пользователю выбрать количество товара от 1-20.
    # coerce=int - для преобразования ввода в целое число
    quantity = forms.TypedChoiceField(choices=PRODUCT_QUANTITY_CHOICES, coerce=int)
    # Позволяет указать, следует ли добавлять сумму к любому существующему значению
    # в корзине для данного продукта (False) или если существующее значение должно
    # быть обновлено с заданным значением (True). Для этого поля используется графический
    # элемент HiddenInput, поскольку не требуется показывать его пользователю.
    update = forms.BooleanField(required=False, initial=False, widget=forms.HiddenInput)
