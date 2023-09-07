from .ApiUtils import ApiUtils


class ApiUtilsFactory:
    _api_instance = None

    @classmethod
    def create_api_instance(cls, client_id, client_secret) -> ApiUtils:
        if cls._api_instance is None:
            cls._api_instance = ApiUtils(client_id, client_secret)
        return cls._api_instance

    @classmethod
    def get_api_instance(cls) -> ApiUtils:
        return cls._api_instance
