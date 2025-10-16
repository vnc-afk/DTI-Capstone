# SERVICE_REPAIR_ACCREDITATION_FIELD_GROUPS defines the structure of each form step.
# Each item in the list represents a fieldset (form section) and follows this structure:
# (
#     "Fieldset Title",                  # str: Legend/title of the fieldset
#     [                                  # list: A list of rows
#         [field_name_1, field_name_2],  # Each row is a list of field names to be rendered together
#         [field_name_3],
#         ...
#     ],
#     "fieldset-id"                      # str: The HTML id attribute to assign to this fieldset
# )

# ---------- CREATE VIEW GROUPS ---------------- #

SALES_PROMOTION_FIELD_GROUPS = [
    ("Promotion Details", [['promo_title']], 'promo-title'),
    ("Sponsor", [
        ['sponsor_name', 'sponsor_telephone', 'sponsor_email', 'sponsor_authorized_rep', 'sponsor_designation',
        'sponsor_address']
    ], 'sponsors'),
    ("Advertising Agency", [[
        'advertising_agency_name', 
        'advertising_agency_telephone', 'advertising_agency_email', 'advertising_agency_authorized_rep',
        'advertising_agency_designation', 'advertising_agency_address'
    ]], 'advertising'),
    ("Promo Period",[['promo_period_start', 'promo_period_end']], 'promo-period'),
]

PERSONAL_DATA_SHEET_FIELD_GROUPS = [
    ("Personal Background", 
        [
            ['last_name', 'first_name', 'middle_name'],
            ['email_address', 'contact_number', 'current_address'],
            ['position', 'nationality', 'date_of_birth', 'sex', 'civil_status'],
            ['image']
        ],
        "personal-background"
    ),
]

SERVICE_REPAIR_ACCREDITATION_FIELD_GROUPS = [
    ("Application Details", [['application_type', 'category', 'star_rating']], 'application-details'),
    ("Business/Personal Information", [
        ['name_of_business'],
        ['building_name_or_number', 'street_name', 'region', 'province', 'city_or_municipality', 'barangay', 'zip_code'],
        ['email_address', 'mobile_number', 'telephone_number', 'fax_number'],
        ['sex', 'social_classification'] 
    ], 'business-information'),
    ("Authorized Signatory", [['first_name', 'middle_name', 'last_name', 'title', 'suffix', 'designation']], 'authorized-signatory'),
    ("Business Classification", 
     [
        ['asset_size', 'form_of_organization', 
         'industry_classification', 'annual_gross_service_revenue', 'capital_investment', 'tax_identification_number',
         'date_established', 'total_employees'
         ]
        
        ],
        'business-classification'
    ),
]

INSPECTION_VALIDATION_REPORT_FIELD_GROUPS = [
    ("Business Name and Address", [['name_of_business', 'address']], 'business'),

    ("Basic Information", [
        ['type_of_application_activity', 'years_in_service', 'types_of_office_shop'],
        ['business_name_cert', 'business_name_cert_remarks'],
        ['accreditation_cert', 'accreditation_cert_remarks'],
        ['service_rates', 'service_rates_remarks'],
    ], 'basic-information'),

    'service_categories', # Already added custom fieldset

    ("Tools and Equipment", [
        ['tools_equipment_complete', 'tools_equipment_serial_no'],
        ['racmac_sres_recovery_machine', 'racmac_serial_no'],
        ['proof_acquisition_recovery_machine'],
    ], 'tools-equipment'),

    ("Competence of Technicians", [
        ['employed_technicians_count', 'average_technician_experience', 'tesda_certification_nc', 'tesda_certification_coc'],
        ['continuous_training_program', 'list_employees_past_2_years'],
        ['refrigerant_storage_disposal_system'],
    ], 'competence-technicians'),

    ("Facilities", [
        ['office_work_area_sqm', 'working_stalls_count'],
        ['tool_equipment_storage_existing', 'tool_equipment_storage_adequate'],
        ['existing_record_keeping_system'],
        ['customers_reception_waiting_area_existing', 'customers_reception_waiting_area_adequate', 'customers_reception_waiting_area_suitable'],
        ['fire_extinguishers_count', ],
        ['available_personal_protective_equipment'],
        ['security_personnel_count', 'available_medical_kit'],
        ['inflammable_areas']
    ], 'facilities'),

    ("Insurance Coverage", [
        ['type_of_insurance_coverage'],
        ['insurance_expiry_date', 'insurance_coverage_amount'],
    ], 'insurance'),

    ("Customer Satisfaction & Complaints", [
        ['complaints_handling_process_exists', 'complaints_handling_process_documented'],
        ['customer_satisfaction_feedback_form_exists'],
    ], 'csf-complaints'),

    ("Findings and Remarks", [
        ['findings_remarks'],
    ], 'findings-remarks'),

    ("Recommendation", [
        ['recommendation', 'inspected_by_accreditation_officer', 'inspected_by_member'], 
    ], 'recommendation'),

    ("Certification", [
        ['authorized_signatory_name', 'authorized_signatory_date']
    ], 'certification')
]

ORDER_OF_PAYMENT_FIELD_GROUPS = [
    ("Name and Address", [
        ['name', 'address']
    ], 'name-and-address'),
    ('Permit Fee', [
        ['discount_amount', 'discount_remark'],
        ['premium_amount', 'premium_remark'],
        ['raffle_amount', 'raffle_remark'],
        ['contest_amount', 'contest_remark'],
        ['redemption_amount', 'redemption_remark'],
        ['games_amount', 'games_remark'],
        ['beauty_contest_amount', 'beauty_contest_remark'],
        ['home_solicitation_amount', 'home_solicitation_remark'],
        ['amendments_amount', 'amendments_remark'],
        ['doc_stamp_amount', 'doc_stamp_remark'],
    ], 'permit-fees'),
    ('Account/Special Collecting Officer', [
        ['account_officer_date', 'account_officer_signature'],
        ['special_collecting_officer_date', 'special_collecting_officer_or_number', 'special_collecting_officer_signature']
    ], 'account-special-collecting-officer')
]

CHECKLIST_EVALUATION_FIELD_GROUPS = [
    ("Business Details", [
        ['name_of_business', 'type_of_application', 'renewal_year', 'star_rating']
    ], 'business-details'),

    ("Requirements", [
        ['req_application_form', 'req_application_form_remark'],
        ['req_business_name_certificate', 'req_business_name_certificate_remark'],
        ['req_latest_accreditation_certificate', 'req_latest_accreditation_certificate_remark'],
        ['req_mechanics_list', 'req_mechanics_list_remark'],
        ['req_tesda_certificate', 'req_tesda_certificate_remark'],
        ['req_training_list', 'req_training_list_remark'],
        ['req_tools_equipment_list', 'req_tools_equipment_list_remark'],
        ['req_shop_layout_photos', 'req_shop_layout_photos_remark'],
        ['req_certification_no_changes', 'req_certification_no_changes_remark'],
        ['req_comprehensive_insurance', 'req_comprehensive_insurance_remark'],
        ['req_affidavit_on_site_repairs', 'req_affidavit_on_site_repairs_remark'],
        ['req_insurance_exemption_proof', 'req_insurance_exemption_proof_remark'],
        ['req_dealership_agreement', 'req_dealership_agreement_remark'],
        ['req_service_contract', 'req_service_contract_remark'],
        ['req_performance_bond', 'req_performance_bond_remark']
    ], 'requirements'),
]

# ---------- DETAIL VIEW GROUPS ---------------- #

SALES_PROMOTION_DETAIL_GROUPS = [
    ("Base Details", [
        ("User", "user"),
        ("Date Filed", "date_filed"),
        ("Promo Period Start", "promo_period_start"),
        ("Promo Period End", "promo_period_end"),
    ], "dates"),
    ("Sponsor Details", [
        ("Sponsor Name", "sponsor_name"),
        ("Sponsor Address", "sponsor_address"),
        ("Sponsor Telephone", "sponsor_telephone"),
        ("Sponsor Email", "sponsor_email"),
        ("Sponsor Authorized Rep", "sponsor_authorized_rep"),
        ("Sponsor Designation", "sponsor_designation"),
    ], "sponsors"),
    ("Advertising Details", [
        ("Advertising Agency Name", "advertising_agency_name"),
        ("Advertising Agency Address", "advertising_agency_address"),
        ("Advertising Agency Telephone", "advertising_agency_telephone"),
        ("Advertising Agency Email", "advertising_agency_email"),
        ("Advertising Agency Authorized Rep", "advertising_agency_authorized_rep"),
        ("Advertising Agency Designation", "advertising_agency_designation"),
    ], "advertising"),
]

PERSONAL_DATA_SHEET_DETAIL_GROUPS = [
    ("Personal Information", [
        ("Image", 'image'),
        ("First Name", "first_name"),
        ("Middle Name", "middle_name"),
        ("Last Name", "last_name"),
        ("Email Address", "email_address"),
        ("Position", "position"),
        ("Date of Birth", "date_of_birth"),
        ("Nationality", "nationality"),
        ("Sex", "sex"),
        ("Civil Status", "civil_status"),
        ("Current Address", "current_address"),
        ("Contact Number", "contact_number")
    ], "personal-info"),
]

SERVICE_REPAIR_ACCREDITATION_DETAIL_GROUPS = [
    ("Business Details", [
        ('Name of Business', 'name_of_business'),
        ('Application Type', 'application_type'),
        ('Category', 'category'),
        ('Star Rating', 'star_rating'),
    ]),
    ("Address", [
        ('Building Name or #', 'building_name_or_number'),
        ('Street Name', 'street_name'),
        ('Barangay', 'barangay'),
        ('City/Municipality', 'city_or_municipality'),
        ('Province', 'province'),
        ('Region', 'region'),
        ('ZIP Code', 'zip_code'),
    ]),
    ("Contact Information", [
        ('Telephone Number', 'telephone_number'),
        ('Mobile Number', 'mobile_number'),
        ('Fax Number', 'fax_number'),
        ('Email Address', 'email_address'),
    ]),
    ("Authorized Signatory", [
        ('Title', 'title'),
        ('First Name', 'first_name'),
        ('Middle Name', 'middle_name'),
        ('Last Name', 'last_name'),
        ('Suffix', 'suffix'),
        ('Designation', 'designation'),
    ]),
    ("Business Profile", [
        ('Sex', 'sex'),
        ('Social Classification', 'social_classification'),
        ('Asset Size', 'asset_size'),
        ('Form of Organization', 'form_of_organization'),
        ('Industry Classification', 'industry_classification'),
    ]),
    ("Financial & Operational Details", [
        ('Annual Gross Service Revenue', 'annual_gross_service_revenue'),
        ('Capital Investment', 'capital_investment'),
        ('Tax Identification Number', 'tax_identification_number'),
        ('Date Established', 'date_established'),
        ('Total Employees', 'total_employees'),
    ]),
]


INSPECTION_VALIDATION_DETAIL_GROUPS = [
    ("Basic Information", [
        ('Name of Business', 'name_of_business'),
        ('Address', 'address'),
        ('Date', 'date'),
        ('Type of Application/Activity', 'type_of_application_activity'),
        ('No. of Years in Service', 'years_in_service'),
        ('Type of Office/Shop', 'types_of_office_shop'),
        ('Business Name Certificates', 'business_name_certificates'),
        ('Accreditation Certificate', 'accreditation_cert'),
        ('Service Rates', 'service_rates')
    ]),
    ('Tools and Equipment', [
        ('Tools and equipment complete as listed in the submitted list of tools and equipment', 'tools_equipment_complete'),
        ('For RAC/MAC SREs, with Recovery Machine', 'racmac_sres_recovery_machine'),
        ('Serial No', 'racmac_serial_no'),
        ('Proof of Acquisition', 'proof_acquisition_recovery_machine')
    ]),
    ('Competence of Technicians', [
        ('No. of employed technicians', 'employed_technicians_count'),
        ('Average technician experience (in years)', 'average_technician_experience'),
        ('TESDA Certification NC', 'tesda_certification_nc'),
        ('TESDA Certification COC', 'tesda_certification_coc'),
        ('For RAC/MAC, with continuous training program for mechanics/technicians?', 'continuous_training_program'),
        ('Has submitted list or trainings of employees for the past 2 years?', 'list_employees_past_2_years'),
        ('For RAC/MAC, with refrigerant recovery storage and disposal system consistent with existing environmental laws and regulations', 'refrigerant_storage_disposal_system')
    ]),
    ('Facilities', [
        ('Size of shop/work area (sq. m.)', 'office_work_area_sqm'),
        ('No. of working stalls/bays', 'working_stalls_count'),
        ('Tool and equipment storage existing?', 'tool_equipment_storage_existing'),
        ('Adequate', 'tool_equipment_storage_adequate'),
        ('Existing Record keeping system', 'existing_record_keeping_system'),
        ('Customers reception and waiting area exists?', 'customers_reception_waiting_area_existing'),
        ('Adequate?', 'customers_reception_waiting_area_adequate'),
        ('Suitable?', 'customers_reception_waiting_area_suitable'),
        ('No. of applicable and unexpired fire extinguishers?', 'fire_extinguishers_count'),
        ('Available personal protective equipment', 'available_personal_protective_equipment'),
        ('Medical Kit', 'available_medical_kit'),
        ('No. of security Personnel', 'security_personnel_count'),
        ('Areas for inflammables such as gasoline, oil, paint, etc.', 'inflammable_areas')
    ]),
    ('Type of Insurance Coverage', [
        ('Type of Insurance Coverage', 'type_of_insurance_coverage'),
        ('Expiry Date', 'insurance_expiry_date'),
        ('Amount of Coverage (PHP)', 'insurance_coverage_amount')
    ]),
    ('Customer Satisfaction Feedback (CSF) and Complaint Handling', [
        ('With complaints handling process?', 'complaints_handling_process_exists'),
        ('Documented?', 'complaints_handling_process_documented'),
        ('With Customer Satisfaction Feedback (CSF) form?', 'customer_satisfaction_feedback_form_exists')
    ]),
    ('Findings/Remarks', [
        ('Findings/Remarks', 'findings_remarks'),
    ]),
    ('Recommendation', [
        ('Recommendation', 'recommendation'),
        ('Inspected by (Accreditation Officer/Leader)', 'inspected_by_accreditation_officer'),
        ('Inspected by (Member)', 'inspected_by_member'),
        ('Authorized Signatory Name', 'authorized_signatory_name'),
        ('Authorized Signatory Date', 'authorized_signatory_date')
    ])
]

ORDER_OF_PAYMENT_DETAIL_GROUPS = [
    ('Name and Business', [
        ('Name', 'name'),
        ('Date', 'date'),
        ('Address', 'address')
    ]),
    ('Account Officer', [
        ('Account Officer Date', 'account_officer_date'),
        ('Account Officer Signature', 'account_officer_signature'),
    ]),
    ('Special Collecting Officer', [
        ('Special Collecting Officer Date', 'special_collecting_officer_date'),
        ('Special Collecting Officer Number', 'special_collecting_officer_or_number'),
        ('Special Collecting Officer Signature', 'special_collecting_officer_signature')
    ])
]

CHECKLIST_EVALUATION_DETAIL_GROUPS = [
    ('Business Details', [
        ('Name of Buisiness', 'name_of_business'),
        ('Type of Application', 'type_of_application'),
        ('Star Rating', 'star_rating')
    ])
]

CHECKLIST_REQUIREMENT_GROUPS = [
    ('Requirements', [
        ('Application Form', 'req_application_form'),
        ('Application Form Remark', 'req_application_form_remark'),

        ('Business Name Certificate', 'req_business_name_certificate'),
        ('Business Name Certificate Remark', 'req_business_name_certificate_remark'),

        ('Latest Accreditation Certificate', 'req_latest_accreditation_certificate'),
        ('Latest Accreditation Certificate Remark', 'req_latest_accreditation_certificate_remark'),

        ('Mechanics List', 'req_mechanics_list'),
        ('Mechanics List Remark', 'req_mechanics_list_remark'),

        ('TESDA Certificate', 'req_tesda_certificate'),
        ('TESDA Certificate Remark', 'req_tesda_certificate_remark'),

        ('Training List', 'req_training_list'),
        ('Training List Remark', 'req_training_list_remark'),

        ('Tools and Equipment List', 'req_tools_equipment_list'),
        ('Tools and Equipment List Remark', 'req_tools_equipment_list_remark'),

        ('Shop Layout and Photos', 'req_shop_layout_photos'),
        ('Shop Layout and Photos Remark', 'req_shop_layout_photos_remark'),

        ('Certification of No Changes', 'req_certification_no_changes'),
        ('Certification of No Changes Remark', 'req_certification_no_changes_remark'),

        ('Comprehensive Insurance', 'req_comprehensive_insurance'),
        ('Comprehensive Insurance Remark', 'req_comprehensive_insurance_remark'),

        ('Affidavit on Site Repairs', 'req_affidavit_on_site_repairs'),
        ('Affidavit on Site Repairs Remark', 'req_affidavit_on_site_repairs_remark'),

        ('Insurance Exemption Proof', 'req_insurance_exemption_proof'),
        ('Insurance Exemption Proof Remark', 'req_insurance_exemption_proof_remark'),

        ('Dealership Agreement', 'req_dealership_agreement'),
        ('Dealership Agreement Remark', 'req_dealership_agreement_remark'),

        ('Service Contract', 'req_service_contract'),
        ('Service Contract Remark', 'req_service_contract_remark'),

        ('Performance Bond', 'req_performance_bond'),
        ('Performance Bond Remark', 'req_performance_bond_remark'),
    ])
]

PERSONAL_DATA_SHEET_TAB_SECTIONS = [
    {
        'id': 'employee-backgrounds',
        'title': 'Employee Backgrounds',
        'relation': 'employee_backgrounds',
        'icon': 'fas fa-briefcase',  
        'active': True,
    },
    {
        'id': 'trainings-attended',
        'title': 'Trainings Attended',
        'relation': 'trainings_attended',
        'icon': 'fas fa-chalkboard-teacher',  
        'active': False,
    },
    {
        'id': 'educational-attainment',
        'title': 'Educational Attainment',
        'relation': 'educational_attainment',
        'icon': 'fas fa-graduation-cap', 
        'active': False,
    },
    {
        'id': 'character-references',
        'title': 'Character References',
        'relation': 'character_references',
        'icon': 'fas fa-address-book',  
        'active': False,
    }
]

MODEL_URLS = {
    'SalesPromotionPermitApplication': 'sales-promotion-applications',
    'PersonalDataSheet': 'personal-data-sheets',
    'ServiceRepairAccreditationApplication': 'service-repair-accreditations',
    'InspectionValidationReport': 'inspection-validation-reports',
    'OrderOfPayment': 'order-of-payments',
    'ChecklistEvaluationSheet': 'checklist-evaluation-sheets',
}