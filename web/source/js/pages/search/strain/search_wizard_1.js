'use strict';

W.ns('W.pages');

W.pages.StrainSearchWizard1Page = W.pages.StrainSearchBase.extend({

    successURL: '/search/strain/wizard/2/',

    ui: {
        $btnSkip: $('.btn-skip-1'),
        $btnSubmit: $('.btn-step-1'),
        $typeInfo: $('.type-info')
    },

    init: function () {
        this.registerStep1ClickListener();
        this.registerStep1SkipClickListener();
        this.registerTypeInfoClickListener();
    },

    registerStep1ClickListener: function () {
        var that = this;
        this.ui.$btnSubmit.on('click', function (e) {
            e.preventDefault();
            that.sendDataToWizard({
                step: 1,
                sativa: $('input[name="sativa"]').is(":checked"),
                hybrid: $('input[name="hybrid"]').is(":checked"),
                indica: $('input[name="indica"]').is(":checked")
            }, that.successURL);
        });
    },

    registerStep1SkipClickListener: function () {
        var that = this;
        this.ui.$btnSkip.on('click', function (e) {
            e.preventDefault();
            that.sendDataToWizard({step: 1, skipped: true}, that.successURL);
        });
    },

    registerTypeInfoClickListener: function () {
        var that = this;
        this.ui.$typeInfo.on('click', function (e) {
            e.preventDefault();
            var strainType = $(this).parent().find('.type').attr('id');
            // alert(strainType);
            var $dialog = $('.' + strainType + '-dialog');
            $dialog.removeClass('hidden');
            $dialog.dialog();
        });
    }
});
