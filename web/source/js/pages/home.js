'use strict';

W.ns('W.pages');

W.pages.HomePage = Class.extend({

    init: function (cfg) {
        this.registerLetsGoButtonClickListener();
    },

    registerLetsGoButtonClickListener: function () {
        var that = this;
        $('.btn-lets-go').on('click', function (e) {
            e.preventDefault();
            window.location.href = 'search/strain/wizard/1';
        });
    }
});
