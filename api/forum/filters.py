import django_filters
from django.db.models import QuerySet

from common.exceptions import UnprocessableEntity
from forum.models import Question


class OrderingCharFilter(django_filters.CharFilter):
    """Uses 'asc' or 'desc' to order by a certain field."""

    def filter(self, qs: QuerySet[Question], value: str) -> QuerySet[Question]:
        """Applies order to queryset checking if value is 'asc' or 'desc'.

        :param qs: Queryset.
        :param value: Order value. 'asc' or 'desc'.
        :return: Queryset ordered by field in `value` order.
        :raises UnprocessableEntity: if value is 'asc' or 'desc'.
        """
        if not value:
            return qs

        if value not in {"asc", "desc"}:
            raise UnprocessableEntity
        sign = "-" if value == "desc" else ""
        return qs.order_by(f"{sign}{self.field_name}")


class OrderingBooleanFilter(django_filters.BooleanFilter):
    """Orders queryset by field in descending order."""

    def filter(self, qs: QuerySet[Question], value: bool) -> QuerySet[Question]:
        """Orders queryset in descending order if value is True.

        :param qs: Queryset.
        :param value: Boolean value. True, False or None.
        :return: Ordered queryset.
        """
        return qs.order_by(f"-{self.field_name}") if value else qs


class QuestionFilter(django_filters.FilterSet):
    """Question model filter."""

    by_title = django_filters.CharFilter(field_name="title", lookup_expr="icontains")
    order_by_date = OrderingCharFilter(field_name="date_created")
    order_by_views = OrderingBooleanFilter(field_name="views")

    class Meta:
        model = Question
        fields = ["title", "date_created", "order_by_views"]
