from django.contrib import admin
from .models import Article, Comment, Category

admin.site.register([
    Article,
    Comment,
    Category
])