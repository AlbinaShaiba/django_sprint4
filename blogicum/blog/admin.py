from django.contrib import admin

from .models import Category, Comment, Location, Post


admin.site.register(Category)

admin.site.register(Comment)


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('title',
                    'get_short_text',
                    'pub_date',
                    'author',
                    'location',
                    'category',
                    'is_published')

    list_editable = ('location',
                     'category',
                     'is_published')

    search_fields = ('title',
                     'category')

    list_filter = ('category',)

    empty_value_display = 'Не задано'

    def get_short_text(self, obj):
        return obj.text[:30]
    get_short_text.short_description = 'text'


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    search_fields = ('name',)
