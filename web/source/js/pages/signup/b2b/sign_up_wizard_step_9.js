'use strict';

W.ns('W.pages.b2b');

W.pages.b2b.SignUpWizardStep9 = W.common.WizardStep.extend({

    init: function init(options) {
        this._super({
            step: 9,
            model: options && options.model,
            submit_el: '.btn-b2b-step-9',
            template_el: '#b2b-wizard-9'
        });
    },

    initEventHandlers: function initEventHandlers() {
        this._super();
        $('.check').on('click', function () {
            $('.error-message').text('');
        });

        $('.terms-link').on('click', function (e) {
            e.preventDefault();
            W.common.Dialog($('.terms-dialog'));
        });

        $('.policy-link').on('click', function (e) {
            e.preventDefault();
            W.common.Dialog($('.privacy-dialog'));
        });
    },

    renderHTML: function () {
        return this.$template({});
    },

    validate: function validate() {
        var isTermsChecked = $('input[name="terms"]').is(':checked');
        if (!isTermsChecked) {
            $('.error-message').text('Agreement is required');
            return false;
        }

        return true;
    },

    submit: function submit() {
        var data = {terms: $('input[name="terms"]').is(":checked")};
        $.publish('update_step_data', {step: this.step, data: data});
        $.publish('submit_form', this.model.getData());
    }

});