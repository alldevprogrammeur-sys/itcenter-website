// main.js — comportements globaux minimes pour IT CENTER

document.addEventListener('DOMContentLoaded', function () {
  // Initialize Bootstrap tooltips if present
  if (window.bootstrap && bootstrap.Tooltip) {
    var tipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tipTriggerList.forEach(function (el) {
      new bootstrap.Tooltip(el);
    });
  }
});