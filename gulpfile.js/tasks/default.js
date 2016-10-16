'use strict';

var gulp = require('gulp');
var gulpSequence = require('gulp-sequence');

gulp.task('default', function (cb) {
    global.watch = true;
    gulpSequence('build', ['watch'], cb);
});

// don't watch files on stage / prod

gulp.task('prod', function (cb) {
    global.watch = false;
    console.log('\n\n Starting production build... \n\n');
    gulpSequence('build', cb);
});