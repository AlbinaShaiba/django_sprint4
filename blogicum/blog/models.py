from django.db import models
from django.contrib.auth import get_user_model
from django.conf import settings
from django.utils import timezone

from .managers import PublishedPostsManager


User = get_user_model()


class PublishedModel(models.Model):
    """Base class for published models"""

    is_published = models.BooleanField('Опубликовано',
                                       default=True,
                                       help_text=(
                                           'Снимите галочку, '
                                           'чтобы скрыть публикацию.'))
    created_at = models.DateTimeField('Добавлено', auto_now_add=True)

    class Meta:
        abstract = True
        ordering = ('-pub_date',)


class Category(PublishedModel):
    """Category model"""

    title = models.CharField('Заголовок',
                             max_length=settings.MAX_LENGTH)
    description = models.TextField('Описание')
    slug = models.SlugField('Идентификатор',
                            unique=True,
                            help_text=(
                                'Идентификатор страницы для URL; '
                                'разрешены символы латиницы, цифры, '
                                'дефис и подчёркивание.'))

    class Meta:
        verbose_name = 'категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        return self.title[:settings.TITLE_LEN]


class Location(PublishedModel):
    """Location model"""

    name = models.CharField('Название места',
                            max_length=settings.MAX_LENGTH)

    class Meta:
        verbose_name = 'местоположение'
        verbose_name_plural = 'Местоположения'

    def __str__(self):
        return self.name[:settings.TITLE_LEN]


class Post(PublishedModel):
    """Post model"""

    title = models.CharField('Заголовок',
                             max_length=settings.MAX_LENGTH)
    text = models.TextField('Текст')
    pub_date = models.DateTimeField('Дата и время публикации',
                                    help_text=(
                                        'Если установить дату и время '
                                        'в будущем — можно делать '
                                        'отложенные публикации.'))
    author = models.ForeignKey(User,
                               on_delete=models.CASCADE,
                               verbose_name='Автор публикации')
    location = models.ForeignKey(Location,
                                 on_delete=models.SET_NULL,
                                 verbose_name='Местоположение',
                                 null=True)

    category = models.ForeignKey(Category,
                                 on_delete=models.SET_NULL,
                                 null=True,
                                 verbose_name='Категория')

    image = models.ImageField('Изображение',
                              blank=True,
                              upload_to='blogicum_images')

    class Meta:
        verbose_name = 'публикация'
        verbose_name_plural = 'Публикации'


    objects = models.Manager()

    published_ordered_obj = PublishedPostsManager()


    def __str__(self):
        return self.title[:settings.TITLE_LEN]


class Comment(models.Model):
    """Comment model"""

    title = models.CharField('Заголовок комментария',
                             max_length=settings.MAX_LENGTH)
    text = models.TextField('Текст комментария')
    author = models.ForeignKey(User,
                               on_delete=models.CASCADE,
                               verbose_name='Автор комментария')

    created_at = models.DateTimeField('Добавлено',
                                      auto_now_add=True)

    post = models.ForeignKey(Post, related_name='comments',
                             on_delete=models.CASCADE,
                             null=True)

    class Meta:
        verbose_name = 'комментарий'
        verbose_name_plural = 'Комментарии'

    def __str__(self):
        return self.title[:settings.TITLE_LEN]
