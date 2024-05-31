from django.core.paginator import Paginator
from django.db.models import Count


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
