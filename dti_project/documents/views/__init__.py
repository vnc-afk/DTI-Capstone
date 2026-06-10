from .create_views import (
    CreateSalesPromotionView,
    CreatePersonalDataSheetView,
    CreateServiceRepairAccreditationApplicationView,
    CreateInspectionValidationReportView,
    CreateOrderOfPaymentView,
    CreateChecklistEvaluationSheetView,
    CreateOtherBusinessRelatedFormView
)
from .detail_views import (
    SalesPromotionDetailView,
    PersonalDataSheetDetailView,
    ServiceRepairAccreditationApplicationDetailView,
    InspectionValidationReportDetailView,
    OrderOfPaymentDetailView,
    ChecklistEvaluationSheetDetailView,
    CollectionReportDetailView,
    CollectionReportItemDetailView,
    OtherBusinessRelatedDetailView
)

from .update_views import (
    UpdateSalesPromotionView,
    UpdatePersonalDataSheetView,
    UpdateServiceRepairAccreditationApplicationView,
    UpdateInspectionValidationReportView,
    UpdateOrderOfPaymentView,
    UpdateChecklistEvaluationSheetView
)

from .list_views import (
    AllDocumentListView,
    SalesPromotionListView,
    PersonalDataSheetListView,
    ServiceRepairAccreditationApplicationListView,
    InspectionValidationReportListView,
    OrderOfPaymentListView,
    ChecklistEvaluationSheetListView,
    CollectionReportListView,
)

from .upload_excel_views import (
    UploadExcelView,
    ProcessUploadView,
    UploadProgressStreamView,
    CancelUploadView,
)

from .export_report_views import (
    ExportDocumentsExcelView
)

from .action_views import (
    ApproveDocumentsView,
    mark_all_notifications_as_read
)

from .generate_report_views import (
    GenerateDocumentsReportView
)

from .pdf_views import (
    view_oop,
)