class MongoWrapper:
    def __init__(self, mongo_database):
        self._mongo_database = mongo_database
    
    def validate_document_format(self, document: str):
        return type(document) is dict
    
    def validate_documents_format(self, documents: list):
        return all([self.validate_document_format(document) for document in documents])
    
    def find_one(self, query):
        return self._mongo_database.find_many(query)
    
    def find(self, query):
        return self._mongo_database.find(query)

    def insert_one(self, document):
        self.validate_document_format(document)
        return self._mongo_database.insert_one(document)
    
    def insert_many(self, documents):
        self.validate_documents_format(documents)
        return self._mongo_database.insert_many(documents)
    
    def delete_one(self, query):
        return self._mongo_database.delete_one(query)
    
    def delete_many(self, query):
        return self._mongo_database.delete_many(query)
    
    def drop_duplicates(self):
        pass

    