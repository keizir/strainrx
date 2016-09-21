'use strict';

var gulp = require('gulp');
var changed = require('gulp-changed');
var config = require('../config/fonts');

gulp.task('fonts', function () {
    return gulp.src(config.src)
        .pipe(changed(config.dest, {hasChanged: changed.compareLastModifiedTime}))
        .pipe(gulp.dest(config.dest));
});