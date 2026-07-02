// MBON contact form → Google Apps Script web app (scripts/contact-form.gs).
// Reads the endpoint from the form's data-endpoint attribute, validates, reads any
// attachment as base64, and POSTs url-encoded with mode:"no-cors". Recipient emails
// live in the Apps Script, never in this page.
(function () {
  var form = document.getElementById('contact-form');
  if (!form) return;
  var endpoint = form.dataset.endpoint;
  var statusEl = document.getElementById('contact-status');
  var fileInput = form.querySelector('input[type=file]');
  var submitBtn = form.querySelector('button[type=submit]');
  var MAX_BYTES = 10 * 1024 * 1024;

  function setStatus(msg, kind) {
    statusEl.textContent = msg;
    statusEl.className = 'contact-status' + (kind ? ' contact-status--' + kind : '');
  }

  function readAsBase64(file) {
    return new Promise(function (resolve, reject) {
      var r = new FileReader();
      r.onload = function () { resolve(String(r.result).split(',')[1] || ''); };
      r.onerror = reject;
      r.readAsDataURL(file);
    });
  }

  form.addEventListener('submit', function (ev) {
    ev.preventDefault();
    if (!endpoint) { setStatus('The form is not configured yet.', 'error'); return; }

    var fd = new FormData(form);
    var name = (fd.get('name') || '').trim();
    var email = (fd.get('email') || '').trim();
    var message = (fd.get('message') || '').trim();
    var file = fileInput && fileInput.files[0];

    if (!name || !email || !message) {
      setStatus('Please fill in your name, email, and message.', 'error'); return;
    }
    if (!/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(email)) {
      setStatus('Please enter a valid email address.', 'error'); return;
    }
    if (file && file.size > MAX_BYTES) {
      setStatus('That attachment is larger than 10 MB — please attach a smaller file.', 'error'); return;
    }

    var body = new URLSearchParams();
    body.set('name', name);
    body.set('email', email);
    body.set('subject', (fd.get('subject') || '').trim());
    body.set('message', message);

    submitBtn.disabled = true;
    setStatus('Sending…');

    var prep = file
      ? readAsBase64(file).then(function (b64) {
          body.set('fileName', file.name);
          body.set('fileType', file.type || 'application/octet-stream');
          body.set('fileData', b64);
        })
      : Promise.resolve();

    prep
      .then(function () { return fetch(endpoint, { method: 'POST', mode: 'no-cors', body: body }); })
      .then(function () {
        form.reset();
        setStatus('Thanks — your message has been sent.', 'ok');
      })
      .catch(function () {
        setStatus('Sorry, something went wrong sending your message. Please try again, or open a GitHub issue.', 'error');
      })
      .finally(function () { submitBtn.disabled = false; });
  });
})();
