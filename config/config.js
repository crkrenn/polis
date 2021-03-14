<<<<<<< HEAD
console.log('starting yaml config.js')
=======
// Copyright (C) 2012-present, The Authors. This program is free software: you can redistribute it and/or  modify it under the terms of the GNU Affero General Public License, version 3, as published by the Free Software Foundation. This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Affero General Public License for more details. You should have received a copy of the GNU Affero General Public License along with this program.  If not, see <http://www.gnu.org/licenses/>.

"use strict";

let POLIS_ROOT = process.env.POLIS_ROOT

console.log('starting config.js')
>>>>>>> debug/node-convict-2

const convict = require('convict');
const fs = require('fs');
const yaml = require('js-yaml');

convict.addParser({ extension: ['yml', 'yaml'], parse: yaml.safeLoad });

// for additional validation options, use the following: 
// convict.addFormat(require('convict-format-with-validator').ipaddress);

'use strict';

// Define a schema

try {
<<<<<<< HEAD
    let fileContents = fs.readFileSync('./config/schema.yaml', 'utf8');
=======
    // the next line only works with docker-compose
    let fileContents = fs.readFileSync(POLIS_ROOT + 'config/schema.yaml', 'utf8');
>>>>>>> debug/node-convict-2
    let schema = yaml.safeLoad(fileContents);
    var config = convict(schema);    
} catch (e) {
    console.log(e);
}

<<<<<<< HEAD
// Load environment dependent configuration
var env = config.get('env');
config.loadFile('./config/' + env + '.yaml');
=======
console.log('default aws_region:' + config.get('aws_region'));

// Load environment dependent configuration
var env = config.get('env');
config.loadFile(POLIS_ROOT + 'config/' + env + '.yaml');
var now = new Date(); 
console.log('config aws_region:' + config.get('aws_region') + " @ " + now.toUTCString());

const path = POLIS_ROOT + 'config/config_private.yaml';

try {
  if (fs.existsSync(path)) {
    config.loadFile(path);
  }
} catch(err) {
  console.error(err)
}
>>>>>>> debug/node-convict-2

// Perform validation
config.validate({allowed: 'strict'});
 
module.exports = config;

<<<<<<< HEAD
console.log('finishing yaml config.js')
=======

console.log('finishing config.js')

>>>>>>> debug/node-convict-2
