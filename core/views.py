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

from .models import FundraisingGoal, Event, VolunteerSignUp, ContactMessage, ImpactUpdate, Task
from .forms import VolunteerForm, ContactForm, GoalUpdateForm, EventForm, TaskForm


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
            return redirect(reverse('core:contact') + '?submitted=1')
        return render(request, self.template_name, {'form': form})


# ---------------------------------------------------------------------------
# ADMIN DASHBOARD VIEWS (LoginRequiredMixin)
# ---------------------------------------------------------------------------

class AdminDashboardView(LoginRequiredMixin, TemplateView):
    """Dashboard: summary cards, recent volunteers/contacts, events, impact updates, kanban board."""
    template_name = 'core/admin/dashboard.html'
    login_url = '/admin/login/'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['goal'] = FundraisingGoal.objects.filter(is_active=True).first()
        context['recent_volunteers'] = VolunteerSignUp.objects.all()[:10]
        context['recent_contacts'] = ContactMessage.objects.all()[:10]
        context['events'] = Event.objects.all().order_by('-date')
        context['recent_impact'] = ImpactUpdate.objects.select_related('updated_by').order_by('-updated_at')[:5]
        # Kanban board: tasks by status (for embedded board and move-from-dashboard)
        tasks = Task.objects.select_related('assigned_to').all()
        context['backlog'] = tasks.filter(status='backlog').order_by('-order', 'created_at')
        context['to_do'] = tasks.filter(status='to_do').order_by('-order', 'created_at')
        context['in_progress'] = tasks.filter(status='in_progress').order_by('-order', 'created_at')
        context['done'] = tasks.filter(status='done').order_by('-order', 'created_at')
        context['volunteers'] = VolunteerSignUp.objects.all().order_by('first_name', 'last_name')
        return context

    def post(self, request, *args, **kwargs):
        """Handle task status move or reassign from embedded kanban; redirect back to dashboard."""
        task_id = request.POST.get('task_id')
        if 'assigned_to' in request.POST:
            task = get_object_or_404(Task, pk=task_id) if task_id else None
            if task:
                val = request.POST.get('assigned_to', '').strip()
                task.assigned_to_id = int(val) if val else None
                task.save()
                if task.assigned_to:
                    messages.success(request, f'Task assigned to {task.assigned_to.first_name} {task.assigned_to.last_name}.')
                else:
                    messages.success(request, 'Task unassigned.')
        elif task_id and request.POST.get('status') and request.POST.get('status') in dict(Task.STATUS_CHOICES):
            task = get_object_or_404(Task, pk=task_id)
            task.status = request.POST.get('status')
            task.save()
            messages.success(request, f'Task moved to {dict(Task.STATUS_CHOICES).get(task.status)}.')
        return redirect('core:dashboard')


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


# ---------------------------------------------------------------------------
# TASKS & KANBAN (LoginRequiredMixin)
# ---------------------------------------------------------------------------

class KanbanBoardView(LoginRequiredMixin, TemplateView):
    """Kanban board: columns Backlog, To Do, In Progress, Done; tasks as cards."""
    template_name = 'core/admin/kanban.html'
    login_url = '/admin/login/'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        tasks = Task.objects.select_related('assigned_to').all()
        context['backlog'] = tasks.filter(status='backlog').order_by('-order', 'created_at')
        context['to_do'] = tasks.filter(status='to_do').order_by('-order', 'created_at')
        context['in_progress'] = tasks.filter(status='in_progress').order_by('-order', 'created_at')
        context['done'] = tasks.filter(status='done').order_by('-order', 'created_at')
        context['volunteers'] = VolunteerSignUp.objects.all().order_by('first_name', 'last_name')
        return context

    def post(self, request, *args, **kwargs):
        """Quick-move status or reassign; redirect back to kanban."""
        task_id = request.POST.get('task_id')
        if 'assigned_to' in request.POST:
            task = get_object_or_404(Task, pk=task_id) if task_id else None
            if task:
                val = request.POST.get('assigned_to', '').strip()
                task.assigned_to_id = int(val) if val else None
                task.save()
                if task.assigned_to:
                    messages.success(request, f'Task assigned to {task.assigned_to.first_name} {task.assigned_to.last_name}.')
                else:
                    messages.success(request, 'Task unassigned.')
        elif task_id and request.POST.get('status') and request.POST.get('status') in dict(Task.STATUS_CHOICES):
            task = get_object_or_404(Task, pk=task_id)
            task.status = request.POST.get('status')
            task.save()
            messages.success(request, f'Task moved to {dict(Task.STATUS_CHOICES).get(task.status)}.')
        return redirect('core:kanban')


class TaskCreateView(LoginRequiredMixin, CreateView):
    """Create a new task."""
    model = Task
    form_class = TaskForm
    template_name = 'core/admin/task_form.html'
    success_url = reverse_lazy('core:kanban')
    login_url = '/admin/login/'

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        messages.success(self.request, 'Task created.')
        return super().form_valid(form)


class TaskUpdateView(LoginRequiredMixin, UpdateView):
    """Edit task (assign volunteer, change status, etc.)."""
    model = Task
    form_class = TaskForm
    template_name = 'core/admin/task_form.html'
    success_url = reverse_lazy('core:kanban')
    login_url = '/admin/login/'
    context_object_name = 'task'

    def form_valid(self, form):
        messages.success(self.request, 'Task updated.')
        return super().form_valid(form)


class TaskDeleteView(LoginRequiredMixin, DeleteView):
    """Confirm and delete task."""
    model = Task
    template_name = 'core/admin/task_confirm_delete.html'
    success_url = reverse_lazy('core:kanban')
    login_url = '/admin/login/'
    context_object_name = 'task'

    def form_valid(self, form):
        messages.success(self.request, 'Task deleted.')
        return super().form_valid(form)
