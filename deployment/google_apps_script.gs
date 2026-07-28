/**
 * MerchPilot AI persistence endpoint.
 *
 * Script Properties required:
 * - SPREADSHEET_ID: destination Google Sheet ID
 * - MERCHPILOT_TOKEN: long random shared secret
 * - NOTIFICATION_EMAIL: Team YOUNGHTT email address (optional)
 *
 * Deploy as a Web App that executes as the owner. Copy the /exec URL into
 * Streamlit Secrets. Do not commit the real token.
 */

function doPost(e) {
  try {
    const payload = JSON.parse(e.postData.contents || "{}");
    const properties = PropertiesService.getScriptProperties();
    const expectedToken = properties.getProperty("MERCHPILOT_TOKEN") || "";
    if (!expectedToken || payload.token !== expectedToken) {
      return jsonResponse_({ ok: false, error: "Unauthorized" });
    }

    const spreadsheetId = properties.getProperty("SPREADSHEET_ID");
    if (!spreadsheetId) {
      return jsonResponse_({ ok: false, error: "SPREADSHEET_ID is not configured" });
    }

    const recordType = String(payload.record_type || "");
    const sheetName = recordType === "decision" ? "Decisions" : "Feedback";
    const record = payload.record || {};
    appendRecord_(SpreadsheetApp.openById(spreadsheetId), sheetName, record);
    notifyTeam_(properties, sheetName, record);
    return jsonResponse_({ ok: true, sheet: sheetName });
  } catch (error) {
    return jsonResponse_({ ok: false, error: String(error) });
  }
}

function appendRecord_(spreadsheet, sheetName, record) {
  let sheet = spreadsheet.getSheetByName(sheetName);
  if (!sheet) sheet = spreadsheet.insertSheet(sheetName);

  const incomingKeys = Object.keys(record);
  let headers = [];
  if (sheet.getLastColumn() > 0) {
    headers = sheet.getRange(1, 1, 1, sheet.getLastColumn()).getValues()[0];
  }
  if (headers.length === 0) {
    headers = incomingKeys;
    sheet.getRange(1, 1, 1, headers.length).setValues([headers]);
    sheet.getRange(1, 1, 1, headers.length).setFontWeight("bold");
    sheet.setFrozenRows(1);
  } else {
    const missing = incomingKeys.filter((key) => !headers.includes(key));
    if (missing.length > 0) {
      sheet.getRange(1, headers.length + 1, 1, missing.length).setValues([missing]);
      headers = headers.concat(missing);
    }
  }
  sheet.appendRow(headers.map((header) => record[header] === undefined ? "" : record[header]));
}

function notifyTeam_(properties, sheetName, record) {
  const recipient = properties.getProperty("NOTIFICATION_EMAIL");
  if (!recipient) return;
  const subject = `[MerchPilot AI] New ${sheetName.slice(0, -1).toLowerCase()} submission`;
  const lines = [
    `A new ${sheetName.toLowerCase()} row was saved for Team YOUNGHTT.`,
    "",
    `Timestamp: ${record.submission_timestamp || ""}`,
    `Role: ${record.participant_role || record.reviewer_role || ""}`,
    `Product: ${record.product_name || ""}`,
    `Decision: ${record.decision_status || ""}`,
    `Would use: ${record.would_use || ""}`,
    "",
    "Open the MerchPilot Google Sheet to review the complete submission."
  ];
  MailApp.sendEmail(recipient, subject, lines.join("\n"));
}

function jsonResponse_(value) {
  return ContentService
    .createTextOutput(JSON.stringify(value))
    .setMimeType(ContentService.MimeType.JSON);
}
