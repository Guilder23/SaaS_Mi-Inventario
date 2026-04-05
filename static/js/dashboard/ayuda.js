document.addEventListener('DOMContentLoaded', function () {
  // FAQ toggle
  document.querySelectorAll('.faq-question').forEach(function (q) {
    q.addEventListener('click', function () {
      var item = q.closest('.faq-item');
      if (!item) return;

      item.classList.toggle('is-open');

      var icon = q.querySelector('i');
      if (icon) {
        if (item.classList.contains('is-open')) {
          icon.classList.remove('fa-chevron-down');
          icon.classList.add('fa-chevron-up');
        } else {
          icon.classList.remove('fa-chevron-up');
          icon.classList.add('fa-chevron-down');
        }
      }
    });
  });

  // Buscador FAQ
  var input = document.getElementById('faqSearch');
  if (!input) return;

  var items = Array.prototype.slice.call(document.querySelectorAll('.faq-item'));

  function normalize(text) {
    return (text || '')
      .toString()
      .toLowerCase()
      .normalize('NFD')
      .replace(/\p{Diacritic}/gu, '');
  }

  input.addEventListener('input', function () {
    var q = normalize(input.value.trim());

    items.forEach(function (item) {
      var question = item.querySelector('.faq-question');
      var answer = item.querySelector('.faq-answer');
      var hay = normalize((question ? question.textContent : '') + ' ' + (answer ? answer.textContent : ''));

      var match = !q || hay.indexOf(q) !== -1;
      item.style.display = match ? '' : 'none';

      // Cierra items ocultos
      if (!match) {
        item.classList.remove('is-open');
        var icon = question ? question.querySelector('i') : null;
        if (icon) {
          icon.classList.remove('fa-chevron-up');
          icon.classList.add('fa-chevron-down');
        }
      }
    });
  });
});
