from odmantic import EmbeddedModel


class Attachment(EmbeddedModel):
    file_name: str
    original_file_name: str
