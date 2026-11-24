from django.conf import settings
from django.db import models
from django.utils import timezone


class Cafe(models.Model):
    PRICE_CHOICES = [
        ('$', 'Affordable / Student-friendly'),
        ('$$', 'Mid-range'),
        ('$$$', 'High-end / Specialty'),
    ]

    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    barangay = models.CharField(max_length=100, default='Malolos')
    address = models.TextField(help_text="Specific street or landmark in Malolos")

    # Geo-mapping coordinates
    latitude = models.FloatField(help_text="e.g., 14.8468")
    longitude = models.FloatField(help_text="e.g., 120.8115")

    # Vibe & Details
    vibe_tags = models.CharField(max_length=255, help_text="Comma-separated tags e.g., Aesthetic, Quiet, Sockets")
    price_range = models.CharField(max_length=10, choices=PRICE_CHOICES, default='$$')
    rating = models.DecimalField(max_digits=2, decimal_places=1, blank=True, null=True, help_text="e.g., 4.7")
    hours = models.CharField(max_length=255, blank=True, help_text="e.g., Mon-Fri 10:00-22:00; Sat-Sun 09:00-23:00")
    signature_drink = models.CharField(max_length=100, blank=True, null=True)
    image = models.ImageField(upload_to='cafe_images/', blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.barangay})"


class ActivityLog(models.Model):
    ACTIONS = [
        ('create', 'Created'),
        ('update', 'Edited'),
        ('delete', 'Deleted'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    action = models.CharField(max_length=10, choices=ACTIONS)
    target = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.get_action_display()} {self.target}"

class JournalEntry(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='journal_entries')
    cafe = models.ForeignKey(Cafe, on_delete=models.SET_NULL, null=True, blank=True)
    title = models.CharField(max_length=200)
    note = models.TextField(blank=True)
    rating = models.PositiveSmallIntegerField(null=True, blank=True)
    visited_on = models.DateField(default=timezone.localdate)
    photo = models.ImageField(upload_to='journal/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-visited_on', '-created_at']

    def __str__(self):
        return f"{self.title} ({self.user})"


class StripPhoto(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='strip_photos')
    slot = models.PositiveSmallIntegerField()
    image = models.ImageField(upload_to='strips/')

    class Meta:
        unique_together = ('user', 'slot')

class PlacedSticker(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='stickers')
    kind = models.CharField(max_length=20)
    x = models.FloatField()
    y = models.FloatField()
    rotation = models.FloatField(default=0)