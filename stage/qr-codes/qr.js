const qrcode = require('wifi-qr-code-generator');
const pr = qrcode.generateWifiQRCode({
    ssid: 'xxx',
    password: 'yyy',
    encryption: 'WPA',
    hiddenSSID: false,
    outputFormat: { type: 'image/png' },
});
pr.then((data) => console.log(data));
