from .views import cv_author, cv_book
from .views_bulk import cv_bulk_author

urlpatterns = cv_author.urlpatterns + cv_book.urlpatterns + cv_bulk_author.urlpatterns
