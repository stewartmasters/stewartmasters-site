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
    'background:rgba(13,13,13,0.92)',
    '-webkit-backdrop-filter:blur(24px)',
    'backdrop-filter:blur(24px)',
    'border-top:1px solid #1e1e1e',
    'padding:14px 24px',
    'display:flex',
    'align-items:center',
    'justify-content:space-between',
    'gap:16px',
    'z-index:9999',
    'font-family:"Inter",-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif',
    'font-size:13px',
    'line-height:1.6',
    'color:#B0B0B0',
    'flex-wrap:wrap'
  ].join(';');

  banner.innerHTML = [
    '<span style="max-width:680px">This site uses analytics cookies to understand how visitors engage with the content. No personal data is sold or shared.</span>',
    '<div style="display:flex;gap:10px;flex-shrink:0">',
    '  <button id="cookie-decline" style="background:transparent;border:1px solid #2c2c2c;color:#aaa;padding:8px 18px;border-radius:4px;cursor:pointer;font-size:13px;font-family:\'Space Grotesk\',sans-serif;font-weight:500;transition:border-color 0.2s,color 0.2s">Decline</button>',
    '  <button id="cookie-accept" style="background:#C8A45C;border:none;color:#0D0D0D;padding:8px 18px;border-radius:4px;cursor:pointer;font-size:13px;font-family:\'Space Grotesk\',sans-serif;font-weight:600;transition:background 0.2s,box-shadow 0.2s">Accept</button>',
    '</div>'
  ].join('');

  document.body.appendChild(banner);

  var acceptBtn = document.getElementById('cookie-accept');
  var declineBtn = document.getElementById('cookie-decline');

  acceptBtn.addEventListener('mouseenter', function () {
    acceptBtn.style.background = '#D9B45A';
    acceptBtn.style.boxShadow = '0 0 24px rgba(217, 180, 90, 0.45)';
  });
  acceptBtn.addEventListener('mouseleave', function () {
    acceptBtn.style.background = '#C8A45C';
    acceptBtn.style.boxShadow = 'none';
  });
  declineBtn.addEventListener('mouseenter', function () {
    declineBtn.style.borderColor = '#C8A45C';
    declineBtn.style.color = '#C8A45C';
  });
  declineBtn.addEventListener('mouseleave', function () {
    declineBtn.style.borderColor = '#2c2c2c';
    declineBtn.style.color = '#aaa';
  });

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
