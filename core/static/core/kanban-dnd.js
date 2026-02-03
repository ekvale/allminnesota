/**
 * Kanban drag-and-drop: move task cards between columns.
 * Call window.initKanbanDnd() after Sortable.js has loaded (e.g. from Sortable script onload).
 */
(function () {
  function getCsrfToken() {
    var input = document.querySelector('input[name="csrfmiddlewaretoken"]');
    return input ? input.value : '';
  }

  function postMove(taskId, newStatus) {
    var form = document.createElement('form');
    form.method = 'POST';
    form.action = window.location.pathname + window.location.search;
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
    if (typeof Sortable === 'undefined') return;
    var columns = document.querySelectorAll('.kanban-column');
    if (!columns.length) return;

    columns.forEach(function (el) {
      new Sortable(el, {
        group: 'kanban-tasks',
        draggable: '.task-card',
        animation: 150,
        ghostClass: 'sortable-ghost',
        filter: '.btn, a, input, select, textarea',
        preventOnFilter: true,
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

  window.initKanbanDnd = initKanbanDnd;
  // With defer, Sortable loads first and we run after DOM; init now.
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', function () { initKanbanDnd(); });
  } else {
    initKanbanDnd();
  }
})();
