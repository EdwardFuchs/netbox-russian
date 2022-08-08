from utilities.choices import ChoiceSet


class IPAddressFamilyChoices(ChoiceSet):

    FAMILY_4 = 4
    FAMILY_6 = 6

    CHOICES = (
        (FAMILY_4, 'IPv4'),
        (FAMILY_6, 'IPv6'),
    )


#
# Prefixes
#

class PrefixStatusChoices(ChoiceSet):
    key = 'Prefix.status'

    STATUS_CONTAINER = 'container'
    STATUS_ACTIVE = 'active'
    STATUS_RESERVED = 'reserved'
    STATUS_DEPRECATED = 'deprecated'

    CHOICES = [
        (STATUS_CONTAINER, 'Container', 'gray'),
        (STATUS_ACTIVE, 'Активный', 'blue'),
        (STATUS_RESERVED, 'Зарезервированный', 'cyan'),
        (STATUS_DEPRECATED, 'Устаревший', 'red'),
    ]


#
# IP Ranges
#

class IPRangeStatusChoices(ChoiceSet):
    key = 'IPRange.status'

    STATUS_ACTIVE = 'active'
    STATUS_RESERVED = 'reserved'
    STATUS_DEPRECATED = 'deprecated'

    CHOICES = [
        (STATUS_ACTIVE, 'Активный', 'blue'),
        (STATUS_RESERVED, 'Зарезервированный', 'cyan'),
        (STATUS_DEPRECATED, 'Устаревший', 'red'),
    ]


#
# IP Addresses
#

class IPAddressStatusChoices(ChoiceSet):
    key = 'IPAddress.status'

    STATUS_ACTIVE = 'active'
    STATUS_RESERVED = 'reserved'
    STATUS_DEPRECATED = 'deprecated'
    STATUS_DHCP = 'dhcp'
    STATUS_SLAAC = 'slaac'

    CHOICES = [
        (STATUS_ACTIVE, 'Активный', 'blue'),
        (STATUS_RESERVED, 'Зарезервированный', 'cyan'),
        (STATUS_DEPRECATED, 'Устаревший', 'red'),
        (STATUS_DHCP, 'DHCP', 'green'),
        (STATUS_SLAAC, 'SLAAC', 'purple'),
    ]


class IPAddressRoleChoices(ChoiceSet):

    ROLE_LOOPBACK = 'loopback'
    ROLE_SECONDARY = 'secondary'
    ROLE_ANYCAST = 'anycast'
    ROLE_VIP = 'vip'
    ROLE_VRRP = 'vrrp'
    ROLE_HSRP = 'hsrp'
    ROLE_GLBP = 'glbp'
    ROLE_CARP = 'carp'

    CHOICES = (
        (ROLE_LOOPBACK, 'Loopback', 'gray'),
        (ROLE_SECONDARY, 'Вторичный', 'blue'),
        (ROLE_ANYCAST, 'Anycast', 'yellow'),
        (ROLE_VIP, 'VIP', 'purple'),
        (ROLE_VRRP, 'VRRP', 'green'),
        (ROLE_HSRP, 'HSRP', 'green'),
        (ROLE_GLBP, 'GLBP', 'green'),
        (ROLE_CARP, 'CARP', 'green'),
    )


#
# FHRP
#

class FHRPGroupProtocolChoices(ChoiceSet):

    PROTOCOL_VRRP2 = 'vrrp2'
    PROTOCOL_VRRP3 = 'vrrp3'
    PROTOCOL_HSRP = 'hsrp'
    PROTOCOL_GLBP = 'glbp'
    PROTOCOL_CARP = 'carp'
    PROTOCOL_CLUSTERXL = 'clusterxl'
    PROTOCOL_OTHER = 'other'

    CHOICES = (
        ('Standard', (
            (PROTOCOL_VRRP2, 'VRRPv2'),
            (PROTOCOL_VRRP3, 'VRRPv3'),
            (PROTOCOL_CARP, 'CARP'),
        )),
        ('CheckPoint', (
            (PROTOCOL_CLUSTERXL, 'ClusterXL'),
        )),
        ('Cisco', (
            (PROTOCOL_HSRP, 'HSRP'),
            (PROTOCOL_GLBP, 'GLBP'),
        )),
        (PROTOCOL_OTHER, 'Прочее'),
    )


class FHRPGroupAuthTypeChoices(ChoiceSet):

    AUTHENTICATION_PLAINTEXT = 'plaintext'
    AUTHENTICATION_MD5 = 'md5'

    CHOICES = (
        (AUTHENTICATION_PLAINTEXT, 'Незашифрованный текст'),
        (AUTHENTICATION_MD5, 'MD5'),
    )


#
# VLANs
#

class VLANStatusChoices(ChoiceSet):
    key = 'VLAN.status'

    STATUS_ACTIVE = 'active'
    STATUS_RESERVED = 'reserved'
    STATUS_DEPRECATED = 'deprecated'

    CHOICES = [
        (STATUS_ACTIVE, 'Активный', 'blue'),
        (STATUS_RESERVED, 'Зарезервированный', 'cyan'),
        (STATUS_DEPRECATED, 'Устаревший', 'red'),
    ]


#
# Services
#

class ServiceProtocolChoices(ChoiceSet):

    PROTOCOL_TCP = 'tcp'
    PROTOCOL_UDP = 'udp'
    PROTOCOL_SCTP = 'sctp'

    CHOICES = (
        (PROTOCOL_TCP, 'TCP'),
        (PROTOCOL_UDP, 'UDP'),
        (PROTOCOL_SCTP, 'SCTP'),
    )
