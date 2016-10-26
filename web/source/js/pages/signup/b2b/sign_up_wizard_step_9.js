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

    renderHTML: function () {
        return this.$template({});
    },

    validate: function validate() {
        return true;
    },

    submit: function submit() {
        $.publish('submit_form');
    }

});