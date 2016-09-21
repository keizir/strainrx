'use strict';

var gulp = require('gulp');
var sass = require('gulp-sass');
var config = require('../config/sass');
var autoprefixer = require('gulp-autoprefixer');
var handleErrors = require('../lib/handle_errors');
var plumber = require('gulp-plumber');

gulp.task('sass', function () {
    return gulp.src(config.src)
        .pipe(plumber({
            errorHandler: handleErrors
        }))
        .pipe(sass(config.settings))
        .pipe(autoprefixer(config.autoprefixer))
        .pipe(gulp.dest(config.dest));
});