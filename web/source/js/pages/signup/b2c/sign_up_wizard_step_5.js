'use strict';

W.ns('W.pages.b2c');

W.pages.b2c.SignUpWizardStep5 = W.common.WizardStep.extend({

    init: function init(options) {
        this._super({
            step: 5,
            model: options && options.model,
            submit_el: '.btn-b2c-step-5',
            template_el: '#b2c-wizard-5'
        });
    },

    initEventHandlers: function initEventHandlers() {
        this._super();
        $('.check').on('click', function (e) {
            $('.error-message').text('');
        });
    },

    renderHTML: function () {
        var stepData = this.model.get(this.step);
        return this.$template({is_age_verified: stepData && stepData.is_age_verified});
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
