(function () {
  // Detect subpage by checking if the script src contains '../'
  const scriptSrc = document.currentScript ? document.currentScript.getAttribute('src') : '';
  const isRoot = scriptSrc.indexOf('../') === -1;
  const base   = isRoot ? '' : '../';

  const apps = [
    { id: 'baytransit', label: 'BayTransit' },
    { id: 'habitplate', label: 'HabitPlate' },
    { id: 'wyr',        label: 'WYR'        },
    { id: 'workone',    label: 'WorkOne'    },
  ];

  const pages = [
    { file: 'privacy.html', label: 'Privacy Policy'     },
    { file: 'terms.html',   label: 'Terms & Conditions' },
    { file: 'contact.html', label: 'Contact'             },
  ];

  const currentPath = window.location.pathname;

  var icons = {
    section:  '<svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/><polyline points="9 22 9 12 15 12 15 22"/></svg>',
    privacy:  '<svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>',
    terms:    '<svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/></svg>',
    contact:  '<svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"/><polyline points="22,6 12,13 2,6"/></svg>'
  };

  var pageIcons = { 'privacy.html': icons.privacy, 'terms.html': icons.terms, 'contact.html': icons.contact };

  const navItems = apps.map(function (app) {
    const isActiveApp = currentPath.includes('/' + app.id + '/');
    const sectionHref = isRoot ? '#' + app.id : base + 'index.html#' + app.id;
    const toggleClass = 'nav-link dropdown-toggle' + (isActiveApp ? ' active' : '');

    const subPageItems = pages.map(function (p) {
      const isActivePage = isActiveApp && currentPath.endsWith(p.file);
      return '<li><a class="dropdown-item' + (isActivePage ? ' active' : '') +
             '" href="' + base + app.id + '/' + p.file + '">' +
             pageIcons[p.file] + ' ' + p.label + '</a></li>';
    }).join('');

    return (
      '<li class="nav-item dropdown">' +
        '<a class="' + toggleClass + '" href="' + sectionHref + '"' +
        ' data-bs-toggle="dropdown" aria-expanded="false">' + app.label + '</a>' +
        '<ul class="dropdown-menu">' +
          subPageItems +
        '</ul>' +
      '</li>'
    );
  }).join('');

  const html =
    '<nav class="navbar navbar-expand-lg navbar-dark fixed-top site-nav" id="mainNav">' +
      '<div class="container-fluid">' +
        '<a class="navbar-brand dcw-brand" href="' + base + 'index.html">' +
          '<span class="dcw-label">DCW</span>' +
          '<span class="dcw-sub">Design \xb7 Culture \xb7 Software</span>' +
        '</a>' +
        '<button class="navbar-toggler border-0" type="button"' +
        ' data-bs-toggle="collapse" data-bs-target="#navbarNav">' +
          '<span class="navbar-toggler-icon"></span>' +
        '</button>' +
        '<div class="collapse navbar-collapse" id="navbarNav">' +
          '<ul class="navbar-nav ms-auto gap-2 gap-md-4">' + navItems + '</ul>' +
        '</div>' +
      '</div>' +
    '</nav>';

  document.body.insertAdjacentHTML('afterbegin', html);

  // Desktop only: when hovering one nav-item, close any other open dropdown.
  document.querySelectorAll('#mainNav .nav-item.dropdown').forEach(function (item) {
    item.addEventListener('mouseenter', function () {
      if (window.innerWidth >= 992) {
        document.querySelectorAll('#mainNav .nav-item.dropdown').forEach(function (other) {
          if (other !== item) {
            other.querySelector('.dropdown-menu').classList.remove('show');
            var toggle = other.querySelector('.dropdown-toggle');
            if (toggle) toggle.setAttribute('aria-expanded', 'false');
          }
        });
      }
    });
  });

  // Desktop only: prevent Bootstrap from toggling dropdowns on click.
  // Dropdowns open via CSS hover only. Clicks follow the href instead.
  document.querySelectorAll('#mainNav .nav-link.dropdown-toggle').forEach(function (link) {
    link.addEventListener('click', function (e) {
      if (window.innerWidth >= 992) {
        e.preventDefault();
        e.stopPropagation();
        if (isRoot) {
          var id = this.getAttribute('href').replace('#', '');
          var target = document.getElementById(id);
          if (target) target.scrollIntoView({ behavior: 'smooth' });
        } else {
          window.location.href = this.getAttribute('href');
        }
      }
    }, true);
  });
}());
