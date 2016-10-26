'use strict';

W.ns('W.pages.b2b');

W.pages.b2b.SignUpWizardStep2 = W.common.WizardStep.extend({

    init: function init(options) {
        this._super({
            step: 2,
            model: options && options.model,
            submit_el: '.btn-b2b-step-2',
            template_el: '#b2b-wizard-2'
        });
    },

    renderHTML: function () {
        var stepData = this.model.get(this.step);
        return this.$template({user_email: stepData && stepData.user_email});
    },

    validate: function validate() {
        var userEmail = $('input[name="user_email"]').val();

        if (!userEmail || userEmail.trim().length === 0) {
            $('.error-message').text('Email address is required');
            return false;
        }

        return true;
    },

    submit: function submit() {
        var data = {
            user_email: $('input[name="user_email"]').val().trim()
        };

        $.publish('update_step_data', {step: this.step, data: data});
        $.publish('show_step', {step: 3});
    }

});