'use strict';

W.ns('W.pages.b2b');

W.pages.b2b.SignUpWizardStep4 = W.common.WizardStep.extend({

    init: function init(options) {
        this._super({
            step: 4,
            model: options && options.model,
            submit_el: '.btn-b2b-step-4',
            template_el: '#b2b-wizard-4'
        });
    },

    renderHTML: function () {
        return this.$template({});
    },

    validate: function validate() {
        return true;
    },

    submit: function submit() {
        var data = {};
        $.publish('update_step_data', {step: this.step, data: data});
        $.publish('show_step', {step: 5});
    }

});