from django.db import models


class Author(models.Model):
    name = models.CharField(max_length=200)
    country = models.CharField(max_length=100, blank=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Book(models.Model):
    author = models.ForeignKey(Author, on_delete=models.CASCADE, related_name="books")
    title = models.CharField(max_length=200)
    year = models.PositiveIntegerField(null=True, blank=True)

    class Meta:
        ordering = ["title"]

    def __str__(self):
        return self.title
