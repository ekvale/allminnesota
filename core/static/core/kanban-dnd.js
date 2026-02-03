/**
 * Kanban drag-and-drop: move task cards between columns.
 * Requires Sortable.js to be loaded. Run after DOM ready.
 */
(function () {
  function getCsrfToken() {
    var input = document.querySelector('input[name="csrfmiddlewaretoken"]');
    return input ? input.value : '';
  }

  function postMove(taskId, newStatus) {
    var form = document.createElement('form');
    form.method = 'POST';
    form.action = window.location.pathname;
    form.style.display = 'none';

    var csrf = document.createElement('input');
    csrf.type = 'hidden';
    csrf.name = 'csrfmiddlewaretoken';
    csrf.value = getCsrfToken();
    form.appendChild(csrf);

    var taskInput = document.createElement('input');
    taskInput.type = 'hidden';
    taskInput.name = 'task_id';
    taskInput.value = taskId;
    form.appendChild(taskInput);

    var statusInput = document.createElement('input');
    statusInput.type = 'hidden';
    statusInput.name = 'status';
    statusInput.value = newStatus;
    form.appendChild(statusInput);

    document.body.appendChild(form);
    form.submit();
  }

  function initKanbanDnd() {
    var columns = document.querySelectorAll('.kanban-column');
    if (!columns.length || typeof Sortable === 'undefined') return;

    columns.forEach(function (el) {
      new Sortable(el, {
        group: 'kanban-tasks',
        draggable: '.task-card',
        handle: '.task-card-drag-handle',
        animation: 150,
        ghostClass: 'opacity-50',
        onEnd: function (evt) {
          var fromStatus = evt.from.dataset.status;
          var toStatus = evt.to.dataset.status;
          if (fromStatus === toStatus) return;
          var taskId = evt.item.dataset.taskId;
          if (taskId) postMove(taskId, toStatus);
        }
      });
    });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initKanbanDnd);
  } else {
    initKanbanDnd();
  }
})();
