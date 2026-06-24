class BusinessException(Exception):
    """
    İş/uygulama katmanı hataları için temel exception sınıfı.
    """

    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(message)


class NotFoundException(BusinessException):
    """
    İstenen kaynak bulunamadığında fırlatılır.
    """


class ValidationException(BusinessException):
    """
    İş katmanı doğrulaması başarısız olduğunda fırlatılır.
    """

