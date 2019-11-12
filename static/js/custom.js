$(document).ready(function(){
	$('.add-to-cart-btn').on('click', function(e){
		e.preventDefault()
		product_slug = $(this).attr('data-slug')
		data = {
			product_slug: product_slug
		}
		$.ajax({
			type : "GET",
			url : "{% url 'ecomapp:add_to_cart' %}",
			data : data,
			success: function(data){
				$('#cart_count').html(data.cart_total)
			}
		})
	});
});