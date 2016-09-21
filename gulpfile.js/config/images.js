'use strict';

var config = require('./');
var _ = require('lodash');

module.exports = _.assign({
    src: config.sourceDirectory + '/images/**',
    dest: config.publicDirectory + '/images',
    // see https://www.npmjs.com/package/gulp-imagemin for options list
    settings: {
        optimizationLevel: 3,
        progressive: true
    }
}, config);