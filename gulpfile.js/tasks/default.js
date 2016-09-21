'use strict';

var gulp = require('gulp');
var gulpSequence = require('gulp-sequence');

gulp.task('default', function (cb) {
    global.watch = true;
    gulpSequence('build', ['watch'], cb);
});

// don't watch files on stage / prod
gulp.task('trevanna_tracks.staging', function (cb) {
    global.watch = false;
    console.log('\n\n Starting staging build... \n\n');
    gulpSequence('build', cb);
});

gulp.task('trevanna_tracks.production', function (cb) {
    global.watch = false;
    console.log('\n\n Starting production build... \n\n');
    gulpSequence('build', cb);
});