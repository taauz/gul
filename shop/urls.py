from django.urls import path

from . import auth_api, panel_views as pv, views

urlpatterns = [
    path("", views.home, name="home"),

    # JSON API
    path("api/flower/<int:pk>/comment/", views.add_comment, name="add_comment"),
    path("api/flower/<int:pk>/rating/", views.add_rating, name="add_rating"),
    path("api/order/", views.create_order, name="create_order"),
    path("api/my-orders/", views.my_orders, name="my_orders"),
    path("api/auth/send-code/", auth_api.send_code, name="auth_send_code"),
    path("api/auth/verify/", auth_api.verify_code, name="auth_verify"),
    path("api/auth/google/", auth_api.google_login, name="auth_google"),
    path("api/auth/logout/", auth_api.logout_view, name="auth_logout"),

    # Boshqaruv paneli (faqat staff)
    path("panel/", pv.dashboard, name="panel"),
    path("panel/orders/", pv.orders, name="panel_orders"),
    path("panel/orders/<int:pk>/status/", pv.order_status, name="panel_order_status"),
    path("panel/users/", pv.users, name="panel_users"),
    path("panel/<slug:key>/", pv.crud_list, name="panel_list"),
    path("panel/<slug:key>/new/", pv.crud_form, name="panel_new"),
    path("panel/<slug:key>/<int:pk>/edit/", pv.crud_form, name="panel_edit"),
    path("panel/<slug:key>/<int:pk>/delete/", pv.crud_delete, name="panel_delete"),
    path("panel/<slug:key>/<int:pk>/toggle/", pv.crud_toggle, name="panel_toggle"),
]
