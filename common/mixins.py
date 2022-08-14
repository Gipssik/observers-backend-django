from typing import TYPE_CHECKING, Any, Type

from django.db.models import Model
from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.serializers import Serializer
from rest_framework.viewsets import ModelViewSet

Base = ModelViewSet if TYPE_CHECKING else object


class GetSerializerClassMixin(Base):
    """Get serializer class from dict of serializers classes depending on action."""

    def get_serializer_class(self, *args: Any, **kwargs: Any) -> Type[Serializer]:
        """Returns serializer class looking at current action.

        If action was not found superclass method is used.

        :param args: Args.
        :param kwargs: Kwargs.
        :return: Serializer class.
        """
        kwargs["partial"] = True
        action = kwargs.get("action") or self.action
        try:
            return self.serializer_action_classes[action]
        except (KeyError, AttributeError):
            return super().get_serializer_class()


class CreationRetrieveSerializerMixin(Base):
    """Return created object using retrieve serializer.

    Must be used with GetSerializerClassMixin.
    """

    def perform_create(self, serializer: Serializer) -> Model:
        """Returns created object.

        :param serializer: Serializer object.
        :return: Model instance.
        """
        return serializer.save()

    def create(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        """Creates object and serializes it with retrieve serializer.

        :param request: Current request.
        :param args: Args.
        :param kwargs: Kwargs.
        :return: Response with object serialized with retrieve serializer.
        """
        serializer: Serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance = self.perform_create(serializer)

        serializer_class: Type[Serializer] = self.get_serializer_class(
            action="retrieve",
        )
        instance_serializer = serializer_class(instance)

        headers: dict[str, Any] = self.get_success_headers(instance_serializer.data)
        return Response(
            instance_serializer.data,
            status=status.HTTP_201_CREATED,
            headers=headers,
        )


class UpdateRetrieveSerializerMixin(Base):
    """Return updated object using retrieve serializer.

    Must be used with GetSerializerClassMixin.
    """

    def perform_update(self, serializer: Serializer) -> Model:
        """Returns updated object.

        :param serializer: Serializer object.
        :return: Updated Model instance.
        """
        return serializer.save()

    def update(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        """Updates object and serializes it with retrieve serializer.

        :param request: Current request.
        :param args: Args.
        :param kwargs: Kwargs.
        :return: Response with updated object serialized with retrieve serializer.
        """
        partial = kwargs.pop("partial", False)
        instance: Model = self.get_object()
        serializer: Serializer = self.get_serializer(
            instance,
            data=request.data,
            partial=partial,
        )
        serializer.is_valid(raise_exception=True)
        instance = self.perform_update(serializer)

        if getattr(instance, "_prefetched_objects_cache", None):
            instance._prefetched_objects_cache = {}

        serializer_class: Type[Serializer] = self.get_serializer_class(
            action="retrieve",
        )
        instance_serializer = serializer_class(instance)

        return Response(instance_serializer.data)


class MultipleSerializersMixinSet(
    GetSerializerClassMixin,
    CreationRetrieveSerializerMixin,
    UpdateRetrieveSerializerMixin,
):
    """Set of mixins to implement own serializer class for each action.

    You need to provide the `serializer_action_classes` dictionary.
    """
