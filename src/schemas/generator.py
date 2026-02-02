from pydantic import BaseModel, Field, ConfigDict

class GenerateAIExercise(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [{
                "topic": "Generate an exercise",
            }]
        }
    )
    topic: str = Field(default=None)

