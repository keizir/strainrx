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

    initEventHandlers: function initEventHandlers() {
        this._super();
        $('.check').on('click', function () {
            $('.error-message').text('');
        });
    },

    renderHTML: function () {
        var stepData = this.model.get(this.step);
        return this.$template({certified_legal_compliance: stepData && stepData.certified_legal_compliance});
    },

    validate: function validate() {
        var isCertified = $('input[name="cert"]').is(":checked");
        if (!isCertified) {
            $('.error-message').text('Certification is required');
            return false;
        }

        return true;
    },

    submit: function submit() {
        var data = {certified_legal_compliance: $('input[name="cert"]').is(":checked")};
        $.publish('update_step_data', {step: this.step, data: data});
        $.publish('show_step', {step: 9});
    }

});