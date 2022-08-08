from utilities.choices import ChoiceSet


#
# Contacts
#

class ContactPriorityChoices(ChoiceSet):
    PRIORITY_PRIMARY = 'primary'
    PRIORITY_SECONDARY = 'secondary'
    PRIORITY_TERTIARY = 'tertiary'
    PRIORITY_INACTIVE = 'inactive'

    CHOICES = (
        (PRIORITY_PRIMARY, 'Первичный'),
        (PRIORITY_SECONDARY, 'Вторичный'),
        (PRIORITY_TERTIARY, 'Третичный'),
        (PRIORITY_INACTIVE, 'Неактивный'),
    )
