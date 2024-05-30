from django.core.paginator import Paginator
from django.db.models import Count
from django.utils import timezone


def get_published_posts(queryset):
    """Returns all published posts"""
    return queryset.filter(
        is_published=True,
        category__is_published=True,
        pub_date__lte=timezone.now()
    )


def count_comments(queryset):
    """Returns the number of comments for a given post"""
    comment_count = Count('comments')
    return queryset.annotate(comment_count=comment_count)


def paginate_queryset(request, queryset, page_size):
    """Paginates the queryset"""
    paginator = Paginator(queryset, page_size)
    page_number = request.GET.get('page')
    queryset = paginator.get_page(page_number)
    return queryset
