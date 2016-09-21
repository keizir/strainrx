'use strict';

var gulp = require('gulp');
var changed = require('gulp-changed');
var config = require('../config/sass');

gulp.task('css:vendor', function () {
    return gulp.src(config.vendorSrc)
        .pipe(changed(config.vendorDest, {hasChanged: changed.compareLastModifiedTime}))
        .pipe(gulp.dest(config.vendorDest));
});