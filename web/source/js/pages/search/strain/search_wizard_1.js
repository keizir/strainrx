'use strict';

W.ns('W.pages');

W.pages.StrainSearchWizard1Page = W.pages.StrainSearchBase.extend({

    successURL: '/search/strain/wizard/2/',

    checkedTypes: [],

    ui: {
        $btnSkip: $('.btn-skip-1'),
        $btnSubmit: $('.btn-step-1'),
        $typeInfo: $('.type-info'),
        $checkbox: $('input[type="checkbox"]')
    },

    init: function () {
        this.clickStep1Submit();
        this.ckickStep1Skip();
        this.clickTypeInfo();
        this.clickCheckbox();
    },

    clickStep1Submit: function () {
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

    ckickStep1Skip: function () {
        var that = this;
        this.ui.$btnSkip.on('click', function (e) {
            e.preventDefault();
            that.sendDataToWizard({step: 1, skipped: true}, that.successURL);
        });
    },

    clickTypeInfo: function () {
        this.ui.$typeInfo.on('click', function (e) {
            e.preventDefault();
            W.common.Dialog($('.' + $(this).parent().find('.type').attr('id') + '-dialog'));
        });
    },

    clickCheckbox: function () {
        var that = this;
        this.ui.$checkbox.on('click', function () {
            var $checkbox = $(this);
            if ($checkbox.is(':checked')) {
                that.checkedTypes.push($checkbox.attr('name'));
            } else {
                for (var i = 0; i < that.checkedTypes.length; i++) {
                    if (that.checkedTypes[i] === $checkbox.attr('name')) {
                        that.checkedTypes.splice(i, 1);
                        break;
                    }
                }
            }

            if (that.checkedTypes.length > 0) {
                that.ui.$btnSubmit.removeAttr('disabled');
            } else {
                that.ui.$btnSubmit.attr('disabled', 'disabled');
            }
        });
    }
});
