from django import forms

class OrderForm(forms.Form):
	first_name = forms.CharField()
	last_name = forms.CharField(required=False)
	phone = forms.CharField()
	buying_type = forms.ChoiceField(widget=forms.Select(), choices=([('Доставка', 'Доставка'),
    															('Самовывоз', 'Самовывоз')]))
	date_delivery = forms.DateTimeField(
        input_formats=['%d/%m/%Y %H:%M'],
        widget=forms.DateTimeInput(attrs={
            'class': 'form-control datetimepicker-input',
            'data-target': '#datetimepicker1'
        })
    )
	address = forms.CharField(required=False)
	comments = forms.CharField(widget=forms.Textarea(), required=False)


	def __init__(self, *args, **kwargs):
		super(OrderForm, self).__init__(*args, **kwargs)
		self.fields['first_name'].label = 'Имя'
		self.fields['last_name'].label = 'Фамилия'
		self.fields['phone'].label = 'Контактный телефон'
		self.fields['phone'].help_text = 'Пожалуйста, указывайте реальный номер телефона, по которому с Вами можно связаться'
		self.fields['buying_type'].label = 'Способ получения'
		self.fields['address'].label = 'Адрес доставки'
		self.fields['address'].help_text = '*Обязательно указывайте город!'
		self.fields['comments'].label = 'Коментарии к заказу (по желанию)'
		self.fields['date_delivery'].label = 'Желаемая дата доставки'
		self.fields['date_delivery'].help_text = 'Доставка производится на следующий день после заказа. Менеджер свяжется с вами предварительно'


class CartAddProductForm(forms.Form):
	quantity = forms.IntegerField(required=False, label='Количество:', 
									widget=forms.NumberInput(attrs={
		'class': 'cart-item-quantity-in-product',
		'value': '1',
		'min': '1',
		})
	)