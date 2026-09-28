from typing import List, Optional

from pydantic import BaseModel, Field

from scrapegraphai.utils.schema_trasform import transform_schema


class Seller(BaseModel):
    name: str


class Product(BaseModel):
    title: str = Field(description="Product title")
    price: Optional[float] = Field(default=None, description="Price in USD")
    tags: Optional[List[str]] = None
    seller: Optional[Seller] = None


def test_transform_schema_keeps_optional_fields():
    result = transform_schema(Product.model_json_schema())

    assert result == {
        "title": {"type": "string", "description": "Product title"},
        "price": {"type": "number", "description": "Price in USD"},
        "tags": ["string"],
        "seller": {"name": {"type": "string", "description": ""}},
    }
