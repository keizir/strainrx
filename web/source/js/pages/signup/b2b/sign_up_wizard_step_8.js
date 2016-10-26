'use strict';

W.ns('W.pages.b2b');

W.pages.b2b.SignUpWizardStep8 = W.common.WizardStep.extend({

    init: function init(options) {
        this._super({
            step: 8,
            model: options && options.model,
            submit_el: '.btn-b2b-step-8',
            template_el: '#b2b-wizard-8'
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
        $.publish('show_step', {step: 9});
    }

});