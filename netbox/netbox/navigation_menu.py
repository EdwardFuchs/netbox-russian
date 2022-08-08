from dataclasses import dataclass
from typing import Sequence, Optional

from extras.registry import registry
from utilities.choices import ButtonColorChoices


#
# Nav menu data classes
#

@dataclass
class MenuItemButton:

    link: str
    title: str
    icon_class: str
    permissions: Optional[Sequence[str]] = ()
    color: Optional[str] = None


@dataclass
class MenuItem:

    link: str
    link_text: str
    permissions: Optional[Sequence[str]] = ()
    buttons: Optional[Sequence[MenuItemButton]] = ()


@dataclass
class MenuGroup:

    label: str
    items: Sequence[MenuItem]


@dataclass
class Menu:

    label: str
    icon_class: str
    groups: Sequence[MenuGroup]


#
# Utility functions
#

def get_model_item(app_label, model_name, label, actions=('add', 'import')):
    return MenuItem(
        link=f'{app_label}:{model_name}_list',
        link_text=label,
        permissions=[f'{app_label}.view_{model_name}'],
        buttons=get_model_buttons(app_label, model_name, actions)
    )


def get_model_buttons(app_label, model_name, actions=('add', 'import')):
    buttons = []

    if 'add' in actions:
        buttons.append(
            MenuItemButton(
                link=f'{app_label}:{model_name}_add',
                title='Add',
                icon_class='mdi mdi-plus-thick',
                permissions=[f'{app_label}.add_{model_name}'],
                color=ButtonColorChoices.GREEN
            )
        )
    if 'import' in actions:
        buttons.append(
            MenuItemButton(
                link=f'{app_label}:{model_name}_import',
                title='Import',
                icon_class='mdi mdi-upload',
                permissions=[f'{app_label}.add_{model_name}'],
                color=ButtonColorChoices.CYAN
            )
        )

    return buttons


#
# Nav menus
#

ORGANIZATION_MENU = Menu(
    label='Структура',
    icon_class='mdi mdi-domain',
    groups=(
        MenuGroup(
            label='Адреса',
            items=(
                get_model_item('dcim', 'site', 'Адреса'),
                get_model_item('dcim', 'region', 'Регионы'),
                get_model_item('dcim', 'sitegroup', 'Группы адресов'),
                get_model_item('dcim', 'location', 'Метоположения'),
            ),
        ),
        MenuGroup(
            label='Стойки',
            items=(
                get_model_item('dcim', 'rack', 'Стойки'),
                get_model_item('dcim', 'rackrole', 'Роли стоек'),
                get_model_item('dcim', 'rackreservation', 'Резервирования'),
                MenuItem(
                    link='dcim:rack_elevation_list',
                    link_text='Загруженность',
                    permissions=['dcim.view_rack']
                ),
            ),
        ),
        MenuGroup(
            label='Учреждения',
            items=(
                get_model_item('tenancy', 'tenant', 'Учреждения'),
                get_model_item('tenancy', 'tenantgroup', 'Группы учреждений'),
            ),
        ),
        MenuGroup(
            label='Контакты',
            items=(
                get_model_item('tenancy', 'contact', 'Контакты'),
                get_model_item('tenancy', 'contactgroup', 'Группы контактов'),
                get_model_item('tenancy', 'contactrole', 'Роли контактов'),
            ),
        ),
    ),
)

DEVICES_MENU = Menu(
    label='Устройства',
    icon_class='mdi mdi-server',
    groups=(
        MenuGroup(
            label='Устройства',
            items=(
                get_model_item('dcim', 'device', 'Устройства'),
                get_model_item('dcim', 'module', 'Модули'),
                get_model_item('dcim', 'devicerole', 'Роли устройств'),
                get_model_item('dcim', 'platform', 'Платформы'),
                get_model_item('dcim', 'virtualchassis', 'Виртуальные шасси'),
            ),
        ),
        MenuGroup(
            label='Типы устройств',
            items=(
                get_model_item('dcim', 'devicetype', 'Типы устройств'),
                get_model_item('dcim', 'moduletype', 'Типы модуля'),
                get_model_item('dcim', 'manufacturer', 'Производители'),
            ),
        ),
        MenuGroup(
            label='Компоненты устройства',
            items=(
                get_model_item('dcim', 'interface', 'Интерфейсы', actions=['import']),
                get_model_item('dcim', 'frontport', 'Передние порты', actions=['import']),
                get_model_item('dcim', 'rearport', 'Задние порты', actions=['import']),
                get_model_item('dcim', 'consoleport', 'Консольные порты', actions=['import']),
                get_model_item('dcim', 'consoleserverport', 'Серверные порты', actions=['import']),
                get_model_item('dcim', 'powerport', 'Порты питания', actions=['import']),
                get_model_item('dcim', 'poweroutlet', 'Питание', actions=['import']),
                get_model_item('dcim', 'modulebay', 'Модульные отсеки', actions=['import']),
                get_model_item('dcim', 'devicebay', 'Отсеки', actions=['import']),
                get_model_item('dcim', 'inventoryitem', 'Встроенные устройства', actions=['import']),
                get_model_item('dcim', 'inventoryitemrole', 'Роли компонентов'),
            ),
        ),
    ),
)

CONNECTIONS_MENU = Menu(
    label='Подключения',
    icon_class='mdi mdi-ethernet',
    groups=(
        MenuGroup(
            label='Подключения',
            items=(
                get_model_item('dcim', 'cable', 'Кабели', actions=['import']),
                get_model_item('wireless', 'wirelesslink', 'Беспроводные', actions=['import']),
                MenuItem(
                    link='dcim:interface_connections_list',
                    link_text='Интерфейсы',
                    permissions=['dcim.view_interface']
                ),
                MenuItem(
                    link='dcim:console_connections_list',
                    link_text='Консольные соединения',
                    permissions=['dcim.view_consoleport']
                ),
                MenuItem(
                    link='dcim:power_connections_list',
                    link_text='Силовые соединения',
                    permissions=['dcim.view_powerport']
                ),
            ),
        ),
    ),
)

WIRELESS_MENU = Menu(
    label='Wi-Fi',
    icon_class='mdi mdi-wifi',
    groups=(
        MenuGroup(
            label='Wi-Fi',
            items=(
                get_model_item('wireless', 'wirelesslan', 'Wi-fi сети'),
                get_model_item('wireless', 'wirelesslangroup', 'Группы wi-fi'),
            ),
        ),
    ),
)

IPAM_MENU = Menu(
    label='Сеть',
    icon_class='mdi mdi-counter',
    groups=(
        MenuGroup(
            label='IP адреса',
            items=(
                get_model_item('ipam', 'ipaddress', 'IP адреса'),
                get_model_item('ipam', 'iprange', 'IP диапазоны'),
            ),
        ),
        MenuGroup(
            label='Подсети',
            items=(
                get_model_item('ipam', 'prefix', 'Подсети'),
                get_model_item('ipam', 'role', 'Роли подсетей'),
            ),
        ),
        MenuGroup(
            label='ASNы',
            items=(
                get_model_item('ipam', 'asn', 'ASNы'),
            ),
        ),
        MenuGroup(
            label='Сети',
            items=(
                get_model_item('ipam', 'aggregate', 'Сети'),
                get_model_item('ipam', 'rir', 'RIR'),
            ),
        ),
        MenuGroup(
            label='VRF',
            items=(
                get_model_item('ipam', 'vrf', 'VRF'),
                get_model_item('ipam', 'routetarget', 'Цели маршрута'),
            ),
        ),
        MenuGroup(
            label='VLANы',
            items=(
                get_model_item('ipam', 'vlan', 'VLANы'),
                get_model_item('ipam', 'vlangroup', 'Группы VLANов'),
            ),
        ),
        MenuGroup(
            label='Прочее',
            items=(
                get_model_item('ipam', 'fhrpgroup', 'Группы FHRP'),
                get_model_item('ipam', 'servicetemplate', 'Шаблоны'),
                get_model_item('ipam', 'service', 'Сервисы'),
            ),
        ),
    ),
)

VIRTUALIZATION_MENU = Menu(
    label='Виртуализация',
    icon_class='mdi mdi-monitor',
    groups=(
        MenuGroup(
            label='Виртуальные машины',
            items=(
                get_model_item('virtualization', 'virtualmachine', 'Виртуальные машины'),
                get_model_item('virtualization', 'vminterface', 'Интерфейсы', actions=['import']),
            ),
        ),
        MenuGroup(
            label='Кластеры',
            items=(
                get_model_item('virtualization', 'cluster', 'Кластеры'),
                get_model_item('virtualization', 'clustertype', 'Типы кластеров'),
                get_model_item('virtualization', 'clustergroup', 'Группы кластеров'),
            ),
        ),
    ),
)

CIRCUITS_MENU = Menu(
    label='Каналы',
    icon_class='mdi mdi-transit-connection-variant',
    groups=(
        MenuGroup(
            label='Каналы',
            items=(
                get_model_item('circuits', 'circuit', 'Каналы'),
                get_model_item('circuits', 'circuittype', 'Типы цепи'),
            ),
        ),
        MenuGroup(
            label='Поставщики услуг',
            items=(
                get_model_item('circuits', 'provider', 'Поставщики услуг'),
                get_model_item('circuits', 'providernetwork', 'Сети провайдеров'),
            ),
        ),
    ),
)

POWER_MENU = Menu(
    label='Электропитание',
    icon_class='mdi mdi-flash',
    groups=(
        MenuGroup(
            label='Электропитание',
            items=(
                get_model_item('dcim', 'powerfeed', 'Подача питания'),
                get_model_item('dcim', 'powerpanel', 'Силовая панели'),
            ),
        ),
    ),
)

OTHER_MENU = Menu(
    label='Прочее',
    icon_class='mdi mdi-notification-clear-all',
    groups=(
        MenuGroup(
            label='Журнал',
            items=(
                get_model_item('extras', 'journalentry', 'Записи в журнале', actions=[]),
                get_model_item('extras', 'objectchange', 'Изменение журнала', actions=[]),
            ),
        ),
        MenuGroup(
            label='Настройки',
            items=(
                get_model_item('extras', 'customfield', 'Настраиваемые поля'),
                get_model_item('extras', 'customlink', 'Настраиваемые ссылки'),
                get_model_item('extras', 'exporttemplate', 'Экспорт шаблонов'),
            ),
        ),
        MenuGroup(
            label='Интеграции',
            items=(
                get_model_item('extras', 'webhook', 'Вебхуки'),
                MenuItem(
                    link='extras:report_list',
                    link_text='Отчеты',
                    permissions=['extras.view_report']
                ),
                MenuItem(
                    link='extras:script_list',
                    link_text='Скрипты',
                    permissions=['extras.view_script']
                ),
            ),
        ),
        MenuGroup(
            label='Прочее',
            items=(
                get_model_item('extras', 'tag', 'Теги'),
                get_model_item('extras', 'configcontext', 'Конфигурации', actions=['add']),
            ),
        ),
    ),
)


MENUS = [
    ORGANIZATION_MENU,
    DEVICES_MENU,
    CONNECTIONS_MENU,
    WIRELESS_MENU,
    IPAM_MENU,
    VIRTUALIZATION_MENU,
    CIRCUITS_MENU,
    POWER_MENU,
    OTHER_MENU,
]

#
# Add plugin menus
#

if registry['plugins']['menu_items']:
    plugin_menu_groups = []

    for plugin_name, items in registry['plugins']['menu_items'].items():
        plugin_menu_groups.append(
            MenuGroup(
                label=plugin_name,
                items=items
            )
        )

    PLUGIN_MENU = Menu(
        label="Plugins",
        icon_class="mdi mdi-puzzle",
        groups=plugin_menu_groups
    )

    MENUS.append(PLUGIN_MENU)
