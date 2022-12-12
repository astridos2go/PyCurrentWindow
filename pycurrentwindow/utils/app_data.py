from os import getenv, makedirs, path


def app_data() -> str:
    """Returns location of the AppData directory for the app,
    creating it if it does not exist

    Returns:
        str: The full file location
    """
    app_data: str = path.join(str(getenv("APPDATA")), "PyCurrentWindow")
    if not path.exists(app_data):
        makedirs(app_data)

    return app_data
