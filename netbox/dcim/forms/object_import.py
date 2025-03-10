from django import forms

from dcim.choices import InterfaceTypeChoices, PortTypeChoices
from dcim.models import *
from utilities.forms import BootstrapMixin

__all__ = (
    'ConsolePortTemplateImportForm',
    'ConsoleServerPortTemplateImportForm',
    'DeviceBayTemplateImportForm',
    'DeviceTypeImportForm',
    'FrontPortTemplateImportForm',
    'InterfaceTemplateImportForm',
    'InventoryItemTemplateImportForm',
    'ModuleBayTemplateImportForm',
    'ModuleTypeImportForm',
    'PowerOutletTemplateImportForm',
    'PowerPortTemplateImportForm',
    'RearPortTemplateImportForm',
)


class DeviceTypeImportForm(BootstrapMixin, forms.ModelForm):
    manufacturer = forms.ModelChoiceField(
        label='Производитель',
        queryset=Manufacturer.objects.all(),
        to_field_name='name'
    )

    class Meta:
        model = DeviceType
        fields = [
            'manufacturer', 'model', 'slug', 'part_number', 'u_height', 'is_full_depth', 'subdevice_role', 'airflow',
            'comments',
        ]


class ModuleTypeImportForm(BootstrapMixin, forms.ModelForm):
    manufacturer = forms.ModelChoiceField(
        label='Производитель',
        queryset=Manufacturer.objects.all(),
        to_field_name='name'
    )

    class Meta:
        model = ModuleType
        fields = ['manufacturer', 'model', 'part_number', 'comments']


#
# Component template import forms
#

class ComponentTemplateImportForm(BootstrapMixin, forms.ModelForm):
    pass


class ConsolePortTemplateImportForm(ComponentTemplateImportForm):

    class Meta:
        model = ConsolePortTemplate
        fields = [
            'device_type', 'module_type', 'name', 'label', 'type', 'description',
        ]


class ConsoleServerPortTemplateImportForm(ComponentTemplateImportForm):

    class Meta:
        model = ConsoleServerPortTemplate
        fields = [
            'device_type', 'module_type', 'name', 'label', 'type', 'description',
        ]


class PowerPortTemplateImportForm(ComponentTemplateImportForm):

    class Meta:
        model = PowerPortTemplate
        fields = [
            'device_type', 'module_type', 'name', 'label', 'type', 'maximum_draw', 'allocated_draw', 'description',
        ]


class PowerOutletTemplateImportForm(ComponentTemplateImportForm):
    power_port = forms.ModelChoiceField(
        label='Силовой порт',
        queryset=PowerPortTemplate.objects.all(),
        to_field_name='name',
        required=False
    )

    class Meta:
        model = PowerOutletTemplate
        fields = [
            'device_type', 'module_type', 'name', 'label', 'type', 'power_port', 'feed_leg', 'description',
        ]

    def clean_device_type(self):
        if device_type := self.cleaned_data['device_type']:
            power_port = self.fields['power_port']
            power_port.queryset = power_port.queryset.filter(device_type=device_type)

        return device_type

    def clean_module_type(self):
        if module_type := self.cleaned_data['module_type']:
            power_port = self.fields['power_port']
            power_port.queryset = power_port.queryset.filter(module_type=module_type)

        return module_type


class InterfaceTemplateImportForm(ComponentTemplateImportForm):
    type = forms.ChoiceField(
        label='Тип',
        choices=InterfaceTypeChoices.CHOICES
    )

    class Meta:
        model = InterfaceTemplate
        fields = [
            'device_type', 'module_type', 'name', 'label', 'type', 'mgmt_only', 'description',
        ]


class FrontPortTemplateImportForm(ComponentTemplateImportForm):
    type = forms.ChoiceField(
        label='Тип',
        choices=PortTypeChoices.CHOICES
    )
    rear_port = forms.ModelChoiceField(
        label='Задний порт',
        queryset=RearPortTemplate.objects.all(),
        to_field_name='name'
    )

    def clean_device_type(self):
        if device_type := self.cleaned_data['device_type']:
            rear_port = self.fields['rear_port']
            rear_port.queryset = rear_port.queryset.filter(device_type=device_type)

        return device_type

    def clean_module_type(self):
        if module_type := self.cleaned_data['module_type']:
            rear_port = self.fields['rear_port']
            rear_port.queryset = rear_port.queryset.filter(module_type=module_type)

        return module_type

    class Meta:
        model = FrontPortTemplate
        fields = [
            'device_type', 'module_type', 'name', 'type', 'rear_port', 'rear_port_position', 'label', 'description',
        ]


class RearPortTemplateImportForm(ComponentTemplateImportForm):
    type = forms.ChoiceField(
        label='Тип',
        choices=PortTypeChoices.CHOICES
    )

    class Meta:
        model = RearPortTemplate
        fields = [
            'device_type', 'module_type', 'name', 'type', 'positions', 'label', 'description',
        ]


class ModuleBayTemplateImportForm(ComponentTemplateImportForm):

    class Meta:
        model = ModuleBayTemplate
        fields = [
            'device_type', 'name', 'label', 'position', 'description',
        ]


class DeviceBayTemplateImportForm(ComponentTemplateImportForm):

    class Meta:
        model = DeviceBayTemplate
        fields = [
            'device_type', 'name', 'label', 'description',
        ]


class InventoryItemTemplateImportForm(ComponentTemplateImportForm):
    parent = forms.ModelChoiceField(
        queryset=InventoryItemTemplate.objects.all(),
        required=False
    )
    role = forms.ModelChoiceField(
        label='Роль',
        queryset=InventoryItemRole.objects.all(),
        to_field_name='name',
        required=False
    )
    manufacturer = forms.ModelChoiceField(
        label='Производитель',
        queryset=Manufacturer.objects.all(),
        to_field_name='name',
        required=False
    )

    class Meta:
        model = InventoryItemTemplate
        fields = [
            'device_type', 'parent', 'name', 'label', 'role', 'manufacturer', 'part_id', 'description',
        ]

    def clean_device_type(self):
        if device_type := self.cleaned_data['device_type']:
            parent = self.fields['parent']
            parent.queryset = parent.queryset.filter(device_type=device_type)

        return device_type

    def clean_module_type(self):
        if module_type := self.cleaned_data['module_type']:
            parent = self.fields['parent']
            parent.queryset = parent.queryset.filter(module_type=module_type)

        return module_type
