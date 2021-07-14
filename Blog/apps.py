from django.apps import AppConfig


class BlogConfig(AppConfig):
    name = 'Blog'

    def ready(self):
        import Blog.signals
