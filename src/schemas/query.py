from pydantic import BaseModel, ConfigDict, Field


class QuerySchema(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [{
                "query": "SELECT * FROM students",
            }]
        }
    )

    query: str = Field(default=None)

class ValidateQuerySchema(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [{
                "user_query": "SELECT * FROM students",
                "correct_query": "SELECT * FROM students",
            }]
        }
    )

    user_query: str = Field()
    correct_query: str = Field()
