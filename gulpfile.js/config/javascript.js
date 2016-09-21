'use strict';

var config = require('./');
var _ = require('lodash');

module.exports = _.assign({
    src: config.sourceDirectory + '/js/**/*.js',
    baseSrc: config.sourceDirectory.replace(/(\.|\/)/g, '') + '/js/',
    vendorSrc: config.sourceDirectory + '/js/vendor/**/*.*',
    vendorDest: config.publicDirectory + '/js/vendor',
    dest: config.publicDirectory + '/js'
}, config);