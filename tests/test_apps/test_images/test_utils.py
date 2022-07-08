from django import test
from src.apps.images.utils import (
    get_thumbnail_filename,
    get_thumbnail_dimensions,
    get_format,
)


class TestUtils(test.TestCase):
    def test_get_thumbnail_filename_returns_correct_string(self):
        name = "test"
        extension = "jpg"
        size = (300, 300)
        result = get_thumbnail_filename(name=name, extension=extension, size=size)
        self.assertEqual(result, "test-thumbnail-300x300px.jpg")

    def test_get_format_returns_correct_format(self):
        self.assertEqual(get_format("jpg"), "JPEG")
        self.assertEqual(get_format("jpeg"), "JPEG")
        self.assertEqual(get_format("png"), "PNG")
        self.assertEqual(get_format("invalid"), False)

    def test_get_thumbnail_dimensions(self):

        self.assertEqual(
            get_thumbnail_dimensions(
                image_height=300, image_width=600, thumbnail_height=150
            ),
            (300, 150),
        )
        self.assertEqual(
            get_thumbnail_dimensions(
                image_height=300, image_width=150, thumbnail_height=150
            ),
            (75, 150),
        )
        self.assertEqual(
            get_thumbnail_dimensions(
                image_height=300, image_width=300, thumbnail_height=600
            ),
            (600, 600),
        )
        self.assertEqual(
            get_thumbnail_dimensions(
                image_height=301, image_width=300, thumbnail_height=300
            ),
            (300, 300),
        )
        self.assertEqual(
            get_thumbnail_dimensions(
                image_height=301, image_width=301, thumbnail_height=300
            ),
            (300, 300),
        )
