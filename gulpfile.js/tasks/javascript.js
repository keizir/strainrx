'use strict';

var gulp = require('gulp');
var changed = require('gulp-changed');
var config = require('../config/javascript');
var handleErrors = require('../lib/handle_errors');
var plumber = require('gulp-plumber');
var npmDist = require('gulp-npm-dist');

gulp.task('javascript', function () {
    return gulp.src(config.src)
        .pipe(plumber({
            errorHandler: handleErrors
        }))
        .pipe(changed(config.dest, {hasChanged: changed.compareLastModifiedTime}))
        .pipe(gulp.dest(config.dest));
});

// Copy dependencies to ./public/libs/
gulp.task('copy:libs', function() {
  gulp.src(npmDist(), {base:'./node_modules'})
    .pipe(gulp.dest(config.publicDirectory));
});
