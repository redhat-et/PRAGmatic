from pragmatic.settings import DEFAULT_SETTINGS


def produce_custom_settings(settings_overrides=None):
    """
    Creates a custom settings dict for the current run, where DEFAULT_SETTINGS are overridden with user-specified settings.
    """
    settings = dict(DEFAULT_SETTINGS)
    if settings_overrides is not None:
        for override_key, override_value in settings_overrides.items():
            if override_key not in settings:
                print(f"Warning: undefined parameter {override_key}")
            settings[override_key] = override_value
    return settings
