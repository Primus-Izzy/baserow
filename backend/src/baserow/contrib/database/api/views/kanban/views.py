from drf_spectacular.openapi import OpenApiParameter, OpenApiTypes
from drf_spectacular.utils import extend_schema
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from baserow.api.decorators import (
    allowed_includes,
    map_exceptions,
    validate_body,
    validate_query_parameters,
)
from baserow.api.errors import ERROR_USER_NOT_IN_GROUP
from baserow.api.schemas import get_error_schema
from baserow.api.search.serializers import SearchQueryParamSerializer
from baserow.api.serializers import get_example_pagination_serializer_class
from baserow.contrib.database.api.constants import (
    ADHOC_FILTERS_API_PARAMS,
    ADHOC_FILTERS_API_PARAMS_NO_COMBINE,
    ADHOC_SORTING_API_PARAM,
    EXCLUDE_COUNT_API_PARAM,
    EXCLUDE_FIELDS_API_PARAM,
    INCLUDE_FIELDS_API_PARAM,
    LIMIT_LINKED_ITEMS_API_PARAM,
    ONLY_COUNT_API_PARAM,
    PAGINATION_API_PARAMS,
    SEARCH_MODE_API_PARAM,
    SEARCH_VALUE_API_PARAM,
)
from baserow.contrib.database.api.fields.errors import (
    ERROR_FIELD_DOES_NOT_EXIST,
    ERROR_FIELD_NOT_IN_TABLE,
    ERROR_FILTER_FIELD_NOT_FOUND,
    ERROR_ORDER_BY_FIELD_NOT_FOUND,
    ERROR_ORDER_BY_FIELD_NOT_POSSIBLE,
)
from baserow.contrib.database.api.rows.serializers import (
    RowSerializer,
    get_example_multiple_rows_metadata_serializer,
    get_example_row_serializer_class,
    get_row_serializer_class,
)
from baserow.contrib.database.api.utils import get_include_exclude_field_ids
from baserow.contrib.database.api.views.errors import (
    ERROR_NO_AUTHORIZATION_TO_PUBLICLY_SHARED_VIEW,
    ERROR_VIEW_FILTER_TYPE_DOES_NOT_EXIST,
    ERROR_VIEW_FILTER_TYPE_UNSUPPORTED_FIELD,
)
from baserow.contrib.database.api.views.kanban.serializers import (
    KanbanViewFieldOptionsSerializer,
    KanbanViewFilterSerializer,
    KanbanViewMoveCardSerializer,
)
from baserow.contrib.database.api.views.serializers import FieldOptionsField
from baserow.contrib.database.api.views.utils import (
    get_public_view_authorization_token,
    get_public_view_filtered_queryset,
    get_view_filtered_queryset,
    paginate_and_serialize_queryset,
    serialize_rows_metadata,
    serialize_view_field_options,
)
from baserow.contrib.database.fields.exceptions import (
    FieldDoesNotExist,
    FieldNotInTable,
    FilterFieldNotFound,
    OrderByFieldNotFound,
    OrderByFieldNotPossible,
)
from baserow.contrib.database.fields.handler import FieldHandler
from baserow.contrib.database.rows.handler import RowHandler
from baserow.contrib.database.table.operations import ListRowsDatabaseTableOperationType
from baserow.contrib.database.views.exceptions import (
    NoAuthorizationToPubliclySharedView,
    ViewDoesNotExist,
    ViewFilterTypeDoesNotExist,
    ViewFilterTypeNotAllowedForField,
)
from baserow.contrib.database.views.filters import AdHocFilters
from baserow.contrib.database.views.handler import ViewHandler
from baserow.contrib.database.views.models import KanbanView
from baserow.contrib.database.views.registries import view_type_registry
from baserow.contrib.database.views.signals import view_loaded
from baserow.core.exceptions import UserNotInWorkspace
from baserow.core.handler import CoreHandler

from .errors import ERROR_KANBAN_DOES_NOT_EXIST


class KanbanViewView(APIView):
    permission_classes = (IsAuthenticated,)

    def get_permissions(self):
        if self.request.method == "GET":
            return [AllowAny()]

        return super().get_permissions()

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="view_id",
                location=OpenApiParameter.PATH,
                type=OpenApiTypes.INT,
                description="Returns only rows that belong to the related view's table.",
            ),
            OpenApiParameter(
                name="include",
                location=OpenApiParameter.QUERY,
                type=OpenApiTypes.STR,
                description=(
                    "A comma separated list allowing the values of `field_options` and "
                    "`row_metadata` which will add the object/objects with the same "
                    "name to the response if included."
                ),
            ),
            ONLY_COUNT_API_PARAM,
            EXCLUDE_COUNT_API_PARAM,
            *PAGINATION_API_PARAMS,
            *ADHOC_FILTERS_API_PARAMS_NO_COMBINE,
            ADHOC_SORTING_API_PARAM,
            INCLUDE_FIELDS_API_PARAM,
            EXCLUDE_FIELDS_API_PARAM,
            SEARCH_VALUE_API_PARAM,
            SEARCH_MODE_API_PARAM,
            LIMIT_LINKED_ITEMS_API_PARAM,
        ],
        tags=["Database table kanban view"],
        operation_id="list_database_table_kanban_view_rows",
        description=(
            "Lists the requested rows of the view's table related to the provided "
            "`view_id` if the authorized user has access to the database's workspace."
        ),
        responses={
            200: get_example_pagination_serializer_class(
                get_example_row_serializer_class(
                    example_type="get", user_field_names=False
                ),
                additional_fields={
                    "field_options": FieldOptionsField(
                        serializer_class=KanbanViewFieldOptionsSerializer, required=False
                    ),
                    "row_metadata": get_example_multiple_rows_metadata_serializer(),
                },
                serializer_name="PaginationSerializerWithKanbanViewFieldOptions",
            ),
            400: get_error_schema(
                [
                    "ERROR_USER_NOT_IN_GROUP",
                    "ERROR_ORDER_BY_FIELD_NOT_FOUND",
                    "ERROR_ORDER_BY_FIELD_NOT_POSSIBLE",
                    "ERROR_FILTER_FIELD_NOT_FOUND",
                    "ERROR_VIEW_FILTER_TYPE_DOES_NOT_EXIST",
                    "ERROR_VIEW_FILTER_TYPE_UNSUPPORTED_FIELD",
                    "ERROR_FILTERS_PARAM_VALIDATION_ERROR",
                ]
            ),
            404: get_error_schema(
                ["ERROR_KANBAN_DOES_NOT_EXIST", "ERROR_FIELD_DOES_NOT_EXIST"]
            ),
        },
    )
    @map_exceptions(
        {
            UserNotInWorkspace: ERROR_USER_NOT_IN_GROUP,
            ViewDoesNotExist: ERROR_KANBAN_DOES_NOT_EXIST,
            OrderByFieldNotFound: ERROR_ORDER_BY_FIELD_NOT_FOUND,
            OrderByFieldNotPossible: ERROR_ORDER_BY_FIELD_NOT_POSSIBLE,
            FilterFieldNotFound: ERROR_FILTER_FIELD_NOT_FOUND,
            ViewFilterTypeDoesNotExist: ERROR_VIEW_FILTER_TYPE_DOES_NOT_EXIST,
            ViewFilterTypeNotAllowedForField: ERROR_VIEW_FILTER_TYPE_UNSUPPORTED_FIELD,
            FieldDoesNotExist: ERROR_FIELD_DOES_NOT_EXIST,
        }
    )
    @allowed_includes("field_options", "row_metadata")
    @validate_query_parameters(SearchQueryParamSerializer, return_validated=True)
    def get(self, request, view_id, field_options, row_metadata, query_params):
        """
        Lists all the rows of a kanban view, paginated either by a page or offset/limit.
        """

        include_fields = request.GET.get("include_fields")
        exclude_fields = request.GET.get("exclude_fields")
        adhoc_filters = AdHocFilters.from_request(request)
        order_by = request.GET.get("order_by")

        view_handler = ViewHandler()
        view = view_handler.get_view_as_user(
            request.user,
            view_id,
            KanbanView,
            base_queryset=KanbanView.objects.prefetch_related(
                "viewsort_set", "viewgroupby_set"
            ),
        )
        view_type = view_type_registry.get_by_model(view)

        workspace = view.table.database.workspace
        CoreHandler().check_permissions(
            request.user,
            ListRowsDatabaseTableOperationType.type,
            workspace=workspace,
            context=view.table,
        )
        field_ids = get_include_exclude_field_ids(
            view.table, include_fields, exclude_fields
        )

        queryset = get_view_filtered_queryset(
            view, adhoc_filters, order_by, query_params
        )
        model = queryset.model

        if ONLY_COUNT_API_PARAM.name in request.GET:
            return Response({"count": queryset.count()})

        response, page, _ = paginate_and_serialize_queryset(
            queryset, request, field_ids
        )

        if field_options:
            response.data.update(**serialize_view_field_options(view, model))

        if row_metadata:
            response.data.update(
                row_metadata=serialize_rows_metadata(request.user, view, page)
            )

        view_loaded.send(
            sender=self,
            table=view.table,
            view=view,
            table_model=model,
            user=request.user,
        )
        return response

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="view_id",
                location=OpenApiParameter.PATH,
                type=OpenApiTypes.INT,
                required=False,
                description="Returns only rows that belong to the related view's table.",
            )
        ],
        tags=["Database table kanban view"],
        operation_id="filter_database_table_kanban_view_rows",
        description=(
            "Lists only the rows and fields that match the request. Only the rows "
            "with the ids that are in the `row_ids` list are going to be returned."
        ),
        request=KanbanViewFilterSerializer,
        responses={
            200: get_example_row_serializer_class(
                example_type="get", user_field_names=False
            )(many=True),
            400: get_error_schema(
                ["ERROR_USER_NOT_IN_GROUP", "ERROR_REQUEST_BODY_VALIDATION"]
            ),
            404: get_error_schema(["ERROR_KANBAN_DOES_NOT_EXIST"]),
        },
    )
    @map_exceptions(
        {
            UserNotInWorkspace: ERROR_USER_NOT_IN_GROUP,
            ViewDoesNotExist: ERROR_KANBAN_DOES_NOT_EXIST,
        }
    )
    @validate_body(KanbanViewFilterSerializer)
    def post(self, request, view_id, data):
        """
        Row filter endpoint that only lists the requested rows and optionally only the
        requested fields.
        """

        view = ViewHandler().get_view_as_user(request.user, view_id, KanbanView)
        CoreHandler().check_permissions(
            request.user,
            ListRowsDatabaseTableOperationType.type,
            workspace=view.table.database.workspace,
            context=view.table,
        )

        model = view.table.get_model(field_ids=data["field_ids"])
        results = model.objects.filter(pk__in=data["row_ids"])

        serializer_class = get_row_serializer_class(
            model, RowSerializer, is_response=True
        )
        serializer = serializer_class(results, many=True)
        return Response(serializer.data)


class KanbanViewMoveCardView(APIView):
    permission_classes = (IsAuthenticated,)

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="view_id",
                location=OpenApiParameter.PATH,
                type=OpenApiTypes.INT,
                description="The ID of the kanban view.",
            )
        ],
        tags=["Database table kanban view"],
        operation_id="move_database_table_kanban_view_card",
        description=(
            "Moves a card (row) between columns in a kanban view by updating the "
            "underlying single select field value."
        ),
        request=KanbanViewMoveCardSerializer,
        responses={
            200: get_example_row_serializer_class(
                example_type="get", user_field_names=False
            ),
            400: get_error_schema(
                [
                    "ERROR_USER_NOT_IN_GROUP",
                    "ERROR_REQUEST_BODY_VALIDATION",
                    "ERROR_FIELD_NOT_IN_TABLE",
                ]
            ),
            404: get_error_schema(
                ["ERROR_KANBAN_DOES_NOT_EXIST", "ERROR_ROW_DOES_NOT_EXIST"]
            ),
        },
    )
    @map_exceptions(
        {
            UserNotInWorkspace: ERROR_USER_NOT_IN_GROUP,
            ViewDoesNotExist: ERROR_KANBAN_DOES_NOT_EXIST,
            FieldNotInTable: ERROR_FIELD_NOT_IN_TABLE,
        }
    )
    @validate_body(KanbanViewMoveCardSerializer)
    def patch(self, request, view_id, data):
        """
        Moves a card between columns by updating the single select field value.
        """

        view_handler = ViewHandler()
        view = view_handler.get_view_as_user(request.user, view_id, KanbanView)
        
        workspace = view.table.database.workspace
        CoreHandler().check_permissions(
            request.user,
            ListRowsDatabaseTableOperationType.type,
            workspace=workspace,
            context=view.table,
        )

        try:
            from baserow.contrib.database.views.kanban_handler import KanbanViewHandler
            kanban_handler = KanbanViewHandler()
            
            result = kanban_handler.move_card(
                user=request.user,
                kanban_view=view,
                row_id=data["row_id"],
                to_column_value=data.get("to_column_value"),
                before_row_id=data.get("before_row_id"),
            )
            
            # Return the updated row
            model = view.table.get_model()
            serializer_class = get_row_serializer_class(
                model, RowSerializer, is_response=True
            )
            serializer = serializer_class(result["row"])
            return Response(serializer.data)
            
        except ValueError as e:
            return Response(
                {"error": str(e)},
                status=400
            )


class KanbanViewColumnsView(APIView):
    permission_classes = (IsAuthenticated,)

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="view_id",
                location=OpenApiParameter.PATH,
                type=OpenApiTypes.INT,
                description="The ID of the kanban view.",
            )
        ],
        tags=["Database table kanban view"],
        operation_id="get_database_table_kanban_view_columns",
        description=(
            "Returns the available columns for a Kanban view based on the "
            "single select field options."
        ),
        responses={
            200: {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "integer", "nullable": True},
                        "value": {"type": "string", "nullable": True},
                        "color": {"type": "string"},
                        "name": {"type": "string"},
                        "order": {"type": "integer"},
                    }
                }
            },
            400: get_error_schema(["ERROR_USER_NOT_IN_GROUP"]),
            404: get_error_schema(["ERROR_KANBAN_DOES_NOT_EXIST"]),
        },
    )
    @map_exceptions(
        {
            UserNotInWorkspace: ERROR_USER_NOT_IN_GROUP,
            ViewDoesNotExist: ERROR_KANBAN_DOES_NOT_EXIST,
        }
    )
    def get(self, request, view_id):
        """
        Returns the available columns for a Kanban view.
        """

        view_handler = ViewHandler()
        view = view_handler.get_view_as_user(request.user, view_id, KanbanView)
        
        workspace = view.table.database.workspace
        CoreHandler().check_permissions(
            request.user,
            ListRowsDatabaseTableOperationType.type,
            workspace=workspace,
            context=view.table,
        )

        from baserow.contrib.database.views.kanban_handler import KanbanViewHandler
        kanban_handler = KanbanViewHandler()
        
        columns = kanban_handler.get_kanban_columns(view)
        return Response(columns)