'use strict';

var gulp = require('gulp');
var changed = require('gulp-changed');
//var imagemin = require('gulp-imagemin');
var config = require('../config/images');
var handleErrors = require('../lib/handle_errors');
var plumber = require('gulp-plumber');

gulp.task('images', function () {
    return gulp.src(config.src)
        .pipe(plumber({
            errorHandler: handleErrors
        }))
        .pipe(changed(config.dest), {hasChanged: changed.compareLastModifiedTime})
        // temp disabled since it has trouble running in stage
        //.pipe(imagemin(config.settings))
        .pipe(gulp.dest(config.dest));
});