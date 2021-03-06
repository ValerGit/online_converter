from django.conf.urls import include, url
from django.contrib import admin
from convert import views

urlpatterns = [
    url(r'^jet/', include('jet.urls', 'jet')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^profile/', views.profile, name='view-profile'),
    url(r'^converting/$', 'convert.views.proceed_convert', name='converting'),
    url(r'^$', views.home, name='view-home'),
    url(r'^signin/$', views.signin, name='view-sign-in'),
    url(r'^signup/$', views.signup, name='view-sign-up'),
    url(r'^account/$', views.account, name='view-account'),
    url(r'^send-metric/$', views.sendmetric, name='view-send-metric'),
    url(r'^ports/$', views.ports, name='view-choose-ports'),
    url(r'^tables-choose/$', views.tables, name='view-choose-tables'),
    url(r'^logout/$', 'django.contrib.auth.views.logout', {'next_page': '/'}, name='view-logout'),
    url(r'^connect/$', views.create_db),
    url(r'^get-tables/$', views.get_tables_by_db, name='get-tables'),
    url(r'^get-attrs/$', views.get_attrs_by_table, name='get-attrs'),
    url(r'^progress/$', views.progress, name='progress'),
    url(r'^get-pulse-data/$', views.get_pulse),
    url(r'^check-status/$', views.check_status, name='check-status'),
    url(r'^get-pulse-data/$', views.get_pulse),
    url(r'^remove/$', views.remove, name='view-remove'),
    url(r'^create-user/$', views.create_user, name='view-create-user'),
    url(r'^add-mongo-agent/$', views.add_mongo_agent, name='view-add-mongo-agent'),
    url(r'^view-graphs', views.graphs, name='view-graphs'),
    url(r'^graph', views.get_graph, name='view-get-graph'),
    url(r'^get-metric', views.get_metric, name='view-get-metric'),
]
