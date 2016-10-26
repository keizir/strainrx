'use strict';

W.ns('W.pages.b2b');

W.pages.b2b.SignUpWizardStep7 = W.common.WizardStep.extend({

    init: function init(options) {
        this._super({
            step: 7,
            model: options && options.model,
            submit_el: '.btn-b2b-step-7',
            template_el: '#b2b-wizard-7'
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
        $.publish('show_step', {step: 8});
    }

});