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

    init: function init() {
        this.restoreState();
        this.clickStep1Submit();
        this.clickStep1Skip();
        this.clickTypeInfo();
        this.clickCheckbox();
    },

    restoreState: function restoreState() {
        var step1State = Cookies.get('strains:search:step1');

        if (step1State) {
            step1State = JSON.parse(step1State);

            if (step1State.sativa) {
                $('input[name="sativa"]').prop('checked', 'checked');
                this.checkedTypes.push('sativa');
            }

            if (step1State.hybrid) {
                $('input[name="hybrid"]').prop('checked', 'checked');
                this.checkedTypes.push('hybrid');
            }

            if (step1State.indica) {
                $('input[name="indica"]').prop('checked', 'checked');
                this.checkedTypes.push('indica');
            }

            this.toggleSubmitButtonState();
        }

    },

    clickStep1Submit: function clickStep1Submit() {
        var that = this;
        this.ui.$btnSubmit.on('click', function (e) {
            e.preventDefault();
            var data = {
                step: 1,
                sativa: $('input[name="sativa"]').is(":checked"),
                hybrid: $('input[name="hybrid"]').is(":checked"),
                indica: $('input[name="indica"]').is(":checked")
            };

            Cookies.set('strains:search:step1', data);
            that.sendDataToWizard(data, that.successURL);
        });
    },

    clickStep1Skip: function clickStep1Skip() {
        var that = this;
        this.ui.$btnSkip.on('click', function (e) {
            e.preventDefault();
            that.sendDataToWizard({step: 1, skipped: true}, that.successURL);
        });
    },

    clickTypeInfo: function clickTypeInfo() {
        this.ui.$typeInfo.on('click', function (e) {
            e.preventDefault();
            W.common.Dialog($('.' + $(this).parent().find('.type').attr('id') + '-dialog'));
        });
    },

    clickCheckbox: function clickCheckbox() {
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

            that.toggleSubmitButtonState();
        });
    },

    toggleSubmitButtonState: function toggleSubmitButtonState() {
        if (this.checkedTypes.length > 0) {
            this.ui.$btnSubmit.removeAttr('disabled');
        } else {
            this.ui.$btnSubmit.attr('disabled', 'disabled');
        }
    }
});
