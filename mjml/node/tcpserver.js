'use strict';


var host = '127.0.0.1',
    port = '28101',
    touchstop_fn = null,
    argv = process.argv.slice(2);


switch (argv.length) {
    case 0:
        break;
    case 1:
        port = argv[0];
        break;
    case 2:
        port = argv[0];
        host = argv[1];
        break;
    case 3:
        port = argv[0];
        host = argv[1];
        touchstop_fn = argv[2];
        break;
    default:
        console.log('Run command: NODE_PATH=node_modules node tcpserver.js 28101 127.0.0.1 /tmp/mjmltcpserver.stop');
}


var mjml = require('mjml'),
    net = require('net'),
    fs = require('fs'),
    server = net.createServer();


function handleConnection(conn) {
    conn.setEncoding('utf8');
    conn.on('data', function(d) {
        var result;
        try {
            result = mjml.mjml2html(d.toString());
            conn.write('0');
        } catch (err) {
            result = err.message;
            conn.write('1');
        }
        conn.write(('000000000' + Buffer.byteLength(result).toString()).slice(-9));
        conn.write(result);
    });
    conn.once('close', function() {});
    conn.on('error', function(err) {});
}


server.on('connection', handleConnection);
server.listen(port, host, function () {
    console.log('RUN SERVER %s:%s', host, port);
});


if (touchstop_fn) {
    try {
        fs.statSync(touchstop_fn);
    } catch (e) {
        fs.closeSync(fs.openSync(touchstop_fn, 'w'));
    }

    fs.watchFile(touchstop_fn, function() {
        server.close();
        process.exit();
    });
}
