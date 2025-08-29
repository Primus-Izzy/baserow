from django.urls import re_path

from .views import (
    FormUploadFileView, 
    SubmitFormViewView,
    EnhancedFormViewCustomBrandingView,
    EnhancedFormViewAccessControlView,
    EnhancedFormViewValidationConfigView,
    EnhancedFormViewShareableLinksView,
    EnhancedFormViewShareableLinkDetailView,
    EnhancedFormViewFieldOptionsView,
)

app_name = "baserow.contrib.database.api.views.form"

urlpatterns = [
    re_path(
        r"(?P<slug>[-\w]+)/submit/$",
        SubmitFormViewView.as_view(),
        name="submit",
    ),
    re_path(
        r"^(?P<slug>[-\w]+)/upload-file/$",
        FormUploadFileView.as_view(),
        name="upload_file",
    ),
    # Enhanced form view endpoints
    re_path(
        r"^(?P<view_id>[0-9]+)/custom-branding/$",
        EnhancedFormViewCustomBrandingView.as_view(),
        name="custom_branding",
    ),
    re_path(
        r"^(?P<view_id>[0-9]+)/access-control/$",
        EnhancedFormViewAccessControlView.as_view(),
        name="access_control",
    ),
    re_path(
        r"^(?P<view_id>[0-9]+)/validation-config/$",
        EnhancedFormViewValidationConfigView.as_view(),
        name="validation_config",
    ),
    re_path(
        r"^(?P<view_id>[0-9]+)/shareable-links/$",
        EnhancedFormViewShareableLinksView.as_view(),
        name="shareable_links",
    ),
    re_path(
        r"^(?P<view_id>[0-9]+)/shareable-links/(?P<link_id>[-\w]+)/$",
        EnhancedFormViewShareableLinkDetailView.as_view(),
        name="shareable_link_detail",
    ),
    re_path(
        r"^(?P<view_id>[0-9]+)/field-options/(?P<field_id>[0-9]+)/$",
        EnhancedFormViewFieldOptionsView.as_view(),
        name="field_options",
    ),
]
