/**
 * MBON Contact form backend — Google Apps Script Web App.
 * (Not part of the Hugo build. Paste this into a Sheet-bound Apps Script project.)
 *
 * It receives a POST from the Contact form (layouts/_default/contact.html →
 * static/js/contact.js), logs each message to a tab in the bound Google Sheet,
 * saves any attachment to Drive, and emails the team. The recipient addresses live
 * ONLY in NOTIFY_EMAILS below — they are never published on the website.
 *
 * ── Setup ────────────────────────────────────────────────────────────────────
 * 1. Create a Google Sheet (this becomes the submissions log + attachment owner).
 * 2. Extensions → Apps Script. Delete the stub, paste this file, and edit the
 *    CONFIG block (NOTIFY_EMAILS at minimum). Save.
 * 3. Deploy → New deployment → type "Web app":
 *      • Execute as:      Me
 *      • Who has access:  Anyone
 *    Deploy, authorize when prompted, and copy the Web app URL (…/exec).
 * 4. Put that URL in hugo.yaml → params.contact_endpoint, rebuild, and the form
 *    goes live. (Re-deploy as a *new version* whenever you edit this script.)
 *
 * Note: the form posts application/x-www-form-urlencoded with mode:"no-cors", so the
 * browser can't read the reply — that's expected. Validation happens client-side and
 * here; a failed send is caught as a network error on the page.
 */

// ── CONFIG (edit these) ──────────────────────────────────────────────────────
var NOTIFY_EMAILS = ['CHANGE-ME@example.org'];   // team recipients (kept private, server-side)
var SHEET_TAB     = 'Contacts';                  // tab in the bound Sheet to append to
var DRIVE_FOLDER  = 'MBON Contact Attachments';  // Drive folder for uploaded files
var MAX_BYTES     = 10 * 1024 * 1024;            // 10 MB attachment cap (matches the form)
// ─────────────────────────────────────────────────────────────────────────────

function doPost(e) {
  try {
    var p = (e && e.parameter) || {};
    var name    = (p.name    || '').toString().trim();
    var email   = (p.email   || '').toString().trim();
    var subject = (p.subject || '').toString().trim();
    var message = (p.message || '').toString().trim();

    if (!name || !email || !message) {
      return json_({ ok: false, error: 'Missing required fields.' });
    }
    if (!/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(email)) {
      return json_({ ok: false, error: 'Invalid email.' });
    }

    // optional attachment: sent as base64 in a field, so no multipart parsing needed
    var attachment = null, attachmentUrl = '';
    if (p.fileData && p.fileName) {
      var bytes = Utilities.base64Decode(p.fileData);
      if (bytes.length > MAX_BYTES) {
        return json_({ ok: false, error: 'Attachment too large.' });
      }
      attachment = Utilities.newBlob(bytes, p.fileType || 'application/octet-stream', p.fileName);
      attachmentUrl = getFolder_(DRIVE_FOLDER).createFile(attachment).getUrl();
    }

    // log to the bound Sheet
    getSheet_(SHEET_TAB).appendRow([new Date(), name, email, subject, message, attachmentUrl]);

    // notify the team — recipients come from NOTIFY_EMAILS, not from the request
    var body =
      'New message from the MBON website contact form:\n\n' +
      'Name: '    + name + '\n' +
      'Email: '   + email + '\n' +
      'Subject: ' + (subject || '(none)') + '\n\n' +
      message + '\n' +
      (attachmentUrl ? '\nAttachment: ' + attachmentUrl + '\n' : '');
    var options = { name: 'MBON website', replyTo: email };
    if (attachment) options.attachments = [attachment];
    MailApp.sendEmail(NOTIFY_EMAILS.join(','), 'MBON contact: ' + (subject || name), body, options);

    return json_({ ok: true });
  } catch (err) {
    return json_({ ok: false, error: String(err) });
  }
}

function doGet() {
  return json_({ ok: true, note: 'MBON contact endpoint — POST to submit.' });
}

function getSheet_(tab) {
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  var sh = ss.getSheetByName(tab);
  if (!sh) {
    sh = ss.insertSheet(tab);
    sh.appendRow(['Timestamp', 'Name', 'Email', 'Subject', 'Message', 'Attachment']);
  }
  return sh;
}

function getFolder_(name) {
  var it = DriveApp.getFoldersByName(name);
  return it.hasNext() ? it.next() : DriveApp.createFolder(name);
}

function json_(obj) {
  return ContentService
    .createTextOutput(JSON.stringify(obj))
    .setMimeType(ContentService.MimeType.JSON);
}
