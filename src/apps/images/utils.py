from math import ceil


def get_format(extension: str) -> str:
    if extension in ["jpg", "jpeg"]:
        return "JPEG"
    elif extension == "png":
        return "PNG"
    return False


def get_thumbnail_filename(name: str, extension: str, size: tuple[int]) -> str:
    size = f"{size[0]}x{size[1]}"

    return f"{name}-thumbnail-{size}px.{extension}"


def get_thumbnail_dimensions(
    image_height: int, image_width: int, thumbnail_height: int
) -> tuple[int]:
    scale = image_height / thumbnail_height
    thumbnail_width = image_width / scale
    return (ceil(thumbnail_width), thumbnail_height)
    # rounding down causes PIL to change height
