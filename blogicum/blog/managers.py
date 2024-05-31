from django.db import models
from django.utils import timezone


class PublishedPostsManager(models.Manager):
    """Returns all published posts"""
    def get_queryset(self):
        return super().get_queryset().filter(is_published=True,
                                            category__is_published=True,
                                            pub_date__lte=timezone.now()
                                            ).order_by('-pub_date')