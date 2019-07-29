'use strict';

var mjml = require('mjml'),
    mjml_maj_ver = parseInt(require('mjml/package.json').version.split('.')[0]),
    net = require('net'),
    fs = require('fs'),
    argv = process.argv.slice(2),
    server = null,
    conf = {
        host: '127.0.0.1',
        port: '28101',
        touchstop: null,
        mjml: {}
    };

function terminate(exit_code) {
    if (server && server.listening) {
        server.close(function () {
            process.exit(exit_code);
        });
    } else {
        process.exit(exit_code);
    }
}

process.on('SIGINT', function() {
    terminate(0);
});

process.on('SIGTERM', function() {
    terminate(0);
});

for (var i = 0; i < argv.length; i++) {
    var kv, key, val,
        arg = argv[i];
    try {
        if (!arg.startsWith('--')) {
            throw {message: 'unknown arg'};
        } else {
            arg = arg.slice(2);
        }
        if (arg === 'help') {
            if (mjml_maj_ver >= 4) {
                // more options: https://github.com/mjmlio/mjml/blob/master/packages/mjml-core/src/index.js#L34
                console.log('Run command: NODE_PATH=node_modules node tcpserver.js ' +
                            '--port=28101 --host=127.0.0.1 --touchstop=/tmp/mjmltcpserver.stop ' +
                            '--mjml.minify=false --mjml.validationLevel=soft');
            } else {
                // more options: https://github.com/mjmlio/mjml/blob/3.3.x/packages/mjml-core/src/MJMLRenderer.js#L78
                console.log('Run command: NODE_PATH=node_modules node tcpserver.js ' +
                            '--port=28101 --host=127.0.0.1 --touchstop=/tmp/mjmltcpserver.stop ' +
                            '--mjml.disableMinify=false --mjml.level=soft');
            }
            terminate(0);
        }
        kv = arg.split('=', 2);
        key = kv[0];
        val = kv[1];
        if (!key || !val) throw {message: 'wrong syntax'};
        if (conf.hasOwnProperty(key) && key !== 'mjml') {
            conf[key] = val;
        } else if (key.startsWith('mjml.')) {
            if (val === 'true') {
                val = true;
            } else if (val === 'false') {
                val = false;
            }
            conf.mjml[key.slice(5)] = val;
        } else {
            throw {message: 'unknown arg'};
        }
    } catch (err) {
        console.log('Invalid parsing arg "%s": %s', argv[i], err.message);
        terminate(1);
    }
}

function handleConnection(conn) {
    var total_data = '',
        header_size = 9,
        total_data_size, data_size, result;
    conn.setEncoding('utf8');
    conn.on('data', function(d) {
        total_data += d;
        total_data_size = Buffer.byteLength(total_data);
        if (total_data.length < header_size) return;
        if (data_size === undefined) data_size = parseInt(total_data.slice(0, header_size)) + header_size;
        if (total_data_size < data_size) {
            return;
        } else if (total_data_size > data_size) {
            result = 'MJML server received too many data';
            conn.write('1');
        } else {
            try {
                total_data = total_data.slice(header_size).toString();
                if (mjml_maj_ver >= 4) {
                    result = mjml(total_data, conf.mjml);
                } else {
                    result = mjml.mjml2html(total_data, conf.mjml);
                }
                if (typeof result === 'object') {
                    if (result.errors.length) throw {message: JSON.stringify(result.errors, null, 2)};
                    result = result.html;
                }
                conn.write('0');
            } catch (err) {
                result = err.message;
                conn.write('1');
            }
        }
        conn.write((Array(header_size + 1).join('0') + Buffer.byteLength(result).toString()).slice(-9));
        conn.write(result);
        total_data = '';
        data_size = undefined;
        result = undefined;
    });
    conn.on('close', function() {});
    conn.on('error', function(err) {});
    conn.on('end', function() {});
}

server = net.createServer();
server.on('connection', handleConnection);
server.listen(conf.port, conf.host, function () {
    console.log('RUN SERVER %s:%s', conf.host, conf.port);
});

if (conf.touchstop) {
    try {
        fs.statSync(conf.touchstop);
    } catch (e) {
        fs.closeSync(fs.openSync(conf.touchstop, 'w'));
    }

    fs.watchFile(conf.touchstop, function() {
        console.log('STOP SERVER (cause touchstop)');
        terminate(0);
    });
}
