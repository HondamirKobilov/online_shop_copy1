"""Custom model fields for the shop_admin app."""
from django.db.models.fields.files import ImageField, ImageFieldFile
from django.conf import settings
from environs import Env

# Initialize environment variables
env = Env()
env.read_env()

# Get default product image from environment
DEFAULT_PRODUCT_IMAGE = env.str(
    "DEFAULT_PRODUCT_IMAGE", 
    "https://i.pinimg.com/736x/af/c7/ae/afc7ae95091f8b0c8d6fd97d1557a138.jpg"
)


class DefaultImageFieldFile(ImageFieldFile):
    """Custom ImageFieldFile that returns a default URL when the file is missing."""

    @property
    def url(self):
        """Return the URL for the image, or the default URL if the image is missing."""
        try:
            return super().url
        except ValueError:
            return DEFAULT_PRODUCT_IMAGE


class DefaultImageField(ImageField):
    """Custom ImageField that uses DefaultImageFieldFile."""

    attr_class = DefaultImageFieldFile
