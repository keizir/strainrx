'use strict';

var gulp = require('gulp');
var gulpSequence = require('gulp-sequence');
var config = require('../config');

gulp.task('build', function (cb) {
    // right now tasks are the same for all envs but when they need to differ here is where to do it
    if (config.stage) {
        console.log('\n\n running STAGE tasks...\n\n');
    } else if (config.prod) {
        console.log('\n\n running PROD tasks...\n\n');
    }

    gulpSequence(['clean'], ['sass', 'images', 'fonts', 'javascript', 'css:vendor', 'js:vendor'], cb);
});