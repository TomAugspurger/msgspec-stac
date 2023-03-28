"""msgspec-stac"""
__version__ = "0.1.0"
import msgspec
import typing
import datetime

Position = tuple[float, float]


# GeoJSON
# Define the 7 standard Geometry types.
# All types set `tag=True`, meaning that they'll make use of a `type` field to
# disambiguate between types when decoding.
class Point(msgspec.Struct, tag=True):
    coordinates: Position


class MultiPoint(msgspec.Struct, tag=True):
    coordinates: list[Position]


class LineString(msgspec.Struct, tag=True):
    coordinates: list[Position]


class MultiLineString(msgspec.Struct, tag=True):
    coordinates: list[list[Position]]


class Polygon(msgspec.Struct, tag=True):
    coordinates: list[list[Position]]


class MultiPolygon(msgspec.Struct, tag=True):
    coordinates: list[list[list[Position]]]


class GeometryCollection(msgspec.Struct, tag=True):
    geometries: list["Geometry"]


Geometry = (
    Point
    | MultiPoint
    | LineString
    | MultiLineString
    | Polygon
    | MultiPolygon
    | GeometryCollection
)


# Define the two Feature types
class Feature(msgspec.Struct, tag=True):
    geometry: Geometry | None = None
    properties: dict | None = None
    id: str | int | None = None


class FeatureCollection(msgspec.Struct, tag=True):
    features: list[Feature]


# A union of all 9 GeoJSON types
GeoJSON = Geometry | Feature | FeatureCollection


# Create a decoder and an encoder to use for decoding & encoding GeoJSON types
loads = msgspec.json.Decoder(GeoJSON).decode
dumps = msgspec.json.Encoder().encode


# --- STAC

class Link(msgspec.Struct):
    href: str
    rel: str
    type: str | None = None
    title: str | None = None


class Asset(msgspec.Struct):
    href: str
    title: str | None = None
    description: str | None = None
    type: str | None = None
    roles: list[str] | None = None

class Item(msgspec.Struct, kw_only=True):
    type: typing.Literal["Feature"] = "Feature"
    stac_version: str
    id: str
    geometry: Geometry | None = None
    bbox: list[float] | None = None

    stac_extensions: list[str] | None = None
    properties: dict = {}  # How should this be typed.
    links: list[Link]
    assets: dict[str, Asset]

    collection: str | None = None


class Provider(msgspec.Struct):
    name: str
    description: str | None = None
    roles: list[str] | None = None
    url: str | None = None


class SpatialExtent(msgspec.Struct):
    bbox: list[list[float]]


temporal_extent = typing.Annotated[
    list[datetime.datetime | None], msgspec.Meta(min_length=2, max_length=2)
]

class TemporalExtent(msgspec.Struct):
    interval: list[temporal_extent]

class Extent(msgspec.Struct):
    spatial: SpatialExtent
    temporal: TemporalExtent


class Summary(msgspec.Struct):
    ...


class Range(msgspec.Struct):
    minimum: str | int | float
    maximum: str | int | float


class Collection(msgspec.Struct, kw_only=True):
    type: typing.Literal["Collection"] = "Collection"
    stac_version: str
    stac_extensions: list[str]
    id: str
    title: str | None = None
    description: str | None = None
    keywords: list[str] | None = None
    license: str
    providers: list[Provider]
    extent: Extent
    # summaries: dict[str, Summary]
    links: list[Link]
    assets: dict[str, Asset]


# Create a decoder and an encoder to use for decoding & encoding GeoJSON types
item_loads = msgspec.json.Decoder(Item).decode
collection_loads = msgspec.json.Decoder(Collection).decode


item_dumps = msgspec.json.Encoder().encode

