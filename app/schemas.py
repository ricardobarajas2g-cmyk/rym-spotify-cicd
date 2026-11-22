"""Contrato del endpoint POST /predict; solo columnas de entrada del modelo."""
from pydantic import BaseModel, ConfigDict, Field

class AlbumInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    artista: str = Field(default="", max_length=160, description="Metadato solo para mostrar")
    album: str = Field(default="", max_length=200, description="Metadato solo para mostrar")
    generos_frecuentes: str = Field(min_length=1, max_length=400, examples=["art rock | psychedelic rock"])
    promedio_danceability: float = Field(ge=0, le=1)
    promedio_energy: float = Field(ge=0, le=1)
    promedio_acousticness: float = Field(ge=0, le=1)
    promedio_instrumentalness: float = Field(ge=0, le=1)
    promedio_valence: float = Field(ge=0, le=1)
    promedio_tempo: float = Field(ge=0, le=300, description="BPM")
    promedio_popularity: float = Field(ge=0, le=100)
    promedio_loudness: float = Field(ge=-80, le=15, description="dBFS aproximados")
    anio_spotify: int = Field(ge=1900, le=2100)

class PredictionOutput(BaseModel):
    artista: str
    album: str
    prediction: int
    probabilidad_favorito: float
    interpretacion: str
    modelo: str
