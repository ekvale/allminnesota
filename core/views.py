"""
Views for All Minnesota: public pages (no auth) and admin dashboard (LoginRequiredMixin).
Traditional server-rendered Django only; no API endpoints.
"""

from decimal import Decimal
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import TemplateView, ListView, DetailView, CreateView, UpdateView, DeleteView, FormView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.urls import reverse_lazy, reverse
from django.utils import timezone
from django.db.models import Q

from .models import FundraisingGoal, Event, VolunteerSignUp, ContactMessage, ImpactUpdate
from .forms import VolunteerForm, ContactForm, GoalUpdateForm, EventForm


# ---------------------------------------------------------------------------
# PUBLIC VIEWS (no login required)
# ---------------------------------------------------------------------------

class HomeView(TemplateView):
    """Home page: hero, progress bar, about snippet, upcoming events, CTA."""
    template_name = 'core/home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        goal = FundraisingGoal.objects.filter(is_active=True).first()
        context['goal'] = goal
        if goal:
            try:
                pct = float(goal.current_amount / goal.target_amount * 100)
                context['progress_percent'] = min(100.0, round(pct, 1))
            except (ZeroDivisionError, TypeError):
                context['progress_percent'] = 0
        else:
            context['progress_percent'] = 0
        # Upcoming published events (date >= today)
        context['upcoming_events'] = Event.objects.filter(
            is_published=True,
            date__gte=timezone.now(),
        ).order_by('date')[:3]
        return context


class AboutView(TemplateView):
    """Static about page: story, partnership, team, commitment."""
    template_name = 'core/about.html'


class EventsView(ListView):
    """List all published events ordered by date."""
    model = Event
    template_name = 'core/events/list.html'
    context_object_name = 'events'

    def get_queryset(self):
        return Event.objects.filter(is_published=True).order_by('date')


class EventDetailView(DetailView):
    """Single event detail page."""
    model = Event
    template_name = 'core/events/detail.html'
    context_object_name = 'event'

    def get_queryset(self):
        return Event.objects.filter(is_published=True)


class HowItWorksView(TemplateView):
    """Static 4-step flow: Donate, Match, Prepare, Deliver."""
    template_name = 'core/how_it_works.html'


class ImpactView(TemplateView):
    """Public impact page: KPIs and last 10 ImpactUpdate records."""
    template_name = 'core/impact.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        goal = FundraisingGoal.objects.filter(is_active=True).first()
        context['goal'] = goal
        if goal:
            try:
                pct = float(goal.current_amount / goal.target_amount * 100)
                context['progress_percent'] = min(100.0, round(pct, 1))
            except (ZeroDivisionError, TypeError):
                context['progress_percent'] = 0
        else:
            context['progress_percent'] = 0
        context['impact_updates'] = ImpactUpdate.objects.select_related('updated_by').order_by('-updated_at')[:10]
        return context


class VolunteerView(FormView):
    """GET: show volunteer form. POST handled by VolunteerSubmitView."""
    template_name = 'core/volunteer.html'
    form_class = VolunteerForm
    success_url = reverse_lazy('core:volunteer')

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, {'form': VolunteerForm()})

    def post(self, request, *args, **kwargs):
        form = VolunteerForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Thank you for signing up to volunteer! We\'ve received your information and will be in touch.')
            return redirect(reverse('core:volunteer') + '?submitted=1')
        return render(request, self.template_name, {'form': form})


class ContactView(FormView):
    """GET: show contact form."""
    template_name = 'core/contact.html'
    form_class = ContactForm
    success_url = reverse_lazy('core:contact')

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, {'form': ContactForm()})

    def post(self, request, *args, **kwargs):
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Thank you! Your message was sent.')
            return redirect('core:contact')
        return render(request, self.template_name, {'form': form})


# ---------------------------------------------------------------------------
# ADMIN DASHBOARD VIEWS (LoginRequiredMixin)
# ---------------------------------------------------------------------------

class AdminDashboardView(LoginRequiredMixin, TemplateView):
    """Dashboard: summary cards, recent volunteers/contacts, events, impact updates."""
    template_name = 'core/admin/dashboard.html'
    login_url = '/admin/login/'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['goal'] = FundraisingGoal.objects.filter(is_active=True).first()
        context['recent_volunteers'] = VolunteerSignUp.objects.all()[:10]
        context['recent_contacts'] = ContactMessage.objects.all()[:10]
        context['events'] = Event.objects.all().order_by('-date')
        context['recent_impact'] = ImpactUpdate.objects.select_related('updated_by').order_by('-updated_at')[:5]
        return context


class GoalUpdateView(LoginRequiredMixin, UpdateView):
    """Form to edit current_amount, meals_funded, volunteers_count; on save create ImpactUpdate."""
    model = FundraisingGoal
    form_class = GoalUpdateForm
    template_name = 'core/admin/goal_update.html'
    success_url = reverse_lazy('core:dashboard')
    login_url = '/admin/login/'
    context_object_name = 'goal'

    def get_object(self, queryset=None):
        return get_object_or_404(FundraisingGoal, is_active=True)

    def form_valid(self, form):
        response = super().form_valid(form)
        # Create ImpactUpdate with updated_by = request.user
        ImpactUpdate.objects.create(
            amount_raised=form.cleaned_data['current_amount'],
            meals_funded=form.cleaned_data['meals_funded'],
            volunteers=form.cleaned_data['volunteers_count'],
            updated_by=self.request.user,
        )
        messages.success(self.request, 'Goal updated and impact record created.')
        return response


class EventCreateView(LoginRequiredMixin, CreateView):
    """Create new event."""
    model = Event
    form_class = EventForm
    template_name = 'core/admin/event_form.html'
    success_url = reverse_lazy('core:dashboard')
    login_url = '/admin/login/'

    def form_valid(self, form):
        messages.success(self.request, 'Event created.')
        return super().form_valid(form)


class EventUpdateView(LoginRequiredMixin, UpdateView):
    """Edit existing event."""
    model = Event
    form_class = EventForm
    template_name = 'core/admin/event_form.html'
    success_url = reverse_lazy('core:dashboard')
    login_url = '/admin/login/'
    context_object_name = 'event'

    def form_valid(self, form):
        messages.success(self.request, 'Event updated.')
        return super().form_valid(form)


class EventDeleteView(LoginRequiredMixin, DeleteView):
    """Confirm and delete event."""
    model = Event
    template_name = 'core/admin/event_confirm_delete.html'
    success_url = reverse_lazy('core:dashboard')
    login_url = '/admin/login/'
    context_object_name = 'event'

    def form_valid(self, form):
        messages.success(self.request, 'Event deleted.')
        return super().form_valid(form)


class VolunteerListView(LoginRequiredMixin, ListView):
    """Paginated list of VolunteerSignUp, searchable by name/email."""
    model = VolunteerSignUp
    template_name = 'core/admin/volunteer_list.html'
    context_object_name = 'volunteers'
    paginate_by = 20
    login_url = '/admin/login/'

    def get_queryset(self):
        qs = VolunteerSignUp.objects.all()
        q = self.request.GET.get('q', '').strip()
        if q:
            qs = qs.filter(
                Q(first_name__icontains=q) | Q(last_name__icontains=q) | Q(email__icontains=q)
            )
        return qs.order_by('-submitted_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_query'] = self.request.GET.get('q', '')
        return context


class ContactListView(LoginRequiredMixin, ListView):
    """Paginated list of ContactMessage records."""
    model = ContactMessage
    template_name = 'core/admin/contact_list.html'
    context_object_name = 'contacts'
    paginate_by = 20
    login_url = '/admin/login/'

    def get_queryset(self):
        return ContactMessage.objects.all().order_by('-submitted_at')
