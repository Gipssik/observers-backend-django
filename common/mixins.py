from rest_framework import status
from rest_framework.response import Response


class GetSerializerClassMixin:
    """Get serializer class from dict of serializers classes depending on action."""

    def get_serializer_class(self, *args, **kwargs):
        kwargs["partial"] = True
        action = kwargs.get("action") or self.action
        try:
            return self.serializer_action_classes[action]
        except (KeyError, AttributeError):
            return super().get_serializer_class()


class ReturnCreatedObjectWithRetrieveSerializerMixin:
    """Return created object using retrieve serializer. Must be used with GetSerializerClassMixin."""

    def perform_create(self, serializer):
        return serializer.save()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance = self.perform_create(serializer)

        serializer_class = self.get_serializer_class(action="retrieve")
        instance_serializer = serializer_class(instance)

        headers = self.get_success_headers(instance_serializer.data)
        return Response(
            instance_serializer.data,
            status=status.HTTP_201_CREATED,
            headers=headers,
        )


class ReturnUpdatedObjectWithRetrieveSerializerMixin:
    """Return updated object using retrieve serializer. Must be used with GetSerializerClassMixin."""

    def perform_update(self, serializer):
        return serializer.save()

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        instance = self.perform_update(serializer)

        if getattr(instance, "_prefetched_objects_cache", None):
            instance._prefetched_objects_cache = {}

        serializer_class = self.get_serializer_class(action="retrieve")
        instance_serializer = serializer_class(instance)

        return Response(instance_serializer.data)


class MultipleSerializersMixinSet(
    GetSerializerClassMixin,
    ReturnCreatedObjectWithRetrieveSerializerMixin,
    ReturnUpdatedObjectWithRetrieveSerializerMixin,
):
    """Set of mixins to implement own serializer class for each action. You need to provide
    the `serializer_action_classes` dictionary."""
