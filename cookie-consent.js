(function () {
  var STORAGE_KEY = 'cookie_consent';
  var consent = localStorage.getItem(STORAGE_KEY);

  function updateConsent(granted) {
    if (typeof gtag === 'function') {
      gtag('consent', 'update', { analytics_storage: granted ? 'granted' : 'denied' });
    }
  }

  if (consent === 'accepted') {
    updateConsent(true);
    return;
  }

  if (consent === 'declined') {
    return;
  }

  // No prior choice — show banner
  var banner = document.createElement('div');
  banner.id = 'cookie-banner';
  banner.style.cssText = [
    'position:fixed',
    'bottom:0',
    'left:0',
    'right:0',
    'background:#1a1a2e',
    'border-top:1px solid rgba(255,255,255,0.1)',
    'padding:14px 24px',
    'display:flex',
    'align-items:center',
    'justify-content:space-between',
    'gap:16px',
    'z-index:9999',
    'font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif',
    'font-size:13px',
    'color:#ccc',
    'flex-wrap:wrap'
  ].join(';');

  banner.innerHTML = [
    '<span>This site uses analytics cookies to understand how visitors engage with the content. No personal data is sold or shared.</span>',
    '<div style="display:flex;gap:10px;flex-shrink:0">',
    '  <button id="cookie-decline" style="background:transparent;border:1px solid rgba(255,255,255,0.25);color:#ccc;padding:6px 16px;border-radius:4px;cursor:pointer;font-size:13px">Decline</button>',
    '  <button id="cookie-accept" style="background:#4f8ef7;border:none;color:#fff;padding:6px 16px;border-radius:4px;cursor:pointer;font-size:13px">Accept</button>',
    '</div>'
  ].join('');

  document.body.appendChild(banner);

  document.getElementById('cookie-accept').addEventListener('click', function () {
    localStorage.setItem(STORAGE_KEY, 'accepted');
    updateConsent(true);
    banner.remove();
  });

  document.getElementById('cookie-decline').addEventListener('click', function () {
    localStorage.setItem(STORAGE_KEY, 'declined');
    banner.remove();
  });
})();
