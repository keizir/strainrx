'use strict';

var config = require('./');
var _ = require('lodash');

module.exports = _.assign({
    src: config.sourceDirectory + '/fonts/**',
    dest: config.publicDirectory + '/fonts'
}, config);