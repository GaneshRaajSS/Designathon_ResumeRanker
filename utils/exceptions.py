class DocumentSimilarityError(Exception):
    pass

class AuthenticationError(DocumentSimilarityError):
    pass

class FileHandlingError(DocumentSimilarityError):
    pass

class DocumentProcessingError(DocumentSimilarityError):
    pass

class SimilarityCalculationError(DocumentSimilarityError):
    pass
