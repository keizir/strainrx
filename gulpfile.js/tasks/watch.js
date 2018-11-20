'use strict';

var gulp = require('gulp');
var sass = require('../config/sass');
var images = require('../config/images');
var fonts = require('../config/fonts');
var js = require('../config/javascript');

gulp.task('watch', function () {
    gulp.watch(sass.src, ['sass']);
    gulp.watch(images.src, ['images']);
    gulp.watch(fonts.src, ['fonts']);
    gulp.watch(js.node_modules, ['copy:libs']);
    gulp.watch(js.vendorSrc, ['js:vendor']);
    gulp.watch(js.src, ['javascript']);
});
