import django_filters
from django.db.models import QuerySet

from common.exceptions import UnprocessableEntity
from forum.models import Question


class OrderingCharFilter(django_filters.CharFilter):
    def filter(self, qs: QuerySet, value: str):
        if not value:
            return qs

        if value not in {"asc", "desc"}:
            raise UnprocessableEntity
        sign = "-" if value == "desc" else ""
        return qs.order_by(f"{sign}{self.field_name}")


class OrderingBooleanFilter(django_filters.BooleanFilter):
    def filter(self, qs: QuerySet, value: bool):
        if value is None:
            return qs

        return qs.order_by(f"-{self.field_name}") if value else qs


class QuestionFilter(django_filters.FilterSet):
    by_title = django_filters.CharFilter(field_name="title", lookup_expr="icontains")
    order_by_date = OrderingCharFilter(field_name="date_created")
    order_by_views = OrderingBooleanFilter(field_name="views")

    class Meta:
        model = Question
        fields = ["title", "date_created", "views"]
