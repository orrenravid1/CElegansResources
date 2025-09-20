from openai import OpenAI

def get_api_key():
    try:
        with open("./APIKeys/openaiapikey.txt", "r", encoding="utf-8") as f:
            api_key = f.read().strip()
    except FileNotFoundError:
        api_key = None
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY not found in file.")
    return api_key

class OpenAIClientWrapper:
    def __init__(self, api_key: str):
        if not api_key:
            self.client = None
            raise RuntimeError("API key is required")
        self.client = OpenAI(api_key=api_key)

    def list_files(self):
        """List all files uploaded to OpenAI."""
        return self.client.files.list().data

    def create_file(self, file_path: str, purpose: str = "user_data"):
        """Upload a file to OpenAI and return the file object."""
        with open(file_path, "rb") as f:
            file = self.client.files.create(
                file=f,
                purpose=purpose
            )
        return file
    
    def delete_file(self, file_id: str):
        """Delete a file from OpenAI by its ID."""
        self.client.files.delete(file_id)

    def get_file_by_id(self, file_id: str):
        """Retrieve a file from OpenAI by its ID."""
        return self.client.files.retrieve(file_id)

    def get_file_by_name(self, filename: str):
        """Retrieve a file from OpenAI by its ID."""
        for f in self.client.files.list().data:
            if f.filename == filename:
                return f
        return None
    
    def file_exists(self, file_path: str) -> bool:
        """Check if a file with the same name exists."""
        for f in self.client.files.list().data:
            if f.filename == file_path:
                return True
        return False
    
    def get_or_create_file(self, file_path: str, purpose: str = "user_data"):
        """Check if a file with the same name exists. If it does, return it. Otherwise, upload the file."""
        for f in self.client.files.list().data:
            if f.filename == file_path:
                print("Get")
                return f
        print("Create")
        return self.create_file(file_path, purpose)
    
    def list_vector_stores(self):
        # Get a list of all vector stores
        vector_stores = self.client.vector_stores.list()
        vector_store_list = [vs for vs in vector_stores]
        return vector_store_list
    
    def create_vector_store(self, name: str):
        vector_store = None
        if not self.vector_store_exists(name):
            vector_store = self.client.vector_stores.create(
                name=name
            )
        return vector_store
    
    def delete_vector_store(self, vector_store_id: str):
        return self.client.vector_stores.delete(vector_store_id)

    def vector_store_exists(self, name: str) -> bool:
        vector_stores = self.client.vector_stores.list()
        for vs in vector_stores.data:
            if vs.name == name:
                return True
        return False

    def get_vector_store_by_name(self, name: str):
        vector_stores = self.client.vector_stores.list()
        for vs in vector_stores.data:
            if vs.name == name:
                return vs
        return None

    def get_or_create_vector_store(self, name: str):
        vs = self.get_vector_store_by_name(name)
        if vs is None:
            vs = self.create_vector_store(name)
            print("Create")
        else:
            print("Get")
        return vs
    
    def list_vector_store_files(self, vector_store_id: str):
        """Return the set of original filenames currently attached to the vector store."""
        return [f for f in self.client.vector_stores.files.list(vector_store_id=vector_store_id)]
    
    def list_vector_store_filenames(self, vector_store_id: str) -> set[str]:
        """Return the set of original filenames currently attached to the vector store."""
        filenames = []
        for vsfile in self.list_vector_store_files(vector_store_id=vector_store_id):
            try:
                file = self.get_file_from_vector_store_file(vsfile.id)
                filenames.append(file.filename)
            except Exception as e:
                print(e)
                filenames.append(None)
        return filenames
    
    def create_vector_store_file(self, vector_store_id: str, file_id: str):
        return self.client.vector_stores.files.create(
            vector_store_id=vector_store_id,
            file_id=file_id
        )

    def delete_vector_store_file(self, vector_store_id: str, file_id: str):
        return self.client.vector_stores.files.delete(
            vector_store_id=vector_store_id,
            file_id=file_id
        )

    def get_vector_store_file(self, vector_store_id: str, vs_file_id: str):
        return self.client.vector_stores.files.retrieve(
            vector_store_id=vector_store_id,
            file_id=vs_file_id
        )
    
    def get_or_create_vector_store_file(self, vector_store_id: str, file_id: str):
        vs_files = self.list_vector_store_files(vector_store_id=vector_store_id)
        for vsf in vs_files:
            if vsf.id == file_id:
                print("Get")
                return vsf
        print("Create")
        return self.create_vector_store_file(vector_store_id=vector_store_id, file_id=file_id)
    
    def get_file_from_vector_store_file(self, vs_file_id: str):
        return self.client.files.retrieve(vs_file_id)