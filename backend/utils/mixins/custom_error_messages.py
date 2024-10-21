class FtErrorMessagesMixin:
    """
    Replaces built-in validator messages with messages, defined in Meta class. 
    This mixin should be inherited before the actual Serializer class in order to call __init__ method.

    Example of Meta class:

    >>> class Meta:
    >>>     model = User
    >>>     fields = ('url', 'username', 'email', 'groups')
    >>>     ft_error_messages = {
    >>>         'username': {
    >>>             UniqueValidator: _('This username is already taken. Please, try again'),
    >>>             RegexValidator: _('Invalid username')
    >>>         }
    >>>     }
    """
    def __init__(self, *args, **kwargs):
        # noinspection PyArgumentList
        super(FtErrorMessagesMixin, self).__init__(*args, **kwargs)
        self.replace_validators_messages()

    def replace_validators_messages(self):
        for field_name, validators_lookup in self.ft_error_messages.items():
            # noinspection PyUnresolvedReferences
            for validator in self.fields[field_name].validators:
                if type(validator) in validators_lookup:
                    validator.message = validators_lookup[type(validator)]

    @property
    def ft_error_messages(self):
        meta = getattr(self, 'Meta', None)
        return getattr(meta, 'ft_error_messages', {})
