'use strict';

W.ns('W.views');

// using john resig's simple class inheritence see http://ejohn.org/blog/simple-javascript-inheritance/
W.views.BaseView = Class.extend({

    init: function () {
        var that = this;
    },

    show: function () {
        this.elem.fadeIn();
    },

    hide: function () {
        this.elem.hide();
    }
});