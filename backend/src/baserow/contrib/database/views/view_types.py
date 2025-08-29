from collections import defaultdict
from typing import Any, Dict, List, Optional, Set, Tuple
from zipfile import ZipFile

from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.core.files.storage import Storage
from django.db.models import Count, Q
from django.urls import include, path

from rest_framework import serializers

from baserow.api.user_files.serializers import UserFileField
from baserow.contrib.database.api.fields.errors import (
    ERROR_FIELD_NOT_IN_TABLE,
    ERROR_INCOMPATIBLE_FIELD,
    ERROR_SELECT_OPTION_DOES_NOT_BELONG_TO_FIELD,
)
from baserow.contrib.database.api.views.form.errors import (
    ERROR_FORM_VIEW_FIELD_OPTIONS_CONDITION_GROUP_DOES_NOT_EXIST,
    ERROR_FORM_VIEW_FIELD_TYPE_IS_NOT_SUPPORTED,
    ERROR_FORM_VIEW_READ_ONLY_FIELD_IS_NOT_SUPPORTED,
)
from baserow.contrib.database.api.views.form.exceptions import (
    FormViewFieldOptionsConditionGroupDoesNotExist,
)
from baserow.contrib.database.api.views.form.serializers import (
    FormViewFieldOptionsSerializer,
    FormViewNotifyOnSubmitSerializerMixin,
)
from baserow.contrib.database.api.views.gallery.serializers import (
    GalleryViewFieldOptionsSerializer,
)
from baserow.contrib.database.api.views.grid.errors import (
    ERROR_AGGREGATION_DOES_NOT_SUPPORTED_FIELD,
)
from baserow.contrib.database.api.views.grid.serializers import (
    GridViewFieldOptionsSerializer,
)
from baserow.contrib.database.api.views.timeline.serializers import (
    TimelineViewFieldOptionsSerializer,
)
from baserow.contrib.database.fields.exceptions import (
    FieldNotInTable,
    IncompatibleField,
    SelectOptionDoesNotBelongToField,
)
from baserow.contrib.database.fields.models import Field, FileField, SelectOption
from baserow.contrib.database.fields.registries import field_type_registry
from baserow.contrib.database.table.models import Table
from baserow.contrib.database.views.registries import view_aggregation_type_registry
from baserow.core.handler import CoreHandler
from baserow.core.import_export.utils import file_chunk_generator
from baserow.core.storage import ExportZipFile
from baserow.core.user_files.handler import UserFileHandler
from baserow.core.user_files.models import UserFile

from .exceptions import (
    FormViewFieldTypeIsNotSupported,
    FormViewReadOnlyFieldIsNotSupported,
    GridViewAggregationDoesNotSupportField,
)
from .handler import ViewHandler
from .models import (
    CalendarView,
    CalendarViewFieldOptions,
    FormView,
    FormViewFieldOptions,
    FormViewFieldOptionsAllowedSelectOptions,
    FormViewFieldOptionsCondition,
    FormViewFieldOptionsConditionGroup,
    GalleryView,
    GalleryViewFieldOptions,
    GridView,
    GridViewFieldOptions,
    TimelineView,
    TimelineViewFieldOptions,
    TimelineDependency,
    TimelineMilestone,
    View,
)
from .registries import ViewType, form_view_mode_registry, view_filter_type_registry


class GridViewType(ViewType):
    type = "grid"
    model_class = GridView
    field_options_model_class = GridViewFieldOptions
    field_options_serializer_class = GridViewFieldOptionsSerializer
    can_aggregate_field = True
    can_share = True
    can_decorate = True
    has_public_info = True
    can_group_by = True
    when_shared_publicly_requires_realtime_events = True
    allowed_fields = [
        "row_identifier_type", 
        "row_height_size",
        "sticky_header",
        "conditional_formatting",
        "column_groups",
        "filter_presets",
    ]
    field_options_allowed_fields = [
        "width",
        "hidden",
        "order",
        "aggregation_type",
        "aggregation_raw_type",
        "inline_editing_config",
    ]
    serializer_field_names = [
        "row_identifier_type", 
        "row_height_size",
        "sticky_header",
        "conditional_formatting",
        "column_groups",
        "filter_presets",
    ]

    api_exceptions_map = {
        GridViewAggregationDoesNotSupportField: ERROR_AGGREGATION_DOES_NOT_SUPPORTED_FIELD,
    }

    def get_api_urls(self):
        from baserow.contrib.database.api.views.grid import urls as api_urls

        return [
            path("grid/", include(api_urls, namespace=self.type)),
        ]

    def export_serialized(
        self,
        grid: View,
        cache: Optional[Dict] = None,
        files_zip: Optional[ExportZipFile] = None,
        storage: Optional[Storage] = None,
    ):
        """
        Adds the serialized grid view options to the exported dict.
        """

        serialized = super().export_serialized(grid, cache, files_zip, storage)
        serialized["row_identifier_type"] = grid.row_identifier_type
        serialized["row_height_size"] = grid.row_height_size

        serialized_field_options = []
        for field_option in grid.get_field_options():
            serialized_field_options.append(
                {
                    "id": field_option.id,
                    "field_id": field_option.field_id,
                    "width": field_option.width,
                    "hidden": field_option.hidden,
                    "order": field_option.order,
                    "aggregation_type": field_option.aggregation_type,
                    "aggregation_raw_type": field_option.aggregation_raw_type,
                }
            )

        serialized["field_options"] = serialized_field_options
        return serialized

    def import_serialized(
        self,
        table: Table,
        serialized_values: Dict[str, Any],
        id_mapping: Dict[str, Any],
        files_zip: Optional[ZipFile] = None,
        storage: Optional[Storage] = None,
    ) -> Optional[View]:
        """
        Imports the serialized grid view field options.
        """

        serialized_copy = serialized_values.copy()
        field_options = serialized_copy.pop("field_options")
        grid_view = super().import_serialized(
            table, serialized_copy, id_mapping, files_zip, storage
        )
        if grid_view is not None:
            if "database_grid_view_field_options" not in id_mapping:
                id_mapping["database_grid_view_field_options"] = {}

            for field_option in field_options:
                field_option_copy = field_option.copy()
                field_option_id = field_option_copy.pop("id")
                field_option_copy["field_id"] = id_mapping["database_fields"][
                    field_option["field_id"]
                ]
                field_option_object = GridViewFieldOptions.objects.create(
                    grid_view=grid_view, **field_option_copy
                )
                id_mapping["database_grid_view_field_options"][
                    field_option_id
                ] = field_option_object.id

        return grid_view

    def get_visible_fields_and_model(self, view):
        """
        Returns the model and the field options in the correct order for exporting
        this view type.
        """

        grid_view = ViewHandler().get_view(view.id, view_model=GridView)
        ordered_visible_field_ids = self.get_visible_field_options_in_order(
            grid_view
        ).values_list("field__id", flat=True)
        model = grid_view.table.get_model(field_ids=ordered_visible_field_ids)
        ordered_field_objects = [
            model._field_objects[field_id] for field_id in ordered_visible_field_ids
        ]
        return ordered_field_objects, model

    def before_field_options_update(self, view, field_options, fields):
        """
        Checks if a aggregation raw types are compatible with the field types.
        """

        fields_dict = {field.id: field for field in fields}

        for field_id, options in field_options.items():
            field = fields_dict.get(int(field_id), None)
            aggregation_raw_type = options.get("aggregation_raw_type")

            if aggregation_raw_type and field:
                try:
                    # Invalidate cache if new aggregation raw type has changed
                    prev_options = GridViewFieldOptions.objects.only(
                        "aggregation_raw_type"
                    ).get(field=field, grid_view=view)
                    if prev_options.aggregation_raw_type != aggregation_raw_type:
                        ViewHandler().clear_aggregation_cache(view, field.db_column)
                except GridViewFieldOptions.DoesNotExist:
                    pass

                # Checks if the aggregation raw type is compatible with the field type
                aggregation_type = view_aggregation_type_registry.get(
                    aggregation_raw_type
                )
                if not aggregation_type.field_is_compatible(field):
                    raise GridViewAggregationDoesNotSupportField(aggregation_type)

        return field_options

    def after_fields_type_change(self, fields):
        """
        Check field option aggregation_raw_type compatibility with the new field type.
        """

        field_options = (
            GridViewFieldOptions.objects_and_trash.filter(field__in=fields)
            .exclude(aggregation_raw_type="")
            .select_related("grid_view", "field")
        )

        view_handler = ViewHandler()

        for field_option in field_options:
            aggregation_type = view_aggregation_type_registry.get(
                field_option.aggregation_raw_type
            )

            view_handler.clear_aggregation_cache(
                field_option.grid_view, field_option.field.db_column
            )

            if not aggregation_type.field_is_compatible(field_option.field):
                # The field has an aggregation and the type is not compatible with
                # the new field, so we need to clean the aggregation.
                # @TODO check if there are multiple fields from the same field and
                #  update them in bulk.
                view_handler.update_field_options(
                    view=field_option.grid_view,
                    field_options={
                        field_option.field_id: {
                            "aggregation_type": "",
                            "aggregation_raw_type": "",
                        }
                    },
                )

    def get_visible_field_options_in_order(self, grid_view):
        return (
            grid_view.get_field_options(create_if_missing=True)
            .filter(hidden=False)
            .order_by("-field__primary", "order", "field__id")
        )

    def get_aggregations(self, grid_view):
        """
        Returns the (Field, aggregation_type) list computed from the field options for
        the specified view.
        """

        field_options = (
            GridViewFieldOptions.objects.filter(grid_view=grid_view)
            .exclude(aggregation_raw_type="")
            .select_related("field")
        )
        return [(option.field, option.aggregation_raw_type) for option in field_options]

    def after_field_value_update(self, updated_fields):
        """
        When a field value change, we need to invalidate the aggregation cache for this
        field.
        """

        to_clear = defaultdict(list)
        view_map = {}

        field_options = (
            GridViewFieldOptions.objects.filter(field__in=updated_fields)
            .exclude(aggregation_raw_type="")
            .select_related("grid_view", "field")
        )

        for options in field_options:
            to_clear[options.grid_view.id].append(options.field.db_column)
            view_map[options.grid_view.id] = options.grid_view

        view_handler = ViewHandler()
        for view_id, names in to_clear.items():
            view_handler.clear_aggregation_cache(view_map[view_id], names + ["total"])

    def after_field_update(self, updated_fields):
        """
        When a field configuration is changed, we need to invalid the cache for
        corresponding aggregations also.
        """

        self.after_field_value_update(updated_fields)

    def after_filter_update(self, grid_view):
        """
        If the view filters change we also need to invalid the aggregation cache for all
        fields of this view.
        """

        ViewHandler().clear_full_aggregation_cache(grid_view)

    def get_hidden_fields(
        self,
        view: GridView,
        field_ids_to_check: Optional[List[int]] = None,
    ) -> Set[int]:
        if field_ids_to_check is None:
            field_ids_to_check = view.table.field_set.values_list("id", flat=True)

        fields_with_options = view.gridviewfieldoptions_set.all()
        field_ids_with_options = {o.field_id for o in fields_with_options}
        hidden_field_ids = {o.field_id for o in fields_with_options if o.hidden}
        # Hide fields in shared views by default if they don't have field_options.
        if view.public:
            additional_hidden_field_ids = {
                f_id
                for f_id in field_ids_to_check
                if f_id not in field_ids_with_options
            }
            hidden_field_ids |= additional_hidden_field_ids

        return hidden_field_ids

    def enhance_queryset(self, queryset):
        return queryset.prefetch_related("gridviewfieldoptions_set")


class GalleryViewType(ViewType):
    type = "gallery"
    model_class = GalleryView
    field_options_model_class = GalleryViewFieldOptions
    field_options_serializer_class = GalleryViewFieldOptionsSerializer
    allowed_fields = ["card_cover_image_field"]
    field_options_allowed_fields = ["hidden", "order"]
    serializer_field_names = ["card_cover_image_field"]
    serializer_field_overrides = {
        "card_cover_image_field": serializers.PrimaryKeyRelatedField(
            queryset=Field.objects.all(),
            required=False,
            default=None,
            allow_null=True,
            help_text="References a file field of which the first image must be shown "
            "as card cover image.",
        )
    }
    api_exceptions_map = {
        FieldNotInTable: ERROR_FIELD_NOT_IN_TABLE,
        IncompatibleField: ERROR_INCOMPATIBLE_FIELD,
    }
    can_decorate = True
    can_share = True
    has_public_info = True

    def get_api_urls(self):
        from baserow.contrib.database.api.views.gallery import urls as api_urls

        return [
            path("gallery/", include(api_urls, namespace=self.type)),
        ]

    def prepare_values(self, values, table, user):
        """
        Check if the provided card cover image field belongs to the same table.
        """

        name = "card_cover_image_field"

        if values.get(name, None) is not None:
            if isinstance(values[name], int):
                values[name] = Field.objects.get(pk=values[name])

            field_type = field_type_registry.get_by_model(values[name].specific)
            if not field_type.can_represent_files(values[name]):
                raise IncompatibleField(
                    "The provided field cannot be used as a card cover image field."
                )
            elif values[name].table_id != table.id:
                raise FieldNotInTable(
                    "The provided file select field id does not belong to the gallery "
                    "view's table."
                )

        return super().prepare_values(values, table, user)

    def after_fields_type_change(self, fields):
        fields_cannot_represent_files = [
            field
            for field in fields
            if not field_type_registry.get_by_model(
                field.specific_class
            ).can_represent_files(field)
        ]
        if len(fields_cannot_represent_files) > 0:
            GalleryView.objects.filter(
                card_cover_image_field_id__in=[
                    f.id for f in fields_cannot_represent_files
                ]
            ).update(card_cover_image_field_id=None)

    def export_serialized(
        self,
        gallery: View,
        cache: Optional[Dict] = None,
        files_zip: Optional[ExportZipFile] = None,
        storage: Optional[Storage] = None,
    ):
        """
        Adds the serialized gallery view options to the exported dict.
        """

        serialized = super().export_serialized(gallery, cache, files_zip, storage)

        if gallery.card_cover_image_field_id:
            serialized["card_cover_image_field_id"] = gallery.card_cover_image_field_id

        serialized_field_options = []
        for field_option in gallery.get_field_options():
            serialized_field_options.append(
                {
                    "id": field_option.id,
                    "field_id": field_option.field_id,
                    "hidden": field_option.hidden,
                    "order": field_option.order,
                }
            )

        serialized["field_options"] = serialized_field_options
        return serialized

    def import_serialized(
        self,
        table: Table,
        serialized_values: Dict[str, Any],
        id_mapping: Dict[str, Any],
        files_zip: Optional[ZipFile] = None,
        storage: Optional[Storage] = None,
    ) -> Optional[View]:
        """
        Imports the serialized gallery view field options.
        """

        serialized_copy = serialized_values.copy()

        if serialized_copy.get("card_cover_image_field_id", None):
            serialized_copy["card_cover_image_field_id"] = id_mapping[
                "database_fields"
            ][serialized_copy["card_cover_image_field_id"]]

        field_options = serialized_copy.pop("field_options")

        gallery_view = super().import_serialized(
            table, serialized_copy, id_mapping, files_zip, storage
        )

        if gallery_view is not None:
            if "database_gallery_view_field_options" not in id_mapping:
                id_mapping["database_gallery_view_field_options"] = {}

            for field_option in field_options:
                field_option_copy = field_option.copy()
                field_option_id = field_option_copy.pop("id")
                field_option_copy["field_id"] = id_mapping["database_fields"][
                    field_option["field_id"]
                ]
                field_option_object = GalleryViewFieldOptions.objects.create(
                    gallery_view=gallery_view, **field_option_copy
                )
                id_mapping["database_gallery_view_field_options"][
                    field_option_id
                ] = field_option_object.id

        return gallery_view

    def view_created(self, view):
        """
        When a gallery view is created, we want to set the first three fields as
        visible.
        """

        field_options = view.get_field_options(create_if_missing=True).order_by(
            "-field__primary", "field__id"
        )
        ids_to_update = [f.id for f in field_options[0:3]]

        if ids_to_update:
            GalleryViewFieldOptions.objects.filter(id__in=ids_to_update).update(
                hidden=False
            )

    def export_prepared_values(self, view: GalleryView) -> Dict[str, Any]:
        """
        Add `card_cover_image_field` to the exportable fields.

        :param view: The gallery view to export.
        :return: The prepared values.
        """

        values = super().export_prepared_values(view)
        values["card_cover_image_field"] = view.card_cover_image_field_id

        return values

    def get_visible_field_options_in_order(self, gallery_view: GalleryView):
        return (
            gallery_view.get_field_options(create_if_missing=True)
            .filter(
                Q(hidden=False) | Q(field__id=gallery_view.card_cover_image_field_id)
            )
            .order_by("order", "field__id")
        )

    def get_hidden_fields(
        self,
        view: GalleryView,
        field_ids_to_check: Optional[List[int]] = None,
    ) -> Set[int]:
        hidden_field_ids = set()
        fields = view.table.field_set.all()
        field_options = view.galleryviewfieldoptions_set.all()

        if field_ids_to_check is not None:
            fields = [f for f in fields if f.id in field_ids_to_check]

        for field in fields:
            # The card cover image field is always visible.
            if field.id == view.card_cover_image_field_id:
                continue

            # Find corresponding field option
            field_option_matching = None
            for field_option in field_options:
                if field_option.field_id == field.id:
                    field_option_matching = field_option

            # A field is considered hidden, if it is explicitly hidden
            # or if the field options don't exist
            if field_option_matching is None or field_option_matching.hidden:
                hidden_field_ids.add(field.id)

        return hidden_field_ids

    def enhance_queryset(self, queryset):
        return queryset.prefetch_related("galleryviewfieldoptions_set")

    def after_field_delete(self, field: Field) -> None:
        if isinstance(field, FileField):
            GalleryView.objects.filter(card_cover_image_field_id=field.id).update(
                card_cover_image_field_id=None
            )


class TimelineViewType(ViewType):
    type = "timeline"
    model_class = TimelineView
    field_options_model_class = TimelineViewFieldOptions
    field_options_serializer_class = TimelineViewFieldOptionsSerializer
    allowed_fields = [
        "start_date_field", 
        "end_date_field", 
        "timescale",
        "enable_dependencies",
        "auto_reschedule",
        "enable_milestones"
    ]
    field_options_allowed_fields = [
        "hidden", 
        "order", 
        "show_in_timeline", 
        "color_field"
    ]
    serializer_field_names = [
        "start_date_field", 
        "end_date_field", 
        "timescale",
        "enable_dependencies",
        "auto_reschedule", 
        "enable_milestones"
    ]
    serializer_field_overrides = {
        "start_date_field": serializers.PrimaryKeyRelatedField(
            queryset=Field.objects.all(),
            required=False,
            default=None,
            allow_null=True,
            help_text="Date field used as start date for timeline items"
        ),
        "end_date_field": serializers.PrimaryKeyRelatedField(
            queryset=Field.objects.all(),
            required=False,
            default=None,
            allow_null=True,
            help_text="Date field used as end date for timeline items"
        ),
    }
    api_exceptions_map = {
        FieldNotInTable: ERROR_FIELD_NOT_IN_TABLE,
        IncompatibleField: ERROR_INCOMPATIBLE_FIELD,
    }
    can_decorate = True
    can_share = True
    has_public_info = True

    def get_api_urls(self):
        from baserow.contrib.database.api.views.timeline import urls as api_urls

        return [
            path("timeline/", include(api_urls, namespace=self.type)),
        ]

    def prepare_values(self, values, table, user):
        """
        Check if the provided date fields belong to the same table and are compatible.
        """
        start_date_field_value = values.get("start_date_field", None)
        if start_date_field_value is not None:
            if isinstance(start_date_field_value, int):
                start_date_field_value = Field.objects.get(pk=start_date_field_value)
                values["start_date_field"] = start_date_field_value

            start_date_field_value = start_date_field_value.specific
            field_type = field_type_registry.get_by_model(start_date_field_value)
            if not field_type.can_represent_date(start_date_field_value):
                raise IncompatibleField(
                    "The provided field is not a date field and cannot be used as a start date field."
                )

            if start_date_field_value.table_id != table.id:
                raise FieldNotInTable(
                    "The provided start date field does not belong to the timeline view's table."
                )

        end_date_field_value = values.get("end_date_field", None)
        if end_date_field_value is not None:
            if isinstance(end_date_field_value, int):
                end_date_field_value = Field.objects.get(pk=end_date_field_value)
                values["end_date_field"] = end_date_field_value

            end_date_field_value = end_date_field_value.specific
            field_type = field_type_registry.get_by_model(end_date_field_value)
            if not field_type.can_represent_date(end_date_field_value):
                raise IncompatibleField(
                    "The provided field is not a date field and cannot be used as an end date field."
                )

            if end_date_field_value.table_id != table.id:
                raise FieldNotInTable(
                    "The provided end date field does not belong to the timeline view's table."
                )

        return super().prepare_values(values, table, user)

    def export_serialized(
        self,
        timeline: View,
        cache: Optional[Dict] = None,
        files_zip: Optional[ExportZipFile] = None,
        storage: Optional[Storage] = None,
    ):
        """
        Adds the serialized timeline view options to the exported dict.
        """
        serialized = super().export_serialized(timeline, cache, files_zip, storage)
        
        if timeline.start_date_field_id:
            serialized["start_date_field_id"] = timeline.start_date_field_id
        if timeline.end_date_field_id:
            serialized["end_date_field_id"] = timeline.end_date_field_id
            
        serialized["timescale"] = timeline.timescale
        serialized["enable_dependencies"] = timeline.enable_dependencies
        serialized["auto_reschedule"] = timeline.auto_reschedule
        serialized["enable_milestones"] = timeline.enable_milestones

        serialized_field_options = []
        for field_option in timeline.get_field_options():
            serialized_field_options.append(
                {
                    "id": field_option.id,
                    "field_id": field_option.field_id,
                    "hidden": field_option.hidden,
                    "order": field_option.order,
                    "show_in_timeline": field_option.show_in_timeline,
                    "color_field": field_option.color_field,
                }
            )

        serialized["field_options"] = serialized_field_options
        return serialized

    def import_serialized(
        self,
        table: Table,
        serialized_values: Dict[str, Any],
        id_mapping: Dict[str, Any],
        files_zip: Optional[ZipFile] = None,
        storage: Optional[Storage] = None,
    ) -> Optional[View]:
        """
        Imports the serialized timeline view field options.
        """
        serialized_copy = serialized_values.copy()
        
        if "start_date_field_id" in serialized_copy:
            serialized_copy["start_date_field_id"] = id_mapping["database_fields"][
                serialized_copy.pop("start_date_field_id")
            ]
        if "end_date_field_id" in serialized_copy:
            serialized_copy["end_date_field_id"] = id_mapping["database_fields"][
                serialized_copy.pop("end_date_field_id")
            ]

        field_options = serialized_copy.pop("field_options")
        timeline_view = super().import_serialized(
            table, serialized_copy, id_mapping, files_zip, storage
        )

        if timeline_view is not None:
            if "database_timeline_view_field_options" not in id_mapping:
                id_mapping["database_timeline_view_field_options"] = {}

            for field_option in field_options:
                field_option_copy = field_option.copy()
                field_option_id = field_option_copy.pop("id")
                field_option_copy["field_id"] = id_mapping["database_fields"][
                    field_option["field_id"]
                ]
                field_option_object = TimelineViewFieldOptions.objects.create(
                    timeline_view=timeline_view, **field_option_copy
                )
                id_mapping["database_timeline_view_field_options"][
                    field_option_id
                ] = field_option_object.id

        return timeline_view

    def view_created(self, view: View):
        """
        When a timeline view is created, we want to set the first field as visible.
        """
        field_options = view.get_field_options(create_if_missing=True).order_by(
            "-field__primary", "field__id"
        )
        ids_to_update = [f.id for f in field_options[:1]]

        if len(ids_to_update) > 0:
            TimelineViewFieldOptions.objects.filter(id__in=ids_to_update).update(
                hidden=False
            )

    def export_prepared_values(self, view: TimelineView) -> Dict[str, Any]:
        values = super().export_prepared_values(view)
        values["start_date_field"] = view.start_date_field_id
        values["end_date_field"] = view.end_date_field_id
        values["timescale"] = view.timescale
        values["enable_dependencies"] = view.enable_dependencies
        values["auto_reschedule"] = view.auto_reschedule
        values["enable_milestones"] = view.enable_milestones
        return values

    def get_visible_field_options_in_order(self, timeline_view: TimelineView):
        return (
            timeline_view.get_field_options(create_if_missing=True)
            .filter(
                Q(hidden=False)
                # Always expose start and end date fields as they're required
                | Q(field_id=timeline_view.start_date_field_id)
                | Q(field_id=timeline_view.end_date_field_id)
            )
            .order_by("order", "field__id")
        )

    def get_hidden_fields(
        self,
        view: TimelineView,
        field_ids_to_check: Optional[List[int]] = None,
    ) -> Set[int]:
        hidden_field_ids = set()
        fields = view.table.field_set.all()
        field_options = view.timelineviewfieldoptions_set.all()

        if field_ids_to_check is not None:
            fields = [f for f in fields if f.id in field_ids_to_check]

        for field in fields:
            # Always expose start and end date fields as they're required
            if field.id in [view.start_date_field_id, view.end_date_field_id]:
                continue

            field_option_matching = None
            for field_option in field_options:
                if field_option.field_id == field.id:
                    field_option_matching = field_option

            # A field is considered hidden if it is explicitly hidden
            # or if the field options don't exist
            if field_option_matching is None or field_option_matching.hidden:
                hidden_field_ids.add(field.id)

        return hidden_field_ids

    def enhance_queryset(self, queryset):
        return queryset.prefetch_related(
            "timelineviewfieldoptions_set",
            "dependencies",
            "milestones"
        )

    def after_field_delete(self, field: Field) -> None:
        # Clean up timeline views that reference the deleted field
        TimelineView.objects.filter(start_date_field_id=field.id).update(
            start_date_field_id=None
        )
        TimelineView.objects.filter(end_date_field_id=field.id).update(
            end_date_field_id=None
        )
        # Clean up milestones that reference the deleted field
        TimelineMilestone.objects.filter(date_field_id=field.id).delete()


class FormViewType(ViewType):
    type = "form"
    model_class = FormView
    can_filter = False
    can_sort = False
    can_share = True
    can_list_rows = False
    restrict_link_row_public_view_sharing = False
    when_shared_publicly_requires_realtime_events = False
    field_options_model_class = FormViewFieldOptions
    field_options_serializer_class = FormViewFieldOptionsSerializer
    allowed_fields = [
        "title",
        "description",
        "mode",
        "cover_image",
        "logo_image",
        "submit_text",
        "submit_action",
        "submit_action_message",
        "submit_action_redirect_url",
        "users_to_notify_on_submit",
    ]
    field_options_allowed_fields = [
        "name",
        "description",
        "enabled",
        "required",
        "show_when_matching_conditions",
        "condition_type",
        "order",
        "field_component",
        "include_all_select_options",
    ]
    serializer_mixins = [FormViewNotifyOnSubmitSerializerMixin]
    serializer_field_names = [
        "title",
        "description",
        "mode",
        "cover_image",
        "logo_image",
        "submit_text",
        "submit_action",
        "submit_action_message",
        "submit_action_redirect_url",
        "receive_notification_on_submit",  # from FormViewNotifyOnSubmitSerializerMixin
    ]
    serializer_field_overrides = {
        "cover_image": UserFileField(
            required=False,
            help_text="The cover image that must be displayed at the top of the form.",
        ),
        "logo_image": UserFileField(
            required=False,
            help_text="The logo image that must be displayed at the top of the form.",
        ),
    }
    api_exceptions_map = {
        FormViewFieldTypeIsNotSupported: ERROR_FORM_VIEW_FIELD_TYPE_IS_NOT_SUPPORTED,
        FormViewReadOnlyFieldIsNotSupported: ERROR_FORM_VIEW_READ_ONLY_FIELD_IS_NOT_SUPPORTED,
        FormViewFieldOptionsConditionGroupDoesNotExist: ERROR_FORM_VIEW_FIELD_OPTIONS_CONDITION_GROUP_DOES_NOT_EXIST,
        SelectOptionDoesNotBelongToField: ERROR_SELECT_OPTION_DOES_NOT_BELONG_TO_FIELD,
    }

    def get_api_urls(self):
        from baserow.contrib.database.api.views.form import urls as api_urls

        return [
            path("form/", include(api_urls, namespace=self.type)),
        ]

    def after_fields_type_change(self, fields):
        fields_cannot_be_in_form_view = [
            field
            for field in fields
            if not field_type_registry.get_by_model(
                field.specific_class
            ).can_be_in_form_view
        ]
        if len(fields_cannot_be_in_form_view) > 0:
            # If the new field type is not compatible with the form view, we must
            # disable all the form view field options because they're not compatible
            # anymore.
            FormViewFieldOptions.objects_and_trash.filter(
                field__in=[f.id for f in fields_cannot_be_in_form_view], enabled=True
            ).update(enabled=False)

    def before_field_options_update(self, view, field_options, fields):
        """
        Checks if a field type that is incompatible with the form view is being
        enabled.
        """

        fields_dict = {field.id: field for field in fields}
        for field_id, options in field_options.items():
            field = fields_dict.get(int(field_id), None)
            if options.get("enabled") and field:
                field_type = field_type_registry.get_by_model(field.specific_class)
                if field.read_only:
                    raise FormViewReadOnlyFieldIsNotSupported(field.name)
                if not field_type.can_be_in_form_view:
                    raise FormViewFieldTypeIsNotSupported(field_type.type)

        return field_options

    def _prepare_new_condition_group(
        self, updated_field_option_instance, group, existing_condition_group_ids
    ):
        parent_group_id = group.get("parent_group", None)
        if (
            parent_group_id is not None
            and parent_group_id not in existing_condition_group_ids
        ):
            raise FormViewFieldOptionsConditionGroupDoesNotExist(
                "Invalid parent filter group id."
            )
        return FormViewFieldOptionsConditionGroup(
            field_option=updated_field_option_instance,
            filter_type=group["filter_type"],
            parent_group_id=group.get("parent_group", None),
        )

    def _group_exists_and_matches_field(self, existing_group, numeric_field_id):
        return (
            existing_group is not None
            and existing_group.field_option.field_id == numeric_field_id
        )

    def _prepare_condition_groups(
        self,
        field_options: Dict[str, Any],
        updated_field_options_by_field_id: Dict[int, FormViewFieldOptions],
        existing_condition_groups: Dict[int, FormViewFieldOptionsConditionGroup],
    ) -> Tuple[
        List[int],
        List[FormViewFieldOptionsConditionGroup],
        List[FormViewFieldOptionsConditionGroup],
        List[int],
    ]:
        """
        Figures out which condition groups need to be created, updated or deleted in
        order to match the provided field options.
        """

        groups_to_create_temp_ids = []
        groups_to_create = []
        groups_to_update = []
        existing_condition_group_ids = set(existing_condition_groups.keys())
        group_ids_to_delete = existing_condition_group_ids.copy()

        for field_id, options in field_options.items():
            if "condition_groups" not in options:
                continue

            numeric_field_id = int(field_id)
            updated_field_option_instance = updated_field_options_by_field_id[
                numeric_field_id
            ]

            for group in options["condition_groups"]:
                existing_group = existing_condition_groups.get(group["id"], None)

                parent_group_id = group.get("parent_group", None)
                if (
                    parent_group_id is not None
                    and parent_group_id in group_ids_to_delete
                ):
                    group_ids_to_delete.remove(parent_group_id)

                if self._group_exists_and_matches_field(
                    existing_group, numeric_field_id
                ):
                    existing_group.filter_type = group["filter_type"]
                    groups_to_update.append(existing_group)
                    group_ids_to_delete.remove(existing_group.id)

                else:
                    new_condition_group = self._prepare_new_condition_group(
                        updated_field_option_instance,
                        group,
                        existing_condition_group_ids,
                    )
                    groups_to_create_temp_ids.append(group["id"])
                    groups_to_create.append(new_condition_group)

        return (
            groups_to_create_temp_ids,
            groups_to_create,
            groups_to_update,
            group_ids_to_delete,
        )

    def _update_field_options_condition_groups(
        self,
        field_options: Dict[str, Any],
        updated_field_options_by_field_id: Dict[int, FormViewFieldOptions],
        existing_condition_groups: Dict[int, FormViewFieldOptionsConditionGroup],
    ) -> Dict[int, FormViewFieldOptionsConditionGroup]:
        """
        Updates the condition groups for the specified field options. Based on
        the new provided field options and the existing groups, this function
        figures out which groups need to be created, updated or deleted in order
        to match the options provided.

        :param field_options: The field options that are being updated.
        :param updated_field_options_by_field_id: A map containing the updated field
            options by field id.
        :param existing_condition_groups: A map containing the existing condition
            groups by id.
        :return: A map between the condition groups and their temporary id.
        """

        (
            groups_to_create_temp_ids,
            groups_to_create,
            groups_to_update,
            group_ids_to_delete,
        ) = self._prepare_condition_groups(
            field_options, updated_field_options_by_field_id, existing_condition_groups
        )

        groups_created = []
        if len(groups_to_create) > 0:
            groups_created = FormViewFieldOptionsConditionGroup.objects.bulk_create(
                groups_to_create
            )

        if len(groups_to_update) > 0:
            FormViewFieldOptionsConditionGroup.objects.bulk_update(
                groups_to_update, ["filter_type"]
            )

        if len(group_ids_to_delete) > 0:
            FormViewFieldOptionsConditionGroup.objects.filter(
                id__in=group_ids_to_delete
            ).delete()

        # The map contains the temporary ids for the newly created groups, so
        # that we can later map filters to the correct group.
        condition_group_ids_map = {
            **{
                groups_to_create_temp_ids[i]: groups_created[i]
                for i in range(len(groups_created))
            },
            **{group.id: group for group in groups_to_update},
        }

        return condition_group_ids_map

    def _prepare_condition_update(self, existing_condition, condition, group_id):
        existing_condition.field_id = condition["field"]
        existing_condition.type = condition["type"]
        existing_condition.value = condition["value"]
        existing_condition.group_id = group_id

    def _prepare_new_condition(
        self, updated_field_option_instance, condition, group_id
    ) -> FormViewFieldOptionsCondition:
        return FormViewFieldOptionsCondition(
            field_option=updated_field_option_instance,
            field_id=condition["field"],
            type=condition["type"],
            value=condition["value"],
            group_id=group_id,
        )

    def _get_group_id(self, condition, condition_group_id_map):
        group_id = condition.get("group", None)
        if group_id is None:
            return None
        elif group_id in condition_group_id_map:
            return condition_group_id_map[group_id].id
        else:
            raise FormViewFieldOptionsConditionGroupDoesNotExist(
                "Invalid filter group id."
            )

    def _condition_exists_and_matches_field(self, existing_condition, numeric_field_id):
        return (
            existing_condition is not None
            and existing_condition.field_option.field_id == numeric_field_id
        )

    def _prepare_conditions(
        self,
        field_options: Dict[str, Any],
        updated_field_options_by_field_id,
        existing_conditions: Dict[int, FormViewFieldOptionsCondition],
        condition_group_id_map,
        table_id: int,
        table_field_ids: Set[int],
    ) -> Tuple[
        List[FormViewFieldOptionsCondition],
        List[FormViewFieldOptionsCondition],
        List[int],
    ]:
        """
        Figures out which conditions need to be created, updated or deleted in
        order to match the options provided.
        """

        conditions_to_create = []
        conditions_to_update = []
        condition_ids_to_delete = set(existing_conditions.keys())

        for field_id, options in field_options.items():
            if "conditions" not in options:
                continue

            numeric_field_id = int(field_id)
            updated_field_option_instance = updated_field_options_by_field_id[
                numeric_field_id
            ]

            for condition in options["conditions"]:
                if condition["field"] not in table_field_ids:
                    raise FieldNotInTable(
                        f"The field {condition['field']} does not belong to table {table_id}."
                    )

                existing_condition = existing_conditions.get(condition["id"], None)
                group_id = self._get_group_id(condition, condition_group_id_map)

                if self._condition_exists_and_matches_field(
                    existing_condition, numeric_field_id
                ):
                    self._prepare_condition_update(
                        existing_condition, condition, group_id
                    )
                    conditions_to_update.append(existing_condition)
                    condition_ids_to_delete.remove(existing_condition.id)
                else:
                    new_condition = self._prepare_new_condition(
                        updated_field_option_instance, condition, group_id
                    )
                    conditions_to_create.append(new_condition)

        return conditions_to_create, conditions_to_update, condition_ids_to_delete

    def _update_field_options_conditions(
        self,
        view: View,
        field_options: Dict[str, Any],
        existing_conditions: Dict[int, FormViewFieldOptionsCondition],
        table_field_ids: Set[int],
        updated_field_options_by_field_id: Dict[int, FormViewFieldOptions],
        condition_group_id_map: Dict[int, FormViewFieldOptionsConditionGroup],
    ):
        """
        Updates the conditions for the specified field options. Based on the new
        provided field options and the existing conditions, this function figures out
        which conditions need to be created, updated or deleted in order to match the
        options provided.

        :param view: The form view instance.
        :param field_options: The field options that are being updated.
        :param existing_conditions: A map containing the existing conditions by id.
        :param table_field_ids: A set containing all the field ids that belong to the
            table.
        :param updated_field_options_by_field_id: A map containing the updated field
            options by field id.
        :param condition_group_id_map: A map containing the condition group ids by
            temporary id.
        """

        (
            conditions_to_create,
            conditions_to_update,
            condition_ids_to_delete,
        ) = self._prepare_conditions(
            field_options,
            updated_field_options_by_field_id,
            existing_conditions,
            condition_group_id_map,
            view.table_id,
            table_field_ids,
        )

        if len(conditions_to_create) > 0:
            FormViewFieldOptionsCondition.objects.bulk_create(conditions_to_create)

        if len(conditions_to_update) > 0:
            FormViewFieldOptionsCondition.objects.bulk_update(
                conditions_to_update, ["field_id", "type", "value"]
            )

        if len(condition_ids_to_delete) > 0:
            FormViewFieldOptionsCondition.objects.filter(
                id__in=condition_ids_to_delete
            ).delete()

    def after_field_options_update(
        self, view, field_options, fields, update_field_option_instances
    ):
        """
        This method is called directly after the form view field options are updated.
        It will create, update or delete the provided conditions in a query efficient
        manner.
        """

        field_ids = {field.id for field in fields}
        updated_field_options_by_field_id = {
            o.field_id: o for o in update_field_option_instances
        }
        updated_field_options = [
            updated_field_options_by_field_id[field_id]
            for field_id, options in field_options.items()
            if "conditions" in options
        ]

        # Prefetch all the existing conditions to avoid N amount of queries later on.
        existing_conditions = {
            c.id: c
            for c in FormViewFieldOptionsCondition.objects.filter(
                field_option__in=updated_field_options,
            ).select_related("field_option")
        }
        existing_condition_groups = {
            g.id: g
            for g in FormViewFieldOptionsConditionGroup.objects.filter(
                field_option__in=updated_field_options,
            ).select_related("field_option")
        }

        condition_group_ids_map = self._update_field_options_condition_groups(
            field_options,
            updated_field_options_by_field_id,
            existing_condition_groups,
        )

        self._update_field_options_conditions(
            view,
            field_options,
            existing_conditions,
            field_ids,
            updated_field_options_by_field_id,
            condition_group_ids_map,
        )

        # Delete all groups that have no conditions anymore.
        FormViewFieldOptionsConditionGroup.objects.filter(
            field_option__in=updated_field_options
        ).annotate(
            count=Count("conditions") + Count("formviewfieldoptionsconditiongroup")
        ).filter(
            count=0
        ).delete()

        self._update_field_options_allowed_select_options(
            view, field_options, updated_field_options_by_field_id
        )

    def _update_field_options_allowed_select_options(
        self, view, field_options, updated_field_options_by_field_id
    ):
        # Dict containing the field options object as key and a list of desired field
        # option IDs based on the provided `field_options`.
        desired_allowed_select_options = {}
        for field_id, options in field_options.items():
            field_options_id = updated_field_options_by_field_id[int(field_id)]
            if "allowed_select_options" in options:
                desired_allowed_select_options[field_options_id] = options[
                    "allowed_select_options"
                ]

        # No need to execute any query if no select options have been provided.
        if len(desired_allowed_select_options) == 0:
            return

        # Fetch the available select options per field, so that we can check whether
        # the provided select option is allowed.
        select_options_per_field_options_field = defaultdict(list)
        for select_option in SelectOption.objects.filter(
            field__in=[
                field_id
                for field_id, options in field_options.items()
                if "allowed_select_options" in options
            ]
        ).values("field_id", "id"):
            select_options_per_field_options_field[select_option["field_id"]].append(
                select_option["id"]
            )

        # Fetch the existing allowed select options of the updated field options,
        # so that we can compare with the `desired_allowed_select_options` and figure
        # out which one must be created and deleted.
        existing_allowed_select_options = defaultdict(list)
        for (
            allowed_select_option
        ) in FormViewFieldOptionsAllowedSelectOptions.objects.filter(
            form_view_field_options__in=[
                updated_field_options_by_field_id[field_id].id
                for field_id, options in field_options.items()
                if "allowed_select_options" in options
            ],
        ):
            existing_allowed_select_options[
                allowed_select_option.form_view_field_options_id
            ].append(allowed_select_option.select_option_id)

        to_create = []
        to_delete = []

        for (
            form_view_field_options,
            desired_select_options,
        ) in desired_allowed_select_options.items():
            existing_select_options = set(
                existing_allowed_select_options.get(form_view_field_options.id, [])
            )
            desired_select_options = set(desired_select_options)

            for select_option_id in desired_select_options - existing_select_options:
                if (
                    select_option_id
                    not in select_options_per_field_options_field[
                        form_view_field_options.field_id
                    ]
                ):
                    raise SelectOptionDoesNotBelongToField(
                        select_option_id, form_view_field_options.field_id
                    )
                to_create.append(
                    FormViewFieldOptionsAllowedSelectOptions(
                        form_view_field_options_id=form_view_field_options.id,
                        select_option_id=select_option_id,
                    )
                )

            for select_option_id in existing_select_options - desired_select_options:
                to_delete.append(select_option_id)

        if to_delete:
            FormViewFieldOptionsAllowedSelectOptions.objects.filter(
                form_view_field_options__in=desired_allowed_select_options.keys(),
                select_option_id__in=to_delete,
            ).delete()

        if to_create:
            FormViewFieldOptionsAllowedSelectOptions.objects.bulk_create(to_create)

    def export_serialized(
        self,
        form: View,
        cache: Optional[Dict] = None,
        files_zip: Optional[ExportZipFile] = None,
        storage: Optional[Storage] = None,
    ):
        """
        Adds the serialized form view options to the exported dict.
        """

        serialized = super().export_serialized(form, cache, files_zip, storage)

        def add_user_file(user_file):
            if not user_file:
                return None

            name = user_file.name
            namelist = (
                [item["name"] for item in files_zip.info_list()]
                if files_zip is not None
                else []
            )
            if files_zip is not None and name not in namelist:
                file_path = UserFileHandler().user_file_path(name)

                chunk_generator = file_chunk_generator(storage, file_path)
                files_zip.add(chunk_generator, name)

            return {"name": name, "original_name": user_file.original_name}

        serialized["title"] = form.title
        serialized["description"] = form.description
        serialized["cover_image"] = add_user_file(form.cover_image)
        serialized["logo_image"] = add_user_file(form.logo_image)
        serialized["submit_text"] = form.submit_text
        serialized["submit_action"] = form.submit_action
        serialized["submit_action_message"] = form.submit_action_message
        serialized["submit_action_redirect_url"] = form.submit_action_redirect_url

        serialized_field_options = []
        for field_option in form.get_field_options():
            serialized_field_options.append(
                {
                    "id": field_option.id,
                    "field_id": field_option.field_id,
                    "name": field_option.name,
                    "description": field_option.description,
                    "enabled": field_option.enabled,
                    "required": field_option.required,
                    "order": field_option.order,
                    "show_when_matching_conditions": field_option.show_when_matching_conditions,
                    "condition_type": field_option.condition_type,
                    "conditions": [
                        {
                            "id": condition.id,
                            "field": condition.field_id,
                            "type": condition.type,
                            "group": condition.group_id,
                            "value": view_filter_type_registry.get(
                                condition.type
                            ).get_export_serialized_value(condition.value, {}),
                        }
                        for condition in field_option.conditions.all()
                    ],
                    "condition_groups": [
                        {
                            "id": condition_group.id,
                            "parent_group": condition_group.parent_group_id,
                            "filter_type": condition_group.filter_type,
                        }
                        for condition_group in field_option.condition_groups.all()
                    ],
                    "field_component": field_option.field_component,
                    "include_all_select_options": field_option.include_all_select_options,
                    "allowed_select_options": [
                        s.id for s in field_option.allowed_select_options.all()
                    ],
                }
            )

        serialized["field_options"] = serialized_field_options
        return serialized

    def import_serialized(
        self,
        table: Table,
        serialized_values: Dict[str, Any],
        id_mapping: Dict[str, Any],
        files_zip: Optional[ZipFile] = None,
        storage: Optional[Storage] = None,
    ) -> Optional[View]:
        """
        Imports the serialized form view and field options.
        """

        def get_file(file):
            if not file:
                return None

            if files_zip is None:
                user_file = UserFileHandler().get_user_file_by_name(file["name"])
            else:
                with files_zip.open(file["name"]) as stream:
                    user_file = UserFileHandler().upload_user_file(
                        None, file["original_name"], stream, storage=storage
                    )
            return user_file

        serialized_copy = serialized_values.copy()
        serialized_copy["cover_image"] = get_file(serialized_copy.pop("cover_image"))
        serialized_copy["logo_image"] = get_file(serialized_copy.pop("logo_image"))
        field_options = serialized_copy.pop("field_options")
        form_view = super().import_serialized(
            table, serialized_copy, id_mapping, files_zip, storage
        )

        if form_view is not None:
            if "database_form_view_field_options" not in id_mapping:
                id_mapping["database_form_view_field_options"] = {}
                id_mapping["database_form_view_condition_groups"] = {}

            condition_objects = []
            form_view_field_options_allowed_select_options = []
            for field_option in field_options:
                field_option_copy = field_option.copy()
                field_option_id = field_option_copy.pop("id")
                field_option_conditions = field_option_copy.pop("conditions", [])
                field_option_condition_groups = field_option_copy.pop(
                    "condition_groups", []
                )
                allowed_select_options = field_option_copy.pop(
                    "allowed_select_options", []
                )
                field_option_copy["field_id"] = id_mapping["database_fields"][
                    field_option["field_id"]
                ]
                field_option_object = FormViewFieldOptions.objects.create(
                    form_view=form_view, **field_option_copy
                )
                for condition_group in field_option_condition_groups:
                    condition_group_copy = condition_group.copy()
                    condition_group_id = condition_group_copy.pop("id")
                    if condition_group_copy["parent_group"]:
                        condition_group_copy["parent_group_id"] = id_mapping[
                            "database_form_view_condition_groups"
                        ][condition_group_copy.pop("parent_group")]
                    condition_group_object = (
                        FormViewFieldOptionsConditionGroup.objects.create(
                            field_option=field_option_object, **condition_group_copy
                        )
                    )
                    id_mapping["database_form_view_condition_groups"][
                        condition_group_id
                    ] = condition_group_object.id
                for condition in field_option_conditions:
                    value = view_filter_type_registry.get(
                        condition["type"]
                    ).set_import_serialized_value(condition["value"], id_mapping)
                    mapped_group_id = None
                    group = condition.get("group", None)
                    if group:
                        mapped_group_id = id_mapping[
                            "database_form_view_condition_groups"
                        ][group]
                    condition_objects.append(
                        FormViewFieldOptionsCondition(
                            field_option=field_option_object,
                            field_id=id_mapping["database_fields"][condition["field"]],
                            type=condition["type"],
                            value=value,
                            group_id=mapped_group_id,
                        )
                    )
                for select_option_id in allowed_select_options:
                    form_view_field_options_allowed_select_options.append(
                        FormViewFieldOptionsAllowedSelectOptions(
                            form_view_field_options_id=field_option_object.id,
                            select_option_id=id_mapping[
                                "database_field_select_options"
                            ][select_option_id],
                        )
                    )

                    field_option_object.id
                id_mapping["database_form_view_field_options"][
                    field_option_id
                ] = field_option_object.id

            # Create the objects in bulk to improve performance.
            FormViewFieldOptionsCondition.objects.bulk_create(condition_objects)
            FormViewFieldOptionsAllowedSelectOptions.objects.bulk_create(
                form_view_field_options_allowed_select_options
            )

        return form_view

    def get_visible_field_options_in_order(self, form_view):
        return (
            form_view.get_field_options(create_if_missing=True)
            .filter(enabled=True)
            .order_by("-field__primary", "order", "field__id")
        )

    def before_view_create(self, values: dict, table: "Table", user: AbstractUser):
        if "mode" in values:
            mode_type = form_view_mode_registry.get(values["mode"])
        else:
            # This is the default mode that's set when nothing is provided.
            mode_type = form_view_mode_registry.get_default_type()

        mode_type.before_form_create(values, table, user)

    def before_view_update(self, values: dict, view: "View", user: AbstractUser):
        mode_type = form_view_mode_registry.get(values.get("mode", view.mode))
        mode_type.before_form_update(values, view, user)

        notify_on_submit = values.pop("receive_notification_on_submit", None)
        if notify_on_submit is not None:
            users_to_notify_on_submit = [
                utn.id
                for utn in view.users_to_notify_on_submit.all()
                if utn.id != user.id
            ]
            if notify_on_submit:
                users_to_notify_on_submit.append(user.id)
            values["users_to_notify_on_submit"] = users_to_notify_on_submit

    def prepare_values(
        self, values: Dict[str, Any], table: Table, user: AbstractUser
    ) -> Dict[str, Any]:
        """
        Prepares the values for the form view.
        If a serialized version of UserFile is found, it will be converted to a
        UserFile object.

        :param values: The values to prepare.
        :param table: The table the form view belongs to.
        :param user: The user that is submitting the form.
        :raises: ValidationError if the provided value for images is not
            compatible with UserFile.
        :return: The prepared values.
        """

        for user_file_key in ["cover_image", "logo_image"]:
            user_file = values.get(user_file_key, None)

            if user_file is None:
                continue

            if isinstance(user_file, dict):
                values[user_file_key] = UserFileHandler().get_user_file_by_name(
                    user_file.get("name", None)
                )

            elif not isinstance(user_file, UserFile):
                raise ValidationError(
                    f"Invalid user file type. '{user_file_key}' should be a UserFile \
                        instance or the serialized version of it."
                )

        return super().prepare_values(values, table, user)

    def export_prepared_values(self, view: FormView) -> Dict[str, Any]:
        """
        Add form fields to the exportable fields for undo/redo.
        This is the counterpart of prepare_values. Starting from object instances,
        it exports data to a serialized version of the object, in a way that
        prepare_values can be used to import it.

        :param view: The gallery view to export.
        :return: The prepared values.
        """

        values = super().export_prepared_values(view)

        for field in ["cover_image", "logo_image"]:
            user_file = getattr(view, field)
            values[field] = user_file and user_file.serialize()

        return values

    def enhance_queryset(self, queryset):
        return queryset.prefetch_related(
            "formviewfieldoptions_set", "users_to_notify_on_submit"
        )

    def enhance_field_options_queryset(self, queryset):
        return queryset.prefetch_related(
            "conditions", "condition_groups", "allowed_select_options"
        )

    def prepare_field_options(
        self, view: FormView, field_id: int
    ) -> FormViewFieldOptions:
        return FormViewFieldOptions(
            field_id=field_id, form_view_id=view.id, enabled=False
        )

    def check_view_update_permissions(self, user, view, data):
        from .operations import CanReceiveNotificationOnSubmitFormViewOperationType

        workspace = view.table.database.workspace

        if "receive_notification_on_submit" in data:
            # If `receive_notification_on_submit` is in the data, then we must check if
            # the user has permissions to receive a notification on submit.
            CoreHandler().check_permissions(
                user,
                CanReceiveNotificationOnSubmitFormViewOperationType.type,
                workspace=workspace,
                context=view,
            )

            # If only the `receive_notification_on_submit` is provided, then there is
            # no need to check if the user has permissions to update the view because
            # nothing else is changed.
            if len(data) == 1:
                return

        return super().check_view_update_permissions(user, view, data)


class KanbanViewType(ViewType):
    type = "kanban"
    model_class = None  # Will be set after import
    field_options_model_class = None  # Will be set after import
    field_options_serializer_class = None  # Will be set after import
    allowed_fields = [
        "single_select_field",
        "card_cover_image_field", 
        "stack_by_field",
        "card_configuration",
        "column_configuration",
    ]
    field_options_allowed_fields = [
        "hidden",
        "order",
        "show_in_card",
        "card_display_style",
    ]
    serializer_field_names = [
        "single_select_field",
        "card_cover_image_field",
        "stack_by_field", 
        "card_configuration",
        "column_configuration",
    ]
    serializer_field_overrides = {
        "single_select_field": serializers.PrimaryKeyRelatedField(
            queryset=Field.objects.all(),
            required=False,
            default=None,
            allow_null=True,
            help_text="References a single select field that determines the Kanban columns.",
        ),
        "card_cover_image_field": serializers.PrimaryKeyRelatedField(
            queryset=Field.objects.all(),
            required=False,
            default=None,
            allow_null=True,
            help_text="References a file field of which the first image must be shown as card cover image.",
        ),
        "stack_by_field": serializers.PrimaryKeyRelatedField(
            queryset=Field.objects.all(),
            required=False,
            default=None,
            allow_null=True,
            help_text="Field used to stack cards in columns.",
        ),
    }
    api_exceptions_map = {
        FieldNotInTable: ERROR_FIELD_NOT_IN_TABLE,
        IncompatibleField: ERROR_INCOMPATIBLE_FIELD,
    }
    can_decorate = True
    can_share = True
    has_public_info = True

    def __init__(self):
        # Import here to avoid circular imports
        from .models import KanbanView, KanbanViewFieldOptions
        
        self.model_class = KanbanView
        self.field_options_model_class = KanbanViewFieldOptions
        
        # Set the serializer class dynamically to avoid circular imports
        try:
            from baserow.contrib.database.api.views.kanban.serializers import KanbanViewFieldOptionsSerializer
            self.field_options_serializer_class = KanbanViewFieldOptionsSerializer
        except ImportError:
            # Fallback if serializer is not available yet
            self.field_options_serializer_class = None

    def get_api_urls(self):
        from baserow.contrib.database.api.views.kanban import urls as api_urls

        return [
            path("kanban/", include(api_urls, namespace=self.type)),
        ]

    def prepare_values(self, values, table, user):
        """
        Check if the provided fields belong to the same table and are compatible.
        """
        
        # Check single_select_field
        if values.get("single_select_field", None) is not None:
            if isinstance(values["single_select_field"], int):
                values["single_select_field"] = Field.objects.get(pk=values["single_select_field"])
            
            field_type = field_type_registry.get_by_model(values["single_select_field"].specific)
            if field_type.type != "single_select":
                raise IncompatibleField(
                    "The provided field cannot be used as a single select field for Kanban columns."
                )
            elif values["single_select_field"].table_id != table.id:
                raise FieldNotInTable(
                    "The provided single select field does not belong to the Kanban view's table."
                )

        # Check card_cover_image_field
        if values.get("card_cover_image_field", None) is not None:
            if isinstance(values["card_cover_image_field"], int):
                values["card_cover_image_field"] = Field.objects.get(pk=values["card_cover_image_field"])

            field_type = field_type_registry.get_by_model(values["card_cover_image_field"].specific)
            if not field_type.can_represent_files(values["card_cover_image_field"]):
                raise IncompatibleField(
                    "The provided field cannot be used as a card cover image field."
                )
            elif values["card_cover_image_field"].table_id != table.id:
                raise FieldNotInTable(
                    "The provided file field does not belong to the Kanban view's table."
                )

        # Check stack_by_field
        if values.get("stack_by_field", None) is not None:
            if isinstance(values["stack_by_field"], int):
                values["stack_by_field"] = Field.objects.get(pk=values["stack_by_field"])
            
            if values["stack_by_field"].table_id != table.id:
                raise FieldNotInTable(
                    "The provided stack by field does not belong to the Kanban view's table."
                )

        return super().prepare_values(values, table, user)

    def after_fields_type_change(self, fields):
        """
        Handle field type changes that might affect Kanban view configuration.
        """
        from .models import KanbanView
        
        # Handle single_select_field changes
        fields_not_single_select = [
            field for field in fields
            if field_type_registry.get_by_model(field.specific_class).type != "single_select"
        ]
        if len(fields_not_single_select) > 0:
            KanbanView.objects.filter(
                single_select_field_id__in=[f.id for f in fields_not_single_select]
            ).update(single_select_field_id=None)

        # Handle card_cover_image_field changes
        fields_cannot_represent_files = [
            field for field in fields
            if not field_type_registry.get_by_model(field.specific_class).can_represent_files(field)
        ]
        if len(fields_cannot_represent_files) > 0:
            KanbanView.objects.filter(
                card_cover_image_field_id__in=[f.id for f in fields_cannot_represent_files]
            ).update(card_cover_image_field_id=None)

    def export_serialized(
        self,
        kanban: "KanbanView",
        cache: Optional[Dict] = None,
        files_zip: Optional[ExportZipFile] = None,
        storage: Optional[Storage] = None,
    ):
        """
        Adds the serialized kanban view options to the exported dict.
        """

        serialized = super().export_serialized(kanban, cache, files_zip, storage)

        if kanban.single_select_field_id:
            serialized["single_select_field_id"] = kanban.single_select_field_id
        if kanban.card_cover_image_field_id:
            serialized["card_cover_image_field_id"] = kanban.card_cover_image_field_id
        if kanban.stack_by_field_id:
            serialized["stack_by_field_id"] = kanban.stack_by_field_id
        
        serialized["card_configuration"] = kanban.card_configuration
        serialized["column_configuration"] = kanban.column_configuration

        serialized_field_options = []
        for field_option in kanban.get_field_options():
            serialized_field_options.append(
                {
                    "id": field_option.id,
                    "field_id": field_option.field_id,
                    "hidden": field_option.hidden,
                    "order": field_option.order,
                    "show_in_card": field_option.show_in_card,
                    "card_display_style": field_option.card_display_style,
                }
            )

        serialized["field_options"] = serialized_field_options
        return serialized

    def import_serialized(
        self,
        table: Table,
        serialized_values: Dict[str, Any],
        id_mapping: Dict[str, Any],
        files_zip: Optional[ZipFile] = None,
        storage: Optional[Storage] = None,
    ) -> Optional["KanbanView"]:
        """
        Imports the serialized kanban view field options.
        """
        from .models import KanbanView, KanbanViewFieldOptions

        serialized_copy = serialized_values.copy()

        # Map field references
        if serialized_copy.get("single_select_field_id", None):
            serialized_copy["single_select_field_id"] = id_mapping["database_fields"][
                serialized_copy["single_select_field_id"]
            ]
        if serialized_copy.get("card_cover_image_field_id", None):
            serialized_copy["card_cover_image_field_id"] = id_mapping["database_fields"][
                serialized_copy["card_cover_image_field_id"]
            ]
        if serialized_copy.get("stack_by_field_id", None):
            serialized_copy["stack_by_field_id"] = id_mapping["database_fields"][
                serialized_copy["stack_by_field_id"]
            ]

        field_options = serialized_copy.pop("field_options")

        kanban_view = super().import_serialized(
            table, serialized_copy, id_mapping, files_zip, storage
        )

        if kanban_view is not None:
            if "database_kanban_view_field_options" not in id_mapping:
                id_mapping["database_kanban_view_field_options"] = {}

            for field_option in field_options:
                field_option_copy = field_option.copy()
                field_option_id = field_option_copy.pop("id")
                field_option_copy["field_id"] = id_mapping["database_fields"][
                    field_option["field_id"]
                ]
                field_option_object = KanbanViewFieldOptions.objects.create(
                    kanban_view=kanban_view, **field_option_copy
                )
                id_mapping["database_kanban_view_field_options"][
                    field_option_id
                ] = field_option_object.id

        return kanban_view

    def view_created(self, view):
        """
        When a kanban view is created, we want to set the first few fields as visible on cards.
        """
        from .models import KanbanViewFieldOptions
        
        field_options = view.get_field_options(create_if_missing=True).order_by(
            "-field__primary", "field__id"
        )
        ids_to_update = [f.id for f in field_options[0:3]]

        if ids_to_update:
            KanbanViewFieldOptions.objects.filter(id__in=ids_to_update).update(
                hidden=False, show_in_card=True
            )

    def export_prepared_values(self, view: "KanbanView") -> Dict[str, Any]:
        """
        Add kanban-specific fields to the exportable fields.
        """

        values = super().export_prepared_values(view)
        values["single_select_field"] = view.single_select_field_id
        values["card_cover_image_field"] = view.card_cover_image_field_id
        values["stack_by_field"] = view.stack_by_field_id
        values["card_configuration"] = view.card_configuration
        values["column_configuration"] = view.column_configuration

        return values

    def get_visible_field_options_in_order(self, kanban_view: "KanbanView"):
        """
        Returns field options that should be visible on cards.
        """
        return (
            kanban_view.get_field_options(create_if_missing=True)
            .filter(
                Q(show_in_card=True) | Q(field__id=kanban_view.card_cover_image_field_id)
            )
            .order_by("order", "field__id")
        )

    def get_hidden_fields(
        self,
        view: "KanbanView", 
        field_ids_to_check: Optional[List[int]] = None,
    ) -> Set[int]:
        """
        Returns the set of field IDs that should be hidden in this view.
        """
        hidden_field_ids = set()
        fields = view.table.field_set.all()
        field_options = view.kanbanviewfieldoptions_set.all()

        if field_ids_to_check is not None:
            fields = [f for f in fields if f.id in field_ids_to_check]

        for field in fields:
            # The card cover image field is always visible
            if field.id == view.card_cover_image_field_id:
                continue

            # Find corresponding field option
            field_option_matching = None
            for field_option in field_options:
                if field_option.field_id == field.id:
                    field_option_matching = field_option

            # A field is considered hidden if it's explicitly hidden or if field options don't exist
            if field_option_matching is None or field_option_matching.hidden:
                hidden_field_ids.add(field.id)

        return hidden_field_ids

    def enhance_queryset(self, queryset):
        return queryset.prefetch_related("kanbanviewfieldoptions_set")

    def after_field_delete(self, field: Field) -> None:
        """
        Clean up field references when a field is deleted.
        """
        from .models import KanbanView
        from baserow.contrib.database.fields.models import FileField, SingleSelectField
        
        if isinstance(field, FileField):
            KanbanView.objects.filter(card_cover_image_field_id=field.id).update(
                card_cover_image_field_id=None
            )
        
        if isinstance(field, SingleSelectField):
            KanbanView.objects.filter(single_select_field_id=field.id).update(
                single_select_field_id=None
            )
            KanbanView.objects.filter(stack_by_field_id=field.id).update(
                stack_by_field_id=None
            )


class CalendarViewType(ViewType):
    type = "calendar"
    model_class = None  # Will be set after import
    field_options_model_class = None  # Will be set after import
    field_options_serializer_class = None  # Will be set after import
    allowed_fields = [
        "date_field",
        "display_mode",
        "event_title_field",
        "event_color_field",
        "enable_recurring_events",
        "recurring_pattern_field",
        "external_calendar_config",
        "enable_external_sync",
    ]
    field_options_allowed_fields = [
        "hidden",
        "order",
        "show_in_event",
        "event_display_style",
    ]
    serializer_field_names = [
        "date_field",
        "display_mode",
        "event_title_field",
        "event_color_field",
        "enable_recurring_events",
        "recurring_pattern_field",
        "external_calendar_config",
        "enable_external_sync",
    ]
    serializer_field_overrides = {
        "date_field": serializers.PrimaryKeyRelatedField(
            queryset=Field.objects.all(),
            required=False,
            default=None,
            allow_null=True,
            help_text="Date field used to position events on the calendar",
        ),
        "event_title_field": serializers.PrimaryKeyRelatedField(
            queryset=Field.objects.all(),
            required=False,
            default=None,
            allow_null=True,
            help_text="Field used as the event title",
        ),
        "event_color_field": serializers.PrimaryKeyRelatedField(
            queryset=Field.objects.all(),
            required=False,
            default=None,
            allow_null=True,
            help_text="Field used to determine event colors",
        ),
        "recurring_pattern_field": serializers.PrimaryKeyRelatedField(
            queryset=Field.objects.all(),
            required=False,
            default=None,
            allow_null=True,
            help_text="Field containing recurring event pattern configuration",
        ),
    }
    api_exceptions_map = {
        FieldNotInTable: ERROR_FIELD_NOT_IN_TABLE,
        IncompatibleField: ERROR_INCOMPATIBLE_FIELD,
    }
    can_decorate = True
    can_share = True
    has_public_info = True

    def __init__(self):
        # Import here to avoid circular imports
        from .models import CalendarView, CalendarViewFieldOptions
        
        self.model_class = CalendarView
        self.field_options_model_class = CalendarViewFieldOptions
        
        # Set the serializer class dynamically to avoid circular imports
        try:
            from baserow.contrib.database.api.views.calendar.serializers import CalendarViewFieldOptionsSerializer
            self.field_options_serializer_class = CalendarViewFieldOptionsSerializer
        except ImportError:
            # Fallback if serializer is not available yet
            self.field_options_serializer_class = None

    def get_api_urls(self):
        from baserow.contrib.database.api.views.calendar import urls as api_urls

        return [
            path("calendar/", include(api_urls, namespace=self.type)),
        ]

    def prepare_values(self, values, table, user):
        """
        Check if the provided fields belong to the same table and are compatible.
        """
        
        # Check date_field
        if values.get("date_field", None) is not None:
            if isinstance(values["date_field"], int):
                values["date_field"] = Field.objects.get(pk=values["date_field"])
            
            field_type = field_type_registry.get_by_model(values["date_field"].specific)
            if not field_type.can_represent_date(values["date_field"]):
                raise IncompatibleField(
                    "The provided field is not a date field and cannot be used as a calendar date field."
                )
            elif values["date_field"].table_id != table.id:
                raise FieldNotInTable(
                    "The provided date field does not belong to the calendar view's table."
                )

        # Check event_title_field
        if values.get("event_title_field", None) is not None:
            if isinstance(values["event_title_field"], int):
                values["event_title_field"] = Field.objects.get(pk=values["event_title_field"])
            
            if values["event_title_field"].table_id != table.id:
                raise FieldNotInTable(
                    "The provided event title field does not belong to the calendar view's table."
                )

        # Check event_color_field
        if values.get("event_color_field", None) is not None:
            if isinstance(values["event_color_field"], int):
                values["event_color_field"] = Field.objects.get(pk=values["event_color_field"])
            
            if values["event_color_field"].table_id != table.id:
                raise FieldNotInTable(
                    "The provided event color field does not belong to the calendar view's table."
                )

        # Check recurring_pattern_field
        if values.get("recurring_pattern_field", None) is not None:
            if isinstance(values["recurring_pattern_field"], int):
                values["recurring_pattern_field"] = Field.objects.get(pk=values["recurring_pattern_field"])
            
            if values["recurring_pattern_field"].table_id != table.id:
                raise FieldNotInTable(
                    "The provided recurring pattern field does not belong to the calendar view's table."
                )

        return super().prepare_values(values, table, user)

    def after_fields_type_change(self, fields):
        """
        Handle field type changes that might affect Calendar view configuration.
        """
        from .models import CalendarView
        
        # Handle date_field changes
        fields_not_date = [
            field for field in fields
            if not field_type_registry.get_by_model(field.specific_class).can_represent_date(field)
        ]
        if len(fields_not_date) > 0:
            CalendarView.objects.filter(
                date_field_id__in=[f.id for f in fields_not_date]
            ).update(date_field_id=None)

    def export_serialized(
        self,
        calendar: "CalendarView",
        cache: Optional[Dict] = None,
        files_zip: Optional[ExportZipFile] = None,
        storage: Optional[Storage] = None,
    ):
        """
        Adds the serialized calendar view options to the exported dict.
        """

        serialized = super().export_serialized(calendar, cache, files_zip, storage)

        if calendar.date_field_id:
            serialized["date_field_id"] = calendar.date_field_id
        if calendar.event_title_field_id:
            serialized["event_title_field_id"] = calendar.event_title_field_id
        if calendar.event_color_field_id:
            serialized["event_color_field_id"] = calendar.event_color_field_id
        if calendar.recurring_pattern_field_id:
            serialized["recurring_pattern_field_id"] = calendar.recurring_pattern_field_id
        
        serialized["display_mode"] = calendar.display_mode
        serialized["enable_recurring_events"] = calendar.enable_recurring_events
        serialized["external_calendar_config"] = calendar.external_calendar_config
        serialized["enable_external_sync"] = calendar.enable_external_sync

        serialized_field_options = []
        for field_option in calendar.get_field_options():
            serialized_field_options.append(
                {
                    "id": field_option.id,
                    "field_id": field_option.field_id,
                    "hidden": field_option.hidden,
                    "order": field_option.order,
                    "show_in_event": field_option.show_in_event,
                    "event_display_style": field_option.event_display_style,
                }
            )

        serialized["field_options"] = serialized_field_options
        return serialized

    def import_serialized(
        self,
        table: Table,
        serialized_values: Dict[str, Any],
        id_mapping: Dict[str, Any],
        files_zip: Optional[ZipFile] = None,
        storage: Optional[Storage] = None,
    ) -> Optional["CalendarView"]:
        """
        Imports the serialized calendar view field options.
        """
        from .models import CalendarView, CalendarViewFieldOptions

        serialized_copy = serialized_values.copy()

        # Map field references
        if serialized_copy.get("date_field_id", None):
            serialized_copy["date_field_id"] = id_mapping["database_fields"][
                serialized_copy["date_field_id"]
            ]
        if serialized_copy.get("event_title_field_id", None):
            serialized_copy["event_title_field_id"] = id_mapping["database_fields"][
                serialized_copy["event_title_field_id"]
            ]
        if serialized_copy.get("event_color_field_id", None):
            serialized_copy["event_color_field_id"] = id_mapping["database_fields"][
                serialized_copy["event_color_field_id"]
            ]
        if serialized_copy.get("recurring_pattern_field_id", None):
            serialized_copy["recurring_pattern_field_id"] = id_mapping["database_fields"][
                serialized_copy["recurring_pattern_field_id"]
            ]

        field_options = serialized_copy.pop("field_options")

        calendar_view = super().import_serialized(
            table, serialized_copy, id_mapping, files_zip, storage
        )

        if calendar_view is not None:
            if "database_calendar_view_field_options" not in id_mapping:
                id_mapping["database_calendar_view_field_options"] = {}

            for field_option in field_options:
                field_option_copy = field_option.copy()
                field_option_id = field_option_copy.pop("id")
                field_option_copy["field_id"] = id_mapping["database_fields"][
                    field_option["field_id"]
                ]
                field_option_object = CalendarViewFieldOptions.objects.create(
                    calendar_view=calendar_view, **field_option_copy
                )
                id_mapping["database_calendar_view_field_options"][
                    field_option_id
                ] = field_option_object.id

        return calendar_view

    def view_created(self, view):
        """
        When a calendar view is created, we want to set the first few fields as visible in events.
        """
        from .models import CalendarViewFieldOptions
        
        field_options = view.get_field_options(create_if_missing=True).order_by(
            "-field__primary", "field__id"
        )
        ids_to_update = [f.id for f in field_options[0:3]]

        if ids_to_update:
            CalendarViewFieldOptions.objects.filter(id__in=ids_to_update).update(
                hidden=False, show_in_event=True
            )

    def export_prepared_values(self, view: "CalendarView") -> Dict[str, Any]:
        """
        Add calendar-specific fields to the exportable fields.
        """

        values = super().export_prepared_values(view)
        values["date_field"] = view.date_field_id
        values["display_mode"] = view.display_mode
        values["event_title_field"] = view.event_title_field_id
        values["event_color_field"] = view.event_color_field_id
        values["enable_recurring_events"] = view.enable_recurring_events
        values["recurring_pattern_field"] = view.recurring_pattern_field_id
        values["external_calendar_config"] = view.external_calendar_config
        values["enable_external_sync"] = view.enable_external_sync

        return values

    def get_visible_field_options_in_order(self, calendar_view: "CalendarView"):
        """
        Returns field options that should be visible in events.
        """
        return (
            calendar_view.get_field_options(create_if_missing=True)
            .filter(
                Q(show_in_event=True) 
                | Q(field__id=calendar_view.date_field_id)
                | Q(field__id=calendar_view.event_title_field_id)
            )
            .order_by("order", "field__id")
        )

    def get_hidden_fields(
        self,
        view: "CalendarView", 
        field_ids_to_check: Optional[List[int]] = None,
    ) -> Set[int]:
        """
        Returns the set of field IDs that should be hidden in this view.
        """
        hidden_field_ids = set()
        fields = view.table.field_set.all()
        field_options = view.calendarviewfieldoptions_set.all()

        if field_ids_to_check is not None:
            fields = [f for f in fields if f.id in field_ids_to_check]

        for field in fields:
            # The date field and event title field are always visible
            if field.id in [view.date_field_id, view.event_title_field_id]:
                continue

            # Find corresponding field option
            field_option_matching = None
            for field_option in field_options:
                if field_option.field_id == field.id:
                    field_option_matching = field_option

            # A field is considered hidden if it's explicitly hidden or if field options don't exist
            if field_option_matching is None or field_option_matching.hidden:
                hidden_field_ids.add(field.id)

        return hidden_field_ids

    def enhance_queryset(self, queryset):
        return queryset.prefetch_related("calendarviewfieldoptions_set")

    def after_field_delete(self, field: Field) -> None:
        """
        Clean up field references when a field is deleted.
        """
        from .models import CalendarView
        
        CalendarView.objects.filter(date_field_id=field.id).update(
            date_field_id=None
        )
        CalendarView.objects.filter(event_title_field_id=field.id).update(
            event_title_field_id=None
        )
        CalendarView.objects.filter(event_color_field_id=field.id).update(
            event_color_field_id=None
        )
        CalendarView.objects.filter(recurring_pattern_field_id=field.id).update(
            recurring_pattern_field_id=None
        )