from django import forms

PRODUCT_QUANTITY_CHOICES = [(i, str(i)) for i in range(1, 21)]


class CartAddProductForm(forms.Form):
    # выбор количества товаров
    # хотим сконвертировать входные данные в целое число, поэтому используем параметр coerce
    quantity = forms.TypedChoiceField(choices=PRODUCT_QUANTITY_CHOICES, coerce=int)
    # позволяет указывать, будет ли количество продуктов добавляться к уже существующему количеству
    # или будет его перезаписывать
    override = forms.BooleanField(required=False, initial=False, widget=forms.HiddenInput)
