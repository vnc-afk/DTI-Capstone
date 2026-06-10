from datetime import date
import re
from django import forms
from locations.models import Barangay, CityMunicipality, Province, Region
from .utils.form_helpers import create_inline_formset
from .validators import validate_period
from .models import OtherBusinessNameRelatedFormModel, CharacterReference, ChecklistEvaluationSheet, EducationalAttainment, EmployeeBackground, InspectionValidationReport, OrderOfPayment, ProductCovered, SalesPromotionPermitApplication, PersonalDataSheet, Service, ServiceCategory, ServiceRepairAccreditationApplication, TrainingsAttended
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, LayoutObject, TEMPLATE_PACK, Fieldset, HTML, Div, Row, Column, Submit
from django.template.loader import render_to_string
from django.forms.widgets import SelectMultiple

class SortForm(forms.Form):
    SORT_CHOICES = [
        ('name_asc', 'Name (A-Z)'),
        ('name_desc', 'Name (Z-A)')
    ]

    sort_by = forms.ChoiceField(choices=SORT_CHOICES, required=False, label='sort_by')

class BaseCustomForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        if hasattr(self, 'fields'):
            for name, field in self.fields.items():
                label_text = field.label if field.label else name.replace('_', ' ').title()
                if field.required:
                    field.label = f"{label_text} <span class='required-label'>*</span>"
                    field.widget.attrs['placeholder'] = f"Enter {label_text}"
                else:
                    field.label = label_text

                # --- Date fields ---
                if isinstance(field, forms.DateField):
                    field.widget = forms.DateInput(attrs={'type': 'date'})

                # --- Textareas ---
                if isinstance(field.widget, forms.Textarea):
                    field.widget.attrs['rows'] = 4

                # --- Common class ---
                existing_classes = field.widget.attrs.get('class', '')
                field.widget.attrs['class'] = f"{existing_classes} form-group".strip()

                # --- Numeric-only fields ---
                numerical_fields = [
                    'sponsor_telephone',
                    'advertising_agency_telephone',
                    'tax_identification_number',
                    'contact_number',
                    'mobile_number',
                    'fax_number',
                    'telephone_number',
                    'zip_code',
                    'certificate_number',
                ]

                future_only_dates = ['promo_period_end']

                if name in numerical_fields:
                    field.widget.attrs.update({
                        'inputmode': 'numeric',
                        'pattern': r'\d*',
                        'oninput': "this.value=this.value.replace(/[^0-9]/g,'')",
                    })

                if name in ['contact_number', 'mobile_number']:
                    field.validators.append(self.validate_contact_number)
                    field.widget.attrs['maxlength'] = 11
                    field.widget.attrs['placeholder'] = 'Enter Mobile Number (11 digits)'

                # --- Date of Birth / Birthday (must be 18+) ---
                if name in ['date_of_birth', 'birthday']:
                    field.validators.append(self.validate_minimum_age_18)
                    eighteen_years_ago = date.today().replace(year=date.today().year - 18)
                    field.widget.attrs.update({
                        'type': 'date',
                        'max': eighteen_years_ago.isoformat(),
                        'value': eighteen_years_ago.isoformat(),
                        'placeholder': 'Select Date of Birth (Must be 18+)',
                        # Immediate browser feedback
                        'oninput': """
                            const today = new Date();
                            const cutoff = new Date(today.getFullYear() - 18, today.getMonth(), today.getDate());
                            const inputDate = new Date(this.value);
                            if (inputDate > cutoff) {
                                this.setCustomValidity('You must be at least 18 years old.');
                            } else {
                                this.setCustomValidity('');
                            }
                        """,
                    })


                if name == 'date_established':
                    field.validators.append(self.generate_date_not_in_future_validator("Date Established"))
                    field.widget.attrs['max'] = date.today().isoformat()
                    field.widget.attrs['placeholder'] = 'Enter Date Established'

                if name == 'date_registered':
                    field.validators.append(self.generate_date_not_in_future_validator("Date Registered"))
                    field.widget.attrs['max'] = date.today().isoformat()
                    field.widget.attrs['placeholder'] = 'Enter Date Registered'

                if name == 'telephone_number' or name == 'sponsor_telephone' or name == 'advertising_agency_telephone':
                    field.validators.append(self.validate_telephone_number)
                    field.widget.attrs['maxlength'] = 10
                    field.widget.attrs['placeholder'] = 'Enter Telephone Number (10 digits)'

                if name == 'zip_code':
                    field.validators.append(self.validate_zip_code)
                    field.widget.attrs['maxlength'] = 4
                    field.widget.attrs['placeholder'] = 'Enter Zip Code (4 digits)'

                if name == 'tax_identification_number':
                    field.validators.append(self.validate_tax_identification_number)
                    field.widget.attrs['maxlength'] = 12
                    field.widget.attrs['placeholder'] = 'Enter Tax Identification Number (9 to 12 digits)'

                if name in future_only_dates:
                    field.validators.append(self.generate_date_not_in_past_validator('Promo Period End'))
                    field.widget.attrs['min'] = date.today().isoformat()

                if name in ['email', 'email_address']:
                    field.validators.append(self.validate_strict_email)
                    field.widget.attrs['placeholder'] = 'Enter a valid email address'

                # --- Letter-only fields ---
                letter_only_fields = [
                    'first_name',
                    'middle_name',
                    'last_name',
                    'full_name',
                    'nationality',
                ]
                if name in letter_only_fields:
                    field.widget.attrs.update({
                        'pattern': r"[A-Za-zÀ-ÖØ-öø-ÿ' -]+",
                        'title': "Letters, spaces, hyphens, and apostrophes only",
                        'oninput': "this.value=this.value.replace(/[^A-Za-zÀ-ÖØ-öø-ÿ' -]/g,'')",
                    })

        # --- Auto-fill user fields ---
        if user:
            profile = getattr(user, 'profile', None)
            user_field_map = {
                'full_name': 'get_full_name',
                'first_name': 'first_name',
                'last_name': 'last_name',
                'email': 'email',
                'email_address': 'email',
                'mobile_number': 'default_phone',
                'contact_number': 'default_phone',
                'current_address': 'default_address',
                'address': 'default_address',
            }
            for field_name, attr_name in user_field_map.items():
                if field_name in self.fields and not self.initial.get(field_name):
                    value = ''
                    if profile and hasattr(profile, attr_name):
                        value = getattr(profile, attr_name, '')
                    elif hasattr(user, attr_name):
                        value = getattr(user, attr_name, '')
                    self.fields[field_name].initial = value

    def clean(self):
        cleaned_data = super().clean()
        
        return cleaned_data

    # --- Validation methods ---
    def validate_contact_number(self, value):
        value = str(value)

        # Must be exactly 11 digits
        if not re.fullmatch(r'\d{11}', value):
            raise forms.ValidationError("Contact/Mobile number must be exactly 11 digits.")

        # Reject all same digits (e.g., 11111111111)
        if value == value[0] * 11:
            raise forms.ValidationError("This is not a valid mobile number.")

        # Reject simple repeating sequences like 12312312312
        pattern = value[:3]
        if pattern * 3 + value[-2:] == value:
            raise forms.ValidationError("This is not a valid mobile number.")


    def validate_telephone_number(self, value):
        if not re.fullmatch(r'\d{10}', str(value)):
            raise forms.ValidationError("Telephone number must be exactly 10 digits.")

    def validate_zip_code(self, value):
        if not re.fullmatch(r'\d{4}', str(value)):
            raise forms.ValidationError("Zip code must be exactly 4 digits.")

    def validate_tax_identification_number(self, value):
        if not re.fullmatch(r'\d{9,12}', str(value)):
            raise forms.ValidationError("Tax Identification Number must be between 9 to 12 digits.")

    def validate_minimum_age_18(self, value):
        today = date.today()
        eighteen_years_ago = today.replace(year=today.year - 18)
        if value > eighteen_years_ago:
            raise forms.ValidationError("You must be at least 18 years old.")

    def generate_date_not_in_future_validator(self, field_label):
        def validator(value):
            if value > date.today():
                raise forms.ValidationError(f'{field_label} cannot be in the future.')
        return validator

    def generate_date_not_in_past_validator(self, field_label):
        def validator(value):
            if value < date.today():
                raise forms.ValidationError(f'{field_label} cannot be in the past.')
        return validator

    def validate_strict_email(self, value):
        pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.(com|net|org|gov|edu|ph|io|co\.uk)$"
        if not re.fullmatch(pattern, value):
            raise forms.ValidationError("Enter a valid email address.")


class SalesPromotionPermitApplicationForm(BaseCustomForm):
    class Meta:
        model = SalesPromotionPermitApplication
        fields = '__all__'
        exclude = ['status', 'date_filed', 'user']
        widgets = {
            'promo_period_start': forms.DateInput(attrs={'type': 'date', 'class': 'form-group'}),
            'promo_period_end': forms.DateInput(attrs={'type': 'date', 'class': 'form-group'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        promo_start_date = cleaned_data.get('promo_period_start')  # Fixed field name
        promo_end_date = cleaned_data.get('promo_period_end')      # Fixed field name

        # Call your dynamic validator
        if promo_start_date and promo_end_date:
            validate_period(promo_start_date, promo_end_date, 'Promo start date', 'Promo end date')

        return cleaned_data

class ProductCoveredForm(BaseCustomForm):
    class Meta:
        model = ProductCovered
        fields = ['name', 'brand', 'specifications']

class PersonalDataSheetForm(BaseCustomForm):
    class Meta:
        model = PersonalDataSheet
        fields = '__all__'
        exclude = ['status', 'user', 'date']
        widgets = {
            'current_address': forms.TextInput(attrs={'class': 'form-group'}),
            'date_of_birth': forms.DateInput(attrs={'type': 'date', 'class': 'form-group'}),
            'image': forms.FileInput(attrs={
                'class': 'hidden-file-input',
                'accept': 'image/*',
                'id': 'id_image'
            })
        }

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            # Hide the "Currently" label for image field
            self.fields['image'].widget.attrs.update({
                'style': 'display: none;'
            })
            # Remove help text that shows "Currently: filename"
            self.fields['image'].widget.clear_checkbox_label = ''
            self.fields['image'].widget.initial_text = ''
            self.fields['image'].widget.input_text = ''
            
class OtherBusinessNameRelatedForm(BaseCustomForm):
    class Meta:
        model = OtherBusinessNameRelatedFormModel
        fields = '__all__'
        exclude = ['status', 'user']

    def clean(self):
        cleaned_data = super().clean()

        # Sections
        bn_cert_purpose = cleaned_data.get('bn_certification_purpose')
        authentication = cleaned_data.get('no_of_copies')
        cancellation = cleaned_data.get('cancellation_reason')

        # Change of Info sections - CHECK THE ACTUAL FIELDS, NOT THE CHECKBOXES
        change_filled = False
        
        # Check territorial scope
        if cleaned_data.get('territorial_scope_from') or cleaned_data.get('territorial_scope_to'):
            change_filled = True
            
        # Check owner name
        if cleaned_data.get('owner_name_from') or cleaned_data.get('owner_name_to') or cleaned_data.get('owner_name_proof_basis'):
            change_filled = True
            
        # Check business address
        if cleaned_data.get('business_address_from') or cleaned_data.get('business_address_to'):
            change_filled = True
            
        # Check owner address
        if cleaned_data.get('owner_address_from') or cleaned_data.get('owner_address_to'):
            change_filled = True

        # 1️⃣ Require at least one section
        if not any([bn_cert_purpose, authentication, change_filled, cancellation]):
            raise forms.ValidationError("You must fill at least one section: BN Certification, Authentication, Change of Info, or Cancellation.")

        # 2️⃣ Cannot fill change-of-info if cancellation is filled
        if cancellation and change_filled:
            raise forms.ValidationError("You cannot fill any Change of Info fields if Cancellation is provided.")

        # Define the "from/to" field pairs with their checkbox
        from_to_pairs = [
            ('change_territorial_scope', 'territorial_scope_from', 'territorial_scope_to', 'Territorial Scope'),
            ('change_owner_name', 'owner_name_from', 'owner_name_to', "Owner's Name"),
            ('change_business_address', 'business_address_from', 'business_address_to', 'Business Address'),
            ('change_owner_address', 'owner_address_from', 'owner_address_to', "Owner's Address"),
        ]
        
        for checkbox_field, from_field, to_field, label in from_to_pairs:
            # Only validate if these fields exist in the form
            if from_field not in self.fields or to_field not in self.fields:
                continue
                
            from_value = cleaned_data.get(from_field)
            to_value = cleaned_data.get(to_field)
            
            # Convert None to empty string for consistent checking
            from_value = from_value if from_value is not None else ''
            to_value = to_value if to_value is not None else ''
            
            # Strip whitespace
            from_str = str(from_value).strip() if from_value else ''
            to_str = str(to_value).strip() if to_value else ''
            
            # If either field is filled, both must be filled
            if from_str or to_str:
                # Automatically set the checkbox to True
                cleaned_data[checkbox_field] = True
                
                # Validate both fields are filled
                if from_str and not to_str:
                    self.add_error(to_field, f'Both "From" and "To" fields for {label} must be filled.')
                elif to_str and not from_str:
                    self.add_error(from_field, f'Both "From" and "To" fields for {label} must be filled.')
                
                # Check if both are filled and are the same
                elif from_str and to_str:
                    if from_str.lower() == to_str.lower():
                        self.add_error(to_field, f'The "From" and "To" values for {label} cannot be the same.')
            else:
                # If both fields are empty, ensure checkbox is False
                cleaned_data[checkbox_field] = False

        return cleaned_data

class EmployeeBackgroundForm(BaseCustomForm):
    class Meta:
        model = EmployeeBackground
        fields = '__all__'
        exclude = ['personal_data_sheet']

class TrainingsAttendedForm(BaseCustomForm):
    class Meta:
        model = TrainingsAttended
        fields = '__all__'
        exclude = ['personal_data_sheet']

class EducationalAttainmentForm(BaseCustomForm):
    class Meta:
        model = EducationalAttainment
        fields = '__all__'
        exclude = ['personal_data_sheet']     

class CharacterReferenceForm(BaseCustomForm):
    class Meta:
        model = CharacterReference
        fields = '__all__'
        exclude = ['personal_data_sheet']     

class ServiceRepairAccreditationApplicationForm(BaseCustomForm):
    region = forms.ModelChoiceField(queryset=Region.objects.none(), required=False)
    province = forms.ModelChoiceField(queryset=Province.objects.none(), required=False)
    city_or_municipality = forms.ModelChoiceField(queryset=CityMunicipality.objects.none(), required=False)
    barangay = forms.ModelChoiceField(queryset=Barangay.objects.none(), required=False)

    class Meta:
        model = ServiceRepairAccreditationApplication
        fields = '__all__'
        exclude = ['status', 'user', 'date', 'payment_status', 'total_amount']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # --- REGION ---
        region_id = self.data.get('region') or (self.instance.region.id if self.instance.pk and self.instance.region else None)
        if region_id:
            self.fields['region'].queryset = Region.objects.filter(id=region_id)
        else:
            self.fields['region'].queryset = Region.objects.none()

        # --- PROVINCE ---
        province_id = self.data.get('province') or (self.instance.province.id if self.instance.pk and self.instance.province else None)
        if province_id:
            self.fields['province'].queryset = Province.objects.filter(id=province_id)
        elif region_id:
            self.fields['province'].queryset = Province.objects.filter(region_id=region_id)
        else:
            self.fields['province'].queryset = Province.objects.none()

        # --- CITY / MUNICIPALITY ---
        city_id = self.data.get('city_or_municipality') or (self.instance.city_or_municipality.id if self.instance.pk and self.instance.city_or_municipality else None)
        if city_id:
            self.fields['city_or_municipality'].queryset = CityMunicipality.objects.filter(id=city_id)
        elif province_id:
            self.fields['city_or_municipality'].queryset = CityMunicipality.objects.filter(province_id=province_id)
        else:
            self.fields['city_or_municipality'].queryset = CityMunicipality.objects.none()

        # --- BARANGAY ---
        barangay_id = self.data.get('barangay') or (self.instance.barangay.id if self.instance.pk and self.instance.barangay else None)
        if barangay_id:
            self.fields['barangay'].queryset = Barangay.objects.filter(id=barangay_id)
        elif city_id:
            self.fields['barangay'].queryset = Barangay.objects.filter(city_id=city_id)
        else:
            self.fields['barangay'].queryset = Barangay.objects.none()

class InspectionValidationReportForm(BaseCustomForm):
    class Meta:
        model = InspectionValidationReport
        fields = '__all__'
        exclude = ['status', 'date', 'user']
        widgets = {
            'services_offered': forms.CheckboxSelectMultiple()
        }

class ServiceCategoryForm(BaseCustomForm):
    class Meta:
        model = ServiceCategory
        fields = '__all__'

class ServiceForm(BaseCustomForm):
    class Meta:
        model = Service
        fields = '__all__'

class OrderOfPaymentForm(BaseCustomForm):
    class Meta:
        model = OrderOfPayment
        fields = '__all__'
        exclude = ['status', 'date', 'user','payment_status', 'total_amount']
        widgets = {
            'sales_promotion_permit_application': forms.HiddenInput(),
        }


class ChecklistEvaluationSheetForm(BaseCustomForm):
    renewal_year = forms.IntegerField(label="Date Expired: Dec 31, ____", min_value=1900)

    class Meta:
        model = ChecklistEvaluationSheet
        fields = '__all__'
        exclude = ['status', 'user', 'date']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        current_year = date.today().year
        self.fields['renewal_year'].max_value = current_year
        self.fields['renewal_year'].initial = current_year - 1

    def clean(self):
        cleaned_data = super().clean()
        year = cleaned_data.get('renewal_year')
        if year:
            cleaned_data['renewal_due_date'] = date(year, 12, 31)
        return cleaned_data

# Formset configurations
FORMSET_CONFIGS = {
    # Sales Application Formsets
    'product_covered': {
        'parent_model': SalesPromotionPermitApplication,
        'child_model': ProductCovered,
        'form_class': ProductCoveredForm,
        'fields': ['name', 'brand', 'specifications'],
    },

    # Personal Data Sheet Formsets
    'employee_background': {
        'parent_model': PersonalDataSheet,  
        'child_model': EmployeeBackground,
        'form_class': EmployeeBackgroundForm,
    },
    'trainings_attended': {
        'parent_model': PersonalDataSheet,
        'child_model': TrainingsAttended,
        'form_class': TrainingsAttendedForm
    },
    'educational_attainment': {
        'parent_model': PersonalDataSheet,
        'child_model': EducationalAttainment,
        'form_class': EducationalAttainmentForm
    },
    'character_references': {
        'parent_model': PersonalDataSheet,
        'child_model': CharacterReference,
        'form_class': CharacterReferenceForm
    },
}

FORMSET_CLASSES = {}

for key, config in FORMSET_CONFIGS.items():
    FORMSET_CLASSES[key] = create_inline_formset(**config)
