from dataclasses import dataclass

@dataclass
class RetrievedFilesType:
    name: str
    path: str
    created_at: str
    last_modified_at: str