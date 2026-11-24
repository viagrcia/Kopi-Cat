from django.contrib.auth import login
from .models import Cafe, JournalEntry, PlacedSticker, StripPhoto
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.views import LoginView
from django.http import Http404, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_POST

from .forms import MAX_PHOTO_BYTES, EntryForm, StripForm
from .models import Cafe, JournalEntry, StripPhoto


def home(request):
    cafes = Cafe.objects.all().order_by('name')
    return render(request, 'cafes/home.html', {'cafes': cafes})


def cafe_map_view(request):
    cafes = []
    for c in Cafe.objects.all():
        cafes.append({
            'name': c.name,
            'slug': c.slug,
            'barangay': c.barangay,
            'address': c.address,
            'latitude': c.latitude,
            'longitude': c.longitude,
            'vibe_tags': c.vibe_tags,
            'price_range': c.price_range,
            'rating': float(c.rating) if c.rating is not None else None,
            'hours': c.hours,
            'signature_drink': c.signature_drink or '',
            'image': c.image.url if c.image else '',
        })
    return render(request, 'cafes/map.html', {'cafes': cafes})


def about_dev_view(request):
    return render(request, 'cafes/about_dev.html')


# ---------- accounts ----------

class SiteLoginView(LoginView):
    template_name = 'cafes/auth.html'
    redirect_authenticated_user = True
    extra_context = {'mode': 'login'}


def register_view(request):
    form = UserCreationForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        login(request, form.save())
        return redirect('journal')
    return render(request, 'cafes/auth.html', {'form': form, 'mode': 'register'})


# ---------- journal ----------

def _render_journal(request, form, action=None, open_form=False):
    entries = list(request.user.journal_entries.select_related('cafe'))
    strips = {s.slot: s.image.url for s in request.user.strip_photos.all()}

    # one stamp per cafe, dated by the first visit
    first_visits = {}
    for e in reversed(entries):
        if e.cafe_id and e.cafe_id not in first_visits:
            first_visits[e.cafe_id] = e

    stickers = [
        {'id': s.pk, 'kind': s.kind, 'x': s.x, 'y': s.y, 'rot': s.rotation}
        for s in request.user.stickers.order_by('id')
    ]

    return render(request, 'cafes/journal.html', {
        'entries': entries,
        'latest': [e for e in entries if e.photo][:2],
        'slots': [(i, strips.get(i, '')) for i in range(4)],
        'stamps': list(first_visits.values()),
        'total_cafes': Cafe.objects.count(),
        'stickers': stickers,
        'form': form,
        'form_action': action or reverse('entry_create'),
        'open_form': open_form,
    })


@login_required
def journal_view(request):
    return _render_journal(request, EntryForm())


@login_required
@require_POST
def entry_save(request, pk=None):
    instance = get_object_or_404(JournalEntry, pk=pk, user=request.user) if pk else None
    form = EntryForm(request.POST, request.FILES, instance=instance)
    if form.is_valid():
        entry = form.save(commit=False)
        entry.user = request.user
        entry.save()
        return redirect('journal')
    return _render_journal(request, form, action=request.path, open_form=True)


@login_required
@require_POST
def entry_delete(request, pk):
    entry = get_object_or_404(JournalEntry, pk=pk, user=request.user)
    if entry.photo:
        entry.photo.delete(save=False)
    entry.delete()
    return redirect('journal')


@login_required
@require_POST
def strip_upload(request, slot):
    if slot not in range(4):
        raise Http404
    form = StripForm(request.POST, request.FILES)
    if not form.is_valid() or form.cleaned_data['image'].size > MAX_PHOTO_BYTES:
        return JsonResponse({'error': 'Please choose an image under 5 MB.'}, status=400)
    obj = StripPhoto.objects.filter(user=request.user, slot=slot).first() or StripPhoto(user=request.user, slot=slot)
    if obj.pk:
        obj.image.delete(save=False)
    obj.image = form.cleaned_data['image']
    obj.save()
    return JsonResponse({'url': obj.image.url})


@login_required
@require_POST
def strip_clear(request, slot):
    obj = StripPhoto.objects.filter(user=request.user, slot=slot).first()
    if obj:
        obj.image.delete(save=False)
        obj.delete()
    return JsonResponse({'ok': True})

    STICKER_KINDS = {'star', 'heart', 'cup', 'bean', 'cat', 'sparkle', 'flower', 'leaf', 'tape'}
MAX_STICKERS = 80


def _percent(value):
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    if not math.isfinite(number):
        return None
    return min(max(number, 0), 100)


@login_required
@require_POST
def sticker_add(request):
    kind = request.POST.get('kind')
    x = _percent(request.POST.get('x'))
    y = _percent(request.POST.get('y'))
    if kind not in STICKER_KINDS or x is None or y is None:
        return JsonResponse({'error': 'That sticker could not be placed.'}, status=400)
    if request.user.stickers.count() >= MAX_STICKERS:
        return JsonResponse({'error': 'Your journal is full of stickers!'}, status=400)
    try:
        rotation = float(request.POST.get('rotation', 0))
    except ValueError:
        rotation = 0
    if not math.isfinite(rotation):
        rotation = 0
    rotation = max(-30, min(30, rotation))
    sticker = PlacedSticker.objects.create(user=request.user, kind=kind, x=x, y=y, rotation=rotation)
    return JsonResponse({'id': sticker.pk})


@login_required
@require_POST
def sticker_move(request, pk):
    sticker = get_object_or_404(PlacedSticker, pk=pk, user=request.user)
    x = _percent(request.POST.get('x'))
    y = _percent(request.POST.get('y'))
    if x is None or y is None:
        return JsonResponse({'error': 'Invalid position.'}, status=400)
    sticker.x, sticker.y = x, y
    sticker.save(update_fields=['x', 'y'])
    return JsonResponse({'ok': True})


@login_required
@require_POST
def sticker_delete(request, pk):
    get_object_or_404(PlacedSticker, pk=pk, user=request.user).delete()
    return JsonResponse({'ok': True})