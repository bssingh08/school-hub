"""
One-time cleanup script: clears invalid old file-path data that was stored
in BinaryField columns after migrating from ImageField.
Run with: python manage.py shell < cleanup_photos.py
"""
import django
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'school_management.settings')
django.setup()

from core.models import Student, Teacher, GalleryImage


def is_valid_image(data):
    """Check if binary data is a real image using magic bytes."""
    if not data:
        return False
    try:
        if isinstance(data, (bytes, memoryview)):
            b = bytes(data)
        else:
            # It's a string — definitely old path data, not image bytes
            return False
        return (
            (len(b) > 3 and b[:3] == b'\xff\xd8\xff') or    # JPEG
            (len(b) > 8 and b[:8] == b'\x89PNG\r\n\x1a\n') or  # PNG
            (len(b) > 6 and b[:6] in (b'GIF87a', b'GIF89a')) or  # GIF
            (len(b) > 12 and b[:4] == b'RIFF' and b[8:12] == b'WEBP')  # WEBP
        )
    except Exception:
        return False


s_fixed = 0
for s in Student.objects.all():
    if s.photo and not is_valid_image(s.photo):
        s.photo = None
        s.save(update_fields=['photo'])
        s_fixed += 1

t_fixed = 0
for t in Teacher.objects.all():
    if t.photo and not is_valid_image(t.photo):
        t.photo = None
        t.save(update_fields=['photo'])
        t_fixed += 1

g_fixed = 0
for g in GalleryImage.objects.all():
    if g.image and not is_valid_image(g.image):
        g.image = None
        g.save(update_fields=['image'])
        g_fixed += 1

print(f"Cleanup complete!")
print(f"  Students cleared: {s_fixed}")
print(f"  Teachers cleared: {t_fixed}")
print(f"  Gallery images cleared: {g_fixed}")
print(f"\nAfter this cleanup, admins can re-upload photos through the edit forms.")
