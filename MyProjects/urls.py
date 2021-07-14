"""MyProjects URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""


from django.contrib import admin
from django.conf import settings
from django.urls import path, include
from django.conf.urls.static import static


admin.site.site_header = 'ItsPiyushSati'
admin.site.site_title = 'ItsPiyushSati Admin Panel'
admin.site.index_title = 'Welcome Piyush Sati to Admin Panel'


urlpatterns = [
    path('admin/', admin.site.urls),
    path('Blog/', include('Blog.urls')),
    path('', include('Blog.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)

handler404 = 'Blog.views.error_404'
handler500 = 'Blog.views.error_500'
handler400 = 'Blog.views.error_400'
