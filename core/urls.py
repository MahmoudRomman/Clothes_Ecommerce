from django.urls import path
from . import views


app_name = 'core'

urlpatterns = [
    path('', views.HomeView.as_view(), name="home"), 
    path('checkout/', views.CheckoutView.as_view(), name="checkout"), 
    

    path(
        "create-checkout-session/",
        views.CreateStripeCheckoutSessionView.as_view(),
        name="create-checkout-session",
          ),
    
    path("success/", views.SuccessView.as_view(), name="success"),
    path("cancel/", views.CancelView.as_view(), name="cancel"),
    


    path('order-summary/', views.OrderSummaryView.as_view(), name="order-summary"), 
    path('product/<slug>/', views.ProductDetailView.as_view(), name="product"),
    path('add-to-cart/<slug>/', views.add_to_cart, name="add-to-cart"),
    path('add-coupon/', views.add_coupon, name='add-coupon'),
    path('remove-from-cart/<slug>/', views.remove_from_cart, name="remove-from-cart"),
    path('remove-single-item-from-cart/<slug>/', views.remove_single_item_from_cart, name="remove-single-item-from-cart"),
    path('request-refund/', views.RequestRefundView.as_view(), name="request-refund"),
    path('confirm-refund/', views.ConfirmRefundView.as_view(), name="confirm-refund"),




    path('shirts/', views.ShirtsView.as_view(), name="shirts_filter"),
    path('sports_wear/', views.Sport_WearView.as_view(), name="sports_wear"),
    path('out_wear/', views.Out_WearView.as_view(), name="out_wear"),






] 
