/* Путь к профессии — shared site script (nav, FAQ, lead form, phone mask, apply modal) */
(function () {
  'use strict';

  var TG_TOKEN = '8814710536:AAFewXSFvDKcaP2YtVK8K64cy8zPYnAdCYc';
  var TG_CHAT = '5041739228';

  function sendToTelegram(p, source) {
    var lines = [
      '🎓 *Новая заявка с сайта*',
      '📌 *Страница:* ' + source,
      '',
      '👤 *Имя:* ' + (p.name || '—'),
      '📞 *Телефон:* ' + (p.phone || '—'),
      p.interest ? '🏛 *Интересует:* ' + p.interest : '',
      p.grade ? '🏫 *Класс:* ' + p.grade : '',
      p.direction ? '📚 *Направление:* ' + p.direction : '',
      p.goal ? '📊 *Комментарий:* ' + p.goal : '',
      '',
      '🕐 ' + new Date().toLocaleString('ru-RU', { timeZone: 'Europe/Moscow' }) + ' (МСК)'
    ].filter(Boolean).join('\n');
    return fetch('https://api.telegram.org/bot' + TG_TOKEN + '/sendMessage', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ chat_id: TG_CHAT, text: lines, parse_mode: 'Markdown' })
    }).catch(function (e) { console.warn('TG error', e); });
  }

  function phoneMask(inp) {
    inp.addEventListener('focus', function () { if (!this.value) this.value = '+7 ('; });
    inp.addEventListener('blur', function () { if (this.value === '+7 (' || this.value === '+7') this.value = ''; });
    inp.addEventListener('input', function () {
      this.setCustomValidity('');
      var d = this.value.replace(/\D/g, '');
      if (d.slice(0, 1) === '8') d = '7' + d.slice(1);
      if (d.slice(0, 1) === '7') d = d.slice(1);
      if (d.length > 10) d = d.slice(0, 10);
      var r = '+7';
      if (d.length > 0) r += ' (' + d.slice(0, 3);
      if (d.length >= 3) r += ') ' + d.slice(3, 6);
      if (d.length >= 6) r += '-' + d.slice(6, 8);
      if (d.length >= 8) r += '-' + d.slice(8, 10);
      this.value = r;
    });
    inp.addEventListener('keydown', function (e) {
      if (e.key === 'Backspace' && (this.value === '+7 (' || this.value === '+7 ')) this.value = '';
    });
  }

  function wireForm(form) {
    form.addEventListener('submit', function (ev) {
      ev.preventDefault();
      var ph = form.querySelector('[name="phone"]');
      var d = (ph && ph.value || '').replace(/\D/g, '');
      if (ph) ph.setCustomValidity('');
      if (d.length < 10) {
        if (ph) { ph.setCustomValidity('Введите корректный номер телефона'); ph.focus(); }
        form.reportValidity();
        return;
      }
      if (!form.checkValidity()) { form.reportValidity(); return; }
      var btn = form.querySelector('[type="submit"]');
      var origText = btn ? btn.textContent : '';
      if (btn) { btn.disabled = true; btn.textContent = 'Отправляем…'; }
      var g = function (n) { var el = form.querySelector('[name="' + n + '"]'); return el ? (el.value || '').trim() : ''; };
      var payload = { name: g('name'), phone: g('phone'), grade: g('grade'), direction: g('direction'), goal: g('goal'), interest: g('interest') };
      sendToTelegram(payload, window.location.href).then(function () {
        if (btn) { btn.disabled = false; btn.textContent = origText; }
        form.classList.add('is-sent');
      });
    });
  }

  /* ---- Apply modal ---- */
  var modal, modalForm, lastFocus;

  function buildModal() {
    modal = document.createElement('div');
    modal.className = 'modal';
    modal.id = 'applyModal';
    modal.setAttribute('role', 'dialog');
    modal.setAttribute('aria-modal', 'true');
    modal.setAttribute('aria-labelledby', 'applyModalTitle');
    modal.innerHTML =
      '<div class="modal__box">' +
        '<button class="modal__close" type="button" aria-label="Закрыть">✕</button>' +
        '<div class="modal__eyebrow">Бесплатно</div>' +
        '<div class="modal__title" id="applyModalTitle">Оставьте заявку на поступление</div>' +
        '<div class="modal__sub" id="applyModalSub">Перезвоним в течение 30 минут, ответим на вопросы и поможем с поступлением.</div>' +
        '<form class="lead-form" id="applyForm" novalidate>' +
          '<div class="form-fields">' +
            '<input type="hidden" name="interest" value=""/>' +
            '<div class="field"><label for="am-name">Ваше имя</label><input type="text" id="am-name" name="name" placeholder="Александра" autocomplete="given-name" required/></div>' +
            '<div class="field field--phone"><label for="am-phone">Телефон</label><input type="tel" id="am-phone" name="phone" placeholder="+7 (___) ___-__-__" autocomplete="tel" required/></div>' +
            '<label class="consent-row"><input type="checkbox" name="consent" required/><span>Я даю согласие на <a href="/privacy/" target="_blank" class="consent-link">обработку персональных данных</a></span></label>' +
            '<button type="submit" class="btn btn--primary btn--full btn--lg">Отправить заявку →</button>' +
            '<p class="form-note">Отвечаем в течение 30 мин · Без спама · Бесплатно</p>' +
          '</div>' +
          '<div class="form-success" role="alert"><div class="form-success__icon">✓</div><h3>Заявка принята!</h3><p>Перезвоним в течение 30 минут и поможем с поступлением.</p></div>' +
        '</form>' +
      '</div>';
    document.body.appendChild(modal);
    modalForm = modal.querySelector('#applyForm');
    wireForm(modalForm);
    var ph = modalForm.querySelector('[name="phone"]');
    if (ph) phoneMask(ph);
    modal.querySelector('.modal__close').addEventListener('click', closeModal);
    modal.addEventListener('click', function (e) { if (e.target === modal) closeModal(); });
    document.addEventListener('keydown', function (e) { if (e.key === 'Escape' && modal.classList.contains('open')) closeModal(); });
  }

  function openModal(interest) {
    if (!modal) buildModal();
    var sub = modal.querySelector('#applyModalSub');
    var title = modal.querySelector('#applyModalTitle');
    var hidden = modal.querySelector('[name="interest"]');
    modalForm.classList.remove('is-sent');
    if (interest) {
      title.textContent = 'Поступить — ' + interest;
      sub.textContent = 'Оставьте заявку — расскажем о поступлении в «' + interest + '», направлениях и бюджетных местах. Перезвоним за 30 минут.';
      hidden.value = interest;
    } else {
      title.textContent = 'Оставьте заявку на поступление';
      sub.textContent = 'Перезвоним в течение 30 минут, ответим на вопросы и поможем с поступлением.';
      hidden.value = '';
    }
    lastFocus = document.activeElement;
    modal.classList.add('open');
    document.body.classList.add('modal-lock');
    var nameInp = modal.querySelector('#am-name');
    if (nameInp) setTimeout(function () { nameInp.focus(); }, 60);
  }

  function closeModal() {
    if (!modal) return;
    modal.classList.remove('open');
    document.body.classList.remove('modal-lock');
    if (lastFocus && lastFocus.focus) lastFocus.focus();
  }

  function init() {
    // Burger / mobile menu
    var burger = document.getElementById('burger');
    var mobileMenu = document.getElementById('mobileMenu');
    if (burger && mobileMenu) {
      burger.addEventListener('click', function () {
        var o = mobileMenu.classList.toggle('open');
        burger.classList.toggle('open', o);
        burger.setAttribute('aria-expanded', o);
      });
      mobileMenu.querySelectorAll('a').forEach(function (a) {
        a.addEventListener('click', function () {
          mobileMenu.classList.remove('open');
          burger.classList.remove('open');
          burger.setAttribute('aria-expanded', 'false');
        });
      });
    }

    // FAQ accordion
    document.querySelectorAll('.faq-q').forEach(function (btn) {
      btn.addEventListener('click', function () {
        var item = btn.closest('.faq-item');
        var isOpen = item.classList.contains('open');
        document.querySelectorAll('.faq-item').forEach(function (i) {
          i.classList.remove('open');
          var q = i.querySelector('.faq-q'); if (q) q.setAttribute('aria-expanded', 'false');
        });
        if (!isOpen) { item.classList.add('open'); btn.setAttribute('aria-expanded', 'true'); }
      });
    });

    // Inline page forms (non-modal)
    document.querySelectorAll('.lead-form').forEach(wireForm);
    document.querySelectorAll('.lead-form [name="phone"]').forEach(phoneMask);

    // Apply triggers
    document.addEventListener('click', function (e) {
      var t = e.target.closest('[data-apply]');
      if (t) {
        e.preventDefault();
        openModal(t.getAttribute('data-apply') || '');
      }
    });

    // Catalog filter chips (Все / Государственные / С бюджетом / Частные)
    document.querySelectorAll('[data-filter-group]').forEach(function (group) {
      var section = group.closest('section') || group.parentElement;
      var grid = section && section.querySelector('.ic-grid');
      if (!grid) return;
      var cards = Array.prototype.slice.call(grid.querySelectorAll('.ic'));
      var status = section.querySelector('[data-filter-status]');

      function matches(card, filter) {
        return filter === 'all'
          || (filter === 'gos' && card.getAttribute('data-type') === 'gos')
          || (filter === 'chastny' && card.getAttribute('data-type') === 'chastny')
          || (filter === 'budget' && card.getAttribute('data-budget') === '1');
      }

      function countFor(filter) {
        return cards.filter(function (card) { return matches(card, filter); }).length;
      }

      function prepareChip(chip) {
        var filter = chip.getAttribute('data-filter') || 'all';
        var count = countFor(filter);
        var counter = chip.querySelector('.chip__count');
        chip.setAttribute('type', 'button');
        chip.setAttribute('role', 'tab');
        chip.setAttribute('aria-selected', chip.classList.contains('on') ? 'true' : 'false');
        chip.setAttribute('data-count', String(count));
        if (!counter) {
          counter = document.createElement('span');
          counter.className = 'chip__count';
          chip.appendChild(counter);
        }
        counter.textContent = count;
        if (filter !== 'all' && count === 0) {
          chip.disabled = true;
          chip.classList.add('is-disabled');
          chip.setAttribute('aria-disabled', 'true');
        }
      }

      function applyFilter(filter) {
        var visible = 0;
        cards.forEach(function (card) {
          var show = matches(card, filter);
          card.hidden = !show;
          card.style.display = show ? '' : 'none';
          if (show) visible += 1;
        });
        group.querySelectorAll('.chip').forEach(function (chip) {
          var isActive = chip.getAttribute('data-filter') === filter;
          chip.classList.toggle('on', isActive);
          chip.setAttribute('aria-selected', isActive ? 'true' : 'false');
        });
        if (status) {
          status.hidden = visible !== 0;
          status.textContent = visible === 0
            ? 'В этой вкладке пока нет заведений. Выберите другой фильтр или оставьте заявку — подберём вариант вручную.'
            : '';
        }
      }

      group.querySelectorAll('.chip').forEach(prepareChip);
      group.addEventListener('click', function (e) {
        var chip = e.target.closest('.chip');
        if (!chip || chip.disabled || chip.getAttribute('aria-disabled') === 'true') return;
        applyFilter(chip.getAttribute('data-filter') || 'all');
      });
      var active = group.querySelector('.chip.on:not([disabled])') || group.querySelector('.chip:not([disabled])');
      if (active) applyFilter(active.getAttribute('data-filter') || 'all');
    });

    // Favourites (heart) — visual + localStorage
    var FAV_KEY = 'pkp_fav';
    var favs = {};
    try { favs = JSON.parse(localStorage.getItem(FAV_KEY) || '{}'); } catch (e) {}
    document.querySelectorAll('[data-fav]').forEach(function (btn) {
      var card = btn.closest('.ic');
      var link = card && card.querySelector('h4 a');
      var key = link ? link.getAttribute('href') : null;
      if (key && favs[key]) { btn.classList.add('on'); btn.textContent = '♥'; }
      btn.addEventListener('click', function (e) {
        e.preventDefault(); e.stopPropagation();
        var on = btn.classList.toggle('on');
        btn.textContent = on ? '♥' : '♡';
        if (key) { if (on) favs[key] = 1; else delete favs[key];
          try { localStorage.setItem(FAV_KEY, JSON.stringify(favs)); } catch (e) {} }
      });
    });
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init);
  else init();

  window.PKP = { openApply: openModal };
})();
