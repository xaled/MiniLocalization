from abc import abstractmethod, ABC


class BaseLocale(ABC):
    @abstractmethod
    def get(self, key, default=None):
        pass

    @abstractmethod
    def get_rule(self, key, default=None):
        pass

    @abstractmethod
    def get_formatter(self, key, default=None):
        pass

    @abstractmethod
    def format(self, obj: object, fmt: str = None, default_formatter=None, formatter_id: str = None):
        pass

    @abstractmethod
    def apply_rule(self, key, rule_id, *args, **kwargs):
        pass

    @abstractmethod
    def get_text(self, text_key, default=None, *args):
        pass

    @abstractmethod
    def register_rule(self, rule_id, rule_func):
        pass

    @abstractmethod
    def register_formatter(self, formatter_id, formatter_func):
        pass


class Locale(BaseLocale):
    def __init__(self, config: dict, fallback_locale: 'Locale'):
        self.config = config
        self.rules = dict()
        self.formatters = dict()
        self.fallback_locale = fallback_locale

    def get(self, key, default=None):
        return self.config.get(key) or (self.fallback_locale.get(key, default) if self.fallback_locale else default)

    def get_rule(self, key, default=None):
        return self.rules.get(key) or (self.fallback_locale.get_rule(key, default) if self.fallback_locale else default)

    def get_formatter(self, key, default=None):
        return self.formatters.get(key) or (
            self.fallback_locale.get_formatter(key, default) if self.fallback_locale else default)

    def format(self, obj: object, fmt: str = None, default_formatter=None, formatter_id: str = None):
        formatter_id = formatter_id or f"{obj.__class__.__module__}.{obj.__class__.__name__}"

        formatter = self.get_formatter(formatter_id, default=default_formatter)

        if formatter:
            return formatter(obj, self, fmt=fmt)
        if hasattr(obj, '__localized_format__'):
            return getattr(obj, '__localized_format__')(self, fmt=fmt)
        return str(obj)

    def apply_rule(self, config_key, rule_id, *args, **kwargs):
        rule = self.get_rule(rule_id)
        if not rule:
            raise ValueError(f"Rule {rule_id=} not found!")
        resolved_config = self.get(config_key)
        return rule(resolved_config, *args, **kwargs)

    def get_text(self, text_key, default=None, *args):
        default = default or text_key
        resolved_config = self.get(text_key, default=default)

        if isinstance(resolved_config, list) and resolved_config:
            text = str(resolved_config[0])
        else:
            text = str(resolved_config)

        if args:
            text = text % args
        return text

    def register_rule(self, rule_id, rule_func):
        self.rules[rule_id] = rule_func

    def register_formatter(self, formatter_id, formatter_func):
        self.formatters[formatter_id] = formatter_func


class ProxyLocale(BaseLocale, ABC):
    @abstractmethod
    def get_locale(self) -> Locale:
        pass

    def get(self, key, default=None):
        return self.get_locale().get(key, default=default)

    def get_rule(self, key, default=None):
        return self.get_locale().get_rule(key, default=default)

    def get_formatter(self, key, default=None):
        return self.get_locale().get_formatter(key, default=default)

    def format(self, obj: object, fmt: str = None, default_formatter=None, formatter_id: str = None):
        return self.get_locale().format(obj, fmt=fmt, default_formatter=default_formatter, formatter_id=formatter_id)

    def apply_rule(self, key, rule_id, *args, **kwargs):
        return self.get_locale().apply_rule(key, rule_id, *args, **kwargs)

    def get_text(self, text_key, default=None, *args):
        return self.get_locale().get_text(text_key, default=default, *args)

    def register_rule(self, rule_id, rule_func):
        return self.get_locale().register_rule(rule_id, rule_func)

    def register_formatter(self, formatter_id, formatter_func):
        return self.get_locale().register_formatter(formatter_id, formatter_func)
