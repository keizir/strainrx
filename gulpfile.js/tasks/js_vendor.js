'use strict';

var gulp = require('gulp');
var changed = require('gulp-changed');
var config = require('../config/javascript');
var handleErrors = require('../lib/handle_errors');
var plumber = require('gulp-plumber');

gulp.task('js:vendor', function () {
    return gulp.src(config.vendorSrc)
        .pipe(plumber({
            errorHandler: handleErrors
        }))
        .pipe(changed(config.vendorDest, {hasChanged: changed.compareLastModifiedTime}))
        .pipe(gulp.dest(config.vendorDest));
});