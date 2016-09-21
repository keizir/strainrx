'use strict';

var config = require('./');
var _ = require('lodash');

module.exports = _.assign({
    autoprefixer: {
        browsers: ['last 2 versions']
    },
    src: config.sourceDirectory + '/sass/**/*.scss',
    dest: config.publicDirectory + '/css',
    vendorSrc: config.sourceDirectory + '/sass/vendor/*.css',
    vendorDest: config.publicDirectory + '/css/vendor',
    settings: {}
}, config);