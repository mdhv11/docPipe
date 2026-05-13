from typing import List, Optional, Union

from pydantic import BaseModel


class ParagraphItem(BaseModel):
    type: str = "paragraph"
    text: str


class BulletListItem(BaseModel):
    type: str = "bullet_list"
    items: List[str]


class TableItem(BaseModel):
    type: str = "table"
    rows: List[List[str]]


ContentItem = Union[ParagraphItem, BulletListItem, TableItem]


class Section(BaseModel):
    heading: str
    content: List[ContentItem]


class DocumentParseResult(BaseModel):
    title: Optional[str] = ""
    sections: List[Section] = []
    metadata: Optional[dict] = {}
